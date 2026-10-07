/*
 * This file is part of HayBox
 * Copyright (C) 2024 Jonathan Haylett
 *
 * HayBox is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License version 3 as
 * published by the Free Software Foundation.
 *
 * This software is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this software. If not, see <http://www.gnu.org/licenses/>.
 */

#include "core/Persistence.hpp"

#include "stdlib.hpp"

#include <CRC32.h>
#include <LittleFS.h>
#include <pb_arduino.h>
#include <pb_decode.h>
#include <pb_encode.h>

#include <cstring>

namespace {

struct ConfigFileReader {
    File *file;
    bool io_failed = false;
};

bool read_config_file(pb_istream_t *stream, pb_byte_t *buffer, size_t count) {
    ConfigFileReader &reader = *static_cast<ConfigFileReader *>(stream->state);
    // Nanopb may request a skipped field with a null buffer. Keep that read
    // bounded, and distinguish short/error I/O from a complete malformed payload.
    uint8_t skipped[32];
    while (count != 0) {
        const size_t chunk = buffer == nullptr && count > sizeof(skipped)
            ? sizeof(skipped) : count;
        uint8_t *destination = buffer != nullptr ? buffer : skipped;
        const int read = reader.file->read(destination, chunk);
        if (read < 0 || static_cast<size_t>(read) != chunk) {
            reader.io_failed = true;
            return false;
        }
        count -= chunk;
        if (buffer != nullptr) buffer += chunk;
    }
    return true;
}

}  // namespace

Persistence::Persistence() {
    _configuration_ok = LittleFS.setConfig(LittleFSConfig(false));
    if (_configuration_ok) {
        _mounted = LittleFS.begin();
    }
}

Persistence::~Persistence() {
    if (_mounted) {
        LittleFS.end();
    }
}

bool Persistence::IsAvailable() const {
    return _configuration_ok && _mounted;
}

bool Persistence::SetValidator(ConfigSemanticValidator validator) {
    if (validator == nullptr) {
        return false;
    }
    if (_validator != nullptr) {
        return _validator == validator;
    }
    _validator = validator;
    return true;
}

bool Persistence::ValidateConfig(const Config &config, ConfigValidationError &error) const {
    error = ConfigValidationError{};
    if (_validator == nullptr) {
        static const char message[] = "Config validator is not installed";
        std::memcpy(error.message, message, sizeof(message));
        error.length = sizeof(message);
        return false;
    }
    // Every adapter receives an already bounded object. The generic callback
    // retains the existing binding and reference rules; 022 can add its adapter.
    if (!validate_config_extents(config)) {
        static const char message[] = "Config contains an invalid button binding";
        std::memcpy(error.message, message, sizeof(message));
        error.length = sizeof(message);
        return false;
    }
    return _validator(config, error);
}

bool Persistence::SaveConfig(Config &config) {
    if (!IsAvailable()) {
        return false;
    }
    // Make sure config encodes correctly.
    size_t encoded_size;
    if (!pb_get_encoded_size(&encoded_size, Config_fields, &config)) {
        return false;
    }

    // Open file to store config data in.
    File config_file = LittleFS.open(config_filename, "w+");
    if (!config_file) {
        return false;
    }

    // Write empty header to start with.
    ConfigHeader header = { .config_size = 0, .config_crc = 0 };
    config_file.write((uint8_t *)&header, sizeof(ConfigHeader));

    // Encode Protobuf data directly into file body.
    pb_ostream_t ostream = as_pb_ostream(config_file);
    if (!pb_encode(&ostream, Config_fields, &config)) {
        config_file.close();
        return false;
    }

    // Calculate checksum.
    config_file.seek(config_offset);
    CRC32 crc;
    int value;
    while ((value = config_file.read()) != -1) {
        crc.update((uint8_t)value);
    }

    // Update header.
    header.config_size = ostream.bytes_written;
    header.config_crc = crc.finalize();
    config_file.seek(0);
    config_file.write((uint8_t *)&header, sizeof(ConfigHeader));

    // Persist changes.
    config_file.close();

    return true;
}

bool Persistence::LoadConfig(Config &config) {
    return LoadConfigChecked(config) == LoadResult::Loaded;
}

Persistence::LoadResult Persistence::LoadConfigChecked(Config &config) {
    if (!IsAvailable() || _validator == nullptr) {
        return LoadResult::StorageFailure;
    }

    // Config is too large for the core stack. This boot-owned candidate never
    // becomes active and is reset for every attempt, including partial decodes.
    static Config candidate;
    candidate = Config_init_default;

    File config_file = LittleFS.open(config_filename, "r");
    if (!config_file) {
        // The selected Boolean FS API cannot distinguish absence from I/O failure.
        // Absent remains reserved for positively proved absence; it is not inferred.
        return LoadResult::StorageFailure;
    }

    LoadResult failure = LoadResult::Rejected;
    if (!CheckSavedConfig(config_file, &failure)) {
        config_file.close();
        return failure;
    }
    const size_t file_size = config_file.size();
    if (file_size < config_offset || !config_file.seek(config_offset)) {
        config_file.close();
        return LoadResult::StorageFailure;
    }

    ConfigFileReader reader{ &config_file };
    pb_istream_t istream{};
    istream.callback = read_config_file;
    istream.state = &reader;
    istream.bytes_left = file_size - config_offset;
    if (!pb_decode(&istream, Config_fields, &candidate)) {
        config_file.close();
        return reader.io_failed ? LoadResult::StorageFailure : LoadResult::Rejected;
    }
    if (istream.bytes_left != 0 || config_file.position() != file_size ||
        config_file.size() != file_size) {
        config_file.close();
        return LoadResult::StorageFailure;
    }

    ConfigValidationError error;
    if (!ValidateConfig(candidate, error)) {
        config_file.close();
        return LoadResult::Rejected;
    }

    config_file.close();
    config = candidate;
    return LoadResult::Loaded;
}

bool Persistence::CheckSavedConfig() {
    if (!IsAvailable()) {
        return false;
    }
    // Open file to load config data from.
    File config_file = LittleFS.open(config_filename, "r");
    if (!config_file) {
        return false;
    }

    bool is_valid = CheckSavedConfig(config_file);
    config_file.close();
    return is_valid;
}

size_t Persistence::LoadConfigRaw(Print &out, bool validate) {
    if (!IsAvailable()) {
        return false;
    }
    // Open file to load config data from.
    File config_file = LittleFS.open(config_filename, "r");
    if (!config_file) {
        return false;
    }

    // Optionally perform validation.
    if (validate && !CheckSavedConfig(config_file)) {
        config_file.close();
        return false;
    }

    // Seek to start of Protobuf data.
    if (!config_file.seek(config_offset)) {
        config_file.close();
        return false;
    }

    // Write raw Protobuf encoded data to output stream.
    int value;
    while ((value = config_file.read()) != -1) {
        out.write((uint8_t)value);
    }

    config_file.close();
    return true;
}

bool Persistence::CheckSavedConfig(File &config_file, LoadResult *failure) {
    if (failure != nullptr) {
        *failure = LoadResult::Rejected;
    }
    const size_t file_size = config_file.size();
    if (file_size < config_offset) {
        return false;
    }
    if (!config_file.seek(0)) {
        if (failure != nullptr) *failure = LoadResult::StorageFailure;
        return false;
    }

    ConfigHeader header;
    const int bytes_read = config_file.read((uint8_t *)&header, sizeof(ConfigHeader));
    if (bytes_read != static_cast<int>(sizeof(ConfigHeader))) {
        if (failure != nullptr) *failure = LoadResult::StorageFailure;
        return false;
    }
    const size_t config_size = file_size - config_offset;
    if (config_size != header.config_size) {
        return false;
    }

    CRC32 crc;
    for (size_t i = 0; i < config_size; ++i) {
        const int value = config_file.read();
        if (value < 0) {
            if (failure != nullptr) *failure = LoadResult::StorageFailure;
            return false;
        }
        crc.update((uint8_t)value);
    }
    if (config_file.position() != file_size || config_file.size() != file_size) {
        if (failure != nullptr) *failure = LoadResult::StorageFailure;
        return false;
    }
    return crc.finalize() == header.config_crc;
}

Persistence persistence;