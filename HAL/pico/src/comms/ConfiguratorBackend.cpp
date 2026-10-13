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

#include "comms/ConfiguratorBackend.hpp"

#include "core/InputSource.hpp"
#include "core/Persistence.hpp"
#include "core/ProfileStore.hpp"
#include "core/config_validation.hpp"
#include "reboot.hpp"
#include "arduino/Adafruit_USBD_Device.h"

#include <pb_arduino.h>
#include <pb_decode.h>
#include <pb_encode.h>

ConfiguratorBackend::ConfiguratorBackend(
    InputState &inputs,
    InputSource **input_sources,
    size_t input_source_count,
    Config &config,
    Stream &stream
)
    : CommunicationBackend(inputs, input_sources, input_source_count),
      _in(stream),
      _out(stream),
      _base_stream(stream),
      _config(config) {

    TinyUSBDevice.setID(0x2E8A, 0x1092);
}

CommunicationBackendId ConfiguratorBackend::BackendId() {
    return COMMS_BACKEND_CONFIGURATOR;
}

void ConfiguratorBackend::SendReport() {
    int data = ReadByte();
    if (data < 0) {
        if (data == _in.EOP) {
            SkipToNextPacket();
        }
        return;
    }

    Command command = (Command)data;
    switch (command) {
        case CMD_GET_DEVICE_INFO:
            HandleGetDeviceInfo();
            break;
        case CMD_GET_CONFIG:
            HandleGetConfig();
            break;
        case CMD_SET_CONFIG:
            HandleSetConfig();
            break;
        case CMD_PROFILE_STORE:
            // HandleProfileStore consumes the complete framed request through
            // ReadPacket(), which advances the PacketIO reader after EOP (or
            // starts its documented delimiter-based resynchronization).
            // Returning here avoids advancing a second time and dropping the
            // following valid request. Other configurator commands retain
            // their existing packet-ownership lifecycle below.
            HandleProfileStore();
            return;
        case CMD_REBOOT_FIRMWARE:
            reboot_firmware();
            break;
        case CMD_REBOOT_BOOTLOADER:
            reboot_bootloader();
            break;
        case CMD_UNSPECIFIED:
        default:
            HandleUnknownCommand(command);
            break;
    }

    SkipToNextPacket();
}

size_t ConfiguratorBackend::ReadPacket(uint8_t *buffer, size_t max_len) {
    size_t bytes_read = 0;
    _packet_timed_out = false;
    uint32_t last_progress = millis();
    while (true) {
        if (!_in.available()) {
            if (static_cast<uint32_t>(millis() - last_progress) >= 5000u) {
                _packet_timed_out = true;
                _in.next();
                return 0;
            }
            delay(1);
            continue;
        }
        int result = _in.read();
        if (result == _in.EOF) {
            continue;
        }
        last_progress = millis();
        if (result == _in.EOP) {
            break;
        }
        buffer[bytes_read++] = result;
        if (bytes_read >= max_len) {
            _in.next();
            return bytes_read;
        }
    }
    _in.next();

    return bytes_read;
}

int ConfiguratorBackend::ReadByte() {
    if (!_base_stream.available()) {
        return -1;
    }
    return _in.read();
}

void ConfiguratorBackend::SkipToNextPacket() {
    _in.next();
}

bool ConfiguratorBackend::WritePacket(Command command_id, uint8_t *buffer, size_t len) {
    _out.write((uint8_t)command_id);
    for (size_t i = 0; i < len; i++) {
        _out.write(buffer[i]);
    }
    return _out.end();
}

bool ConfiguratorBackend::HandleGetDeviceInfo() {
    static const DeviceInfo device_info = {
        FIRMWARE_NAME,
        FIRMWARE_VERSION,
        DEVICE_NAME,
    };

    // Ensure device info encodes correctly.
    size_t size;
    if (!pb_get_encoded_size(&size, DeviceInfo_fields, &device_info)) {
        char errmsg[] = "Failed to encode device info";
        WritePacket(CMD_ERROR, (uint8_t *)errmsg, sizeof(errmsg));
        return false;
    }

    _out.write(CMD_SET_DEVICE_INFO);
    pb_ostream_t ostream = as_pb_ostream(_out);
    pb_encode(&ostream, DeviceInfo_fields, &device_info);
    return _out.end();
}

bool ConfiguratorBackend::HandleGetConfig() {
    if (!persistence.CheckSavedConfig()) {
        char errmsg[] = "Config file is invalid";
        WritePacket(CMD_ERROR, (uint8_t *)errmsg, sizeof(errmsg));
        return false;
    }

    // Write raw config data to output stream.
    _out.write(CMD_SET_CONFIG);
    persistence.LoadConfigRaw(_out, false);
    return _out.end();
}

bool ConfiguratorBackend::HandleSetConfig() {
    // Keep the accepted live configuration untouched until the complete
    // decode, validation, and persistence sequence succeeds.  The candidate
    // is static because Config contains the fixed-size embedded arrays used
    // by the selected input modes and is too large for the call stack.
    static Config candidate;

    // Reset config defaults first, so config is completely replaced rather than merged.
    candidate = Config_init_default;

    pb_istream_t istream = as_pb_istream(_in);
    if (!pb_decode(&istream, Config_fields, &candidate)) {
        char errmsg[100];
        size_t errmsg_len =
            snprintf(errmsg, sizeof(errmsg), "Failed to decode config: %s", istream.errmsg);
        WritePacket(CMD_ERROR, (uint8_t *)errmsg, errmsg_len);

        return false;
    }

    // Whole-Config SET is the legacy protocol.  Once a compact profile-store
    // Config is active, accepting an older client's decoded default marker
    // would silently sever stable per-mode references.  Store mutations must
    // use the negotiated profile-store protocol instead.
    if (_config.ultimate_profile_store_format == ProfileStore::kCompactConfigFormat &&
        candidate.ultimate_profile_store_format != ProfileStore::kCompactConfigFormat) {
        static const char errmsg[] = "Profile store requires negotiated protocol";
        WritePacket(CMD_ERROR, (uint8_t *)errmsg, sizeof(errmsg));
        return false;
    }

    ConfigValidationError validation_error;
    if (!persistence.ValidateConfig(candidate, validation_error)) {
        WritePacket(CMD_ERROR, (uint8_t *)validation_error.message, validation_error.length);
        return false;
    }

    if (!persistence.SaveConfig(candidate)) {
        char errmsg[] = "Failed to save config to memory";
        WritePacket(CMD_ERROR, (uint8_t *)errmsg, sizeof(errmsg));
        return false;
    }

    _config = candidate;

    WritePacket(CMD_SUCCESS, nullptr, 0);
    return true;
}

bool ConfiguratorBackend::HandleProfileStore() {
    static constexpr size_t kFrameLimit = 8192;
    static ProfileStoreRequest request;
    static ProfileStoreResponse response;
    static uint8_t frame[kFrameLimit];
    const size_t length = ReadPacket(frame, sizeof(frame));
    if (_packet_timed_out) {
        static constexpr char timeout[] = "Profile store frame timeout";
        return WritePacket(CMD_ERROR, (uint8_t *)timeout, sizeof(timeout) - 1);
    }
    if (length == sizeof(frame)) return WritePacket(CMD_ERROR, (uint8_t *)"Profile store frame too large", 29);
    request = ProfileStoreRequest_init_default;
    pb_istream_t input = pb_istream_from_buffer(frame, length);
    if (!pb_decode(&input, ProfileStoreRequest_fields, &request) || request.protocol_version != 1) {
        return WritePacket(CMD_ERROR, (uint8_t *)"Invalid profile store request", 29);
    }
    response = ProfileStoreResponse_init_default;
    response.protocol_version = 1;
    response.request_token = request.request_token;
    response.store_generation = profile_store.Generation();
    response.config_generation = persistence.ConfigGeneration(_config);
    response.status = PROFILE_STORE_UNSUPPORTED;
    if (request.operation == PROFILE_STORE_STATUS) {
        response.status = profile_store.IsReady() ? PROFILE_STORE_OK : PROFILE_STORE_IO_FAILURE;
    } else if (request.operation == PROFILE_STORE_LIST) {
        const size_t cursor = request.page_cursor;
        const size_t count = request.page_size == 0 ? 8 : request.page_size;
        if (count > 8 || cursor > profile_store.Count()) response.status = PROFILE_STORE_INVALID;
        else {
            const size_t end = cursor + count < profile_store.Count() ? cursor + count : profile_store.Count();
            response.entries_count = 0;
            for (size_t i = cursor; i < end; ++i) {
                const ProfileStore::Entry *entry = profile_store.EntryAt(i);
                ProfileStoreEntry &out = response.entries[response.entries_count++];
                out.profile_id = entry->id; out.revision = entry->revision; out.display_rank = entry->rank;
                out.payload_version = entry->payload_version;
                strlcpy(out.name, entry->name, sizeof(out.name));
            }
            response.next_page_cursor = end < profile_store.Count() ? end : 0;
            response.status = PROFILE_STORE_OK;
        }
    } else if (request.expected_store_generation != profile_store.Generation()) {
        response.status = PROFILE_STORE_CONFLICT;
    } else {
        const uint32_t token = static_cast<uint32_t>(request.request_token);
        const uint32_t digest = static_cast<uint32_t>(request.request_token >> 32);
        ProfileStore::TransactionResult result;
        if (request.operation == PROFILE_STORE_READ) {
            uint32_t revision = 0;
            const ProfileStore::Status status = profile_store.Read(request.profile_id, response.profile, &revision);
            response.has_profile = status == ProfileStore::Status::Ok;
            result = {status, request.profile_id, revision, profile_store.Generation()};
        } else if (request.operation == PROFILE_STORE_CREATE) {
            result = profile_store.Create(request.profile, request.name, request.display_rank, token, digest);
        } else if (request.operation == PROFILE_STORE_UPDATE) {
            result = profile_store.Update(request.profile_id, request.profile,
                static_cast<uint32_t>(request.expected_profile_revision), token, digest);
        } else if (request.operation == PROFILE_STORE_DUPLICATE) {
            result = profile_store.Duplicate(request.profile_id,
                static_cast<uint32_t>(request.expected_profile_revision), request.name,
                request.display_rank, token, digest);
        } else if (request.operation == PROFILE_STORE_RENAME) {
            result = profile_store.Rename(request.profile_id, request.name,
                static_cast<uint32_t>(request.expected_store_generation), token, digest);
        } else if (request.operation == PROFILE_STORE_REORDER) {
            result = profile_store.Reorder(request.profile_id, request.display_rank,
                static_cast<uint32_t>(request.expected_store_generation), token, digest);
        } else if (request.operation == PROFILE_STORE_DELETE) {
            uint32_t referenced = 0;
            for (size_t i = 0; i < _config.game_mode_configs_count; ++i) {
                const GameModeConfig &mode = _config.game_mode_configs[i];
                if (mode.mode_id == MODE_ULTIMATE && mode.ultimate_profile_id == request.profile_id) {
                    referenced = request.profile_id; break;
                }
            }
            result = profile_store.Delete(request.profile_id,
                static_cast<uint32_t>(request.expected_store_generation), referenced, token, digest);
        } else if (request.operation == PROFILE_STORE_SET_MODE_REFERENCE) {
            if (_config.ultimate_profile_store_format != ProfileStore::kCompactConfigFormat ||
                request.expected_config_generation != persistence.ConfigGeneration(_config) ||
                request.mode_config_index >= _config.game_mode_configs_count) {
                result.status = ProfileStore::Status::Conflict;
            } else {
                const GameModeConfig &current = _config.game_mode_configs[request.mode_config_index];
                if (current.mode_id != MODE_ULTIMATE) {
                    result.status = ProfileStore::Status::Invalid;
                } else {
                    UltimateProfile selected = UltimateProfile_init_default;
                    if (request.profile_id != 0 && profile_store.Read(request.profile_id, selected) != ProfileStore::Status::Ok) {
                        result.status = ProfileStore::Status::NotFound;
                    } else {
                        // Do not publish a new runtime selection mid-report. The
                        // checked persistence primitive encodes this bounded
                        // temporary edit, then the in-RAM selection is restored;
                        // explicit reboot is the activation boundary.
                        GameModeConfig &mode = _config.game_mode_configs[request.mode_config_index];
                        const uint32_t old_profile_id = mode.ultimate_profile_id;
                        const uint32_t old_legacy_index = mode.ultimate_profile_config;
                        mode.ultimate_profile_id = request.profile_id;
                        mode.ultimate_profile_config = 0;
                        ConfigValidationError validation_error;
                        if (!persistence.ValidateConfig(_config, validation_error)) {
                            result.status = ProfileStore::Status::Invalid;
                        } else if (!persistence.SaveConfig(_config)) {
                            result.status = ProfileStore::Status::IoFailure;
                        } else {
                            result = {ProfileStore::Status::Ok, request.profile_id, 0, profile_store.Generation()};
                        }
                        mode.ultimate_profile_id = old_profile_id;
                        mode.ultimate_profile_config = old_legacy_index;
                    }
                }
            }
        } else if (request.operation == PROFILE_STORE_QUERY_TRANSACTION) {
            result = profile_store.QueryTransaction(token, digest);
        } else {
            response.status = PROFILE_STORE_UNSUPPORTED;
            result.status = ProfileStore::Status::Invalid;
        }
        response.profile_id = result.id;
        response.profile_revision = result.revision;
        response.store_generation = profile_store.Generation();
        response.config_generation = persistence.ConfigGeneration(_config);
        switch (result.status) {
            case ProfileStore::Status::Ok: response.status = PROFILE_STORE_OK; break;
            case ProfileStore::Status::NotFound: response.status = PROFILE_STORE_NOT_FOUND; break;
            case ProfileStore::Status::Referenced: response.status = PROFILE_STORE_REFERENCED; break;
            case ProfileStore::Status::Conflict: response.status = PROFILE_STORE_CONFLICT; break;
            case ProfileStore::Status::Full: response.status = PROFILE_STORE_FULL; break;
            case ProfileStore::Status::IoFailure: response.status = PROFILE_STORE_IO_FAILURE; break;
            case ProfileStore::Status::UnknownOutcome: response.status = PROFILE_STORE_COMMIT_UNKNOWN; break;
            default: response.status = PROFILE_STORE_INVALID; break;
        }
    }
    _out.write(CMD_PROFILE_STORE);
    pb_ostream_t output = as_pb_ostream(_out);
    if (!pb_encode(&output, ProfileStoreResponse_fields, &response)) return false;
    return _out.end();
}

bool ConfiguratorBackend::HandleUnknownCommand(Command command) {
    char errmsg[50];
    size_t errmsg_len =
        snprintf(errmsg, sizeof(errmsg), "Unknown command ID: %d", (uint8_t)command);
    return WritePacket(CMD_ERROR, (uint8_t *)errmsg, errmsg_len);
}
