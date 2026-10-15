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
#include <cstdio>

namespace {
// Config is too large for the core stack. Whole-Config SET and reference SET
// are synchronous core0 handlers and share one unpublished candidate. No live
// runtime selection or ProfileStore payload aliases this scratch.
Config &ConfigWriteCandidate() {
    static Config candidate;
    return candidate;
}

bool ReferencesProfile(const Config &config, uint32_t id) {
    for (size_t i = 0; i < config.game_mode_configs_count; ++i) {
        const GameModeConfig &mode = config.game_mode_configs[i];
        if (mode.mode_id == MODE_ULTIMATE && mode.ultimate_profile_id == id) return true;
    }
    return false;
}

// TinyUSB's ordinary write can wait forever while a connected host stops
// draining TX. Only hand it bytes already admitted by its FIFO. The single
// core0 producer owns this response; USB IRQs can only increase free space.
class ProfilePacketWriter final : public Print {
  public:
    explicit ProfilePacketWriter(Stream &stream) : _stream(stream), _start(millis()) {}
    size_t write(uint8_t byte) override { return write(&byte, 1); }
    size_t write(const uint8_t *bytes, size_t length) override {
        size_t sent = 0;
        while (sent < length && static_cast<uint32_t>(millis() - _start) < 2000u) {
            const int available = _stream.availableForWrite();
            if (available > 0) {
                const size_t count = length - sent < static_cast<size_t>(available)
                    ? length - sent : static_cast<size_t>(available);
                const size_t written = _stream.write(bytes + sent, count);
                sent += written;
                if (written != 0) continue;
            }
            delay(1);
        }
        return sent;
    }
  private:
    Stream &_stream;
    uint32_t _start;
};
}

bool ConfiguratorBackend::WriteProfilePacket(Command command, const uint8_t *bytes, size_t length) {
    ProfilePacketWriter writer(_base_stream);
    // A failed packet may have left a prefix on the wire. Delimit it before
    // starting a fresh COBS encoder; do not retain failed encoder state.
    if (_profile_tx_needs_sync && writer.write(uint8_t{0}) != 1) return false;
    packetio::COBSPrint packet(writer);
    const bool ok = packet.write(static_cast<uint8_t>(command)) == 1 &&
        packet.write(bytes, length) == length && packet.end();
    _profile_tx_needs_sync = !ok;
    return ok;
}

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
    if (_profile_tx_needs_sync && command != CMD_PROFILE_STORE) {
        // Legacy command responses share the physical stream. They must also
        // terminate a partial ProfileStore frame before using their encoder.
        ProfilePacketWriter writer(_base_stream);
        if (writer.write(uint8_t{0}) != 1) {
            SkipToNextPacket();
            return;
        }
        _profile_tx_needs_sync = false;
    }
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
    Config &candidate = ConfigWriteCandidate();

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
        return WriteProfilePacket(CMD_ERROR, (const uint8_t *)timeout, sizeof(timeout) - 1);
    }
    if (length == sizeof(frame)) return WriteProfilePacket(CMD_ERROR, (const uint8_t *)"Profile store frame too large", 29);
    request = ProfileStoreRequest_init_default;
    pb_istream_t input = pb_istream_from_buffer(frame, length);
    if (!pb_decode(&input, ProfileStoreRequest_fields, &request) || request.protocol_version != 1) {
        return WriteProfilePacket(CMD_ERROR, (const uint8_t *)"Invalid profile store request", 29);
    }
    response = ProfileStoreResponse_init_default;
    response.protocol_version = 1;
    response.request_token = request.request_token;
    response.store_generation = profile_store.Generation();
    response.config_generation = persistence.ConfigGeneration(_config);
    response.status = PROFILE_STORE_UNSUPPORTED;
    // Diagnostics describe this request only. In particular, a persistence
    // error outside WriteProfile must never inherit a prior record stage.
    profile_store.ResetDiagnostic();
    if (request.operation == PROFILE_STORE_STATUS) {
        response.status = profile_store.IsReady() && !profile_store.IsReadOnlyRecovery()
            ? PROFILE_STORE_OK : PROFILE_STORE_IO_FAILURE;
        if (profile_store.IsReadOnlyRecovery()) {
            strlcpy(response.diagnostic, "directory.recovery", sizeof(response.diagnostic));
        }
    } else if (request.operation == PROFILE_STORE_LIST) {
        const size_t cursor = request.page_cursor;
        const size_t count = request.page_size == 0 ? 8 : request.page_size;
        if (!profile_store.IsReady()) response.status = PROFILE_STORE_IO_FAILURE;
        else if (count > 8 || cursor > profile_store.Count()) response.status = PROFILE_STORE_INVALID;
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
            // A reference save is reboot-bound. Protect both the currently
            // active selection and the durable selection for the next boot.
            Config &durable = ConfigWriteCandidate();
            if (persistence.LoadConfigChecked(durable) != Persistence::LoadResult::Loaded) {
                result.status = ProfileStore::Status::IoFailure;
            } else {
                const uint32_t referenced = ReferencesProfile(_config, request.profile_id) ||
                    ReferencesProfile(durable, request.profile_id) ? request.profile_id : 0;
                result = profile_store.Delete(request.profile_id,
                    static_cast<uint32_t>(request.expected_store_generation), referenced, token, digest);
            }
        } else if (request.operation == PROFILE_STORE_SET_MODE_REFERENCE) {
            Config &candidate = ConfigWriteCandidate();
            if (!profile_store.IsReady() || profile_store.IsReadOnlyRecovery()) {
                result.status = ProfileStore::Status::IoFailure;
            } else if (request.expected_config_generation != persistence.ConfigGeneration(_config)) {
                result.status = ProfileStore::Status::Conflict;
            } else if (persistence.LoadConfigChecked(candidate) != Persistence::LoadResult::Loaded) {
                result.status = ProfileStore::Status::IoFailure;
            } else if (request.expected_config_generation != persistence.ConfigGeneration(candidate) ||
                candidate.ultimate_profile_store_format != ProfileStore::kCompactConfigFormat ||
                request.mode_config_index >= candidate.game_mode_configs_count) {
                // The checked load establishes which durable generation this
                // candidate represents; the initial cached fence is not enough.
                result.status = ProfileStore::Status::Conflict;
            } else if (candidate.game_mode_configs[request.mode_config_index].mode_id != MODE_ULTIMATE) {
                result.status = ProfileStore::Status::Invalid;
            } else {
                // Static, synchronous core0 scratch preserves CREATE's small
                // frame even though this unrelated operation reads a profile.
                static UltimateProfile selected;
                if (request.profile_id != 0 && profile_store.Read(request.profile_id, selected) != ProfileStore::Status::Ok) {
                    result.status = ProfileStore::Status::NotFound;
                } else {
                    GameModeConfig &mode = candidate.game_mode_configs[request.mode_config_index];
                    mode.ultimate_profile_id = request.profile_id;
                    mode.ultimate_profile_config = 0;
                    ConfigValidationError validation_error;
                    if (!persistence.ValidateConfig(candidate, validation_error)) {
                        result.status = ProfileStore::Status::Invalid;
                    } else {
                        const Persistence::SaveResult saved = persistence.SaveConfigIfGenerationMatches(
                            candidate, request.expected_config_generation);
                        if (saved == Persistence::SaveResult::Conflict) result.status = ProfileStore::Status::Conflict;
                        else if (saved != Persistence::SaveResult::Saved) result.status = ProfileStore::Status::IoFailure;
                        else result = {ProfileStore::Status::Ok, request.profile_id, 0, profile_store.Generation()};
                    }
                    // Never publish candidate into _config here. Runtime and
                    // transient session selectors stay unchanged until reboot.
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
        if (response.status == PROFILE_STORE_IO_FAILURE || response.status == PROFILE_STORE_COMMIT_UNKNOWN) {
            strlcpy(response.diagnostic, profile_store.LastDiagnostic(), sizeof(response.diagnostic));
        }
    }
    // The request is decoded into owned static fields before reusing frame.
    // Encoding and transport are separate bounded stages, with no FS frames
    // alive during either stage.
    pb_ostream_t output = pb_ostream_from_buffer(frame, sizeof(frame));
    if (!pb_encode(&output, ProfileStoreResponse_fields, &response)) {
        return false;
    }
    const bool sent = WriteProfilePacket(CMD_PROFILE_STORE, frame, output.bytes_written);
    return sent;
}

bool ConfiguratorBackend::HandleUnknownCommand(Command command) {
    char errmsg[50];
    size_t errmsg_len =
        snprintf(errmsg, sizeof(errmsg), "Unknown command ID: %d", (uint8_t)command);
    return WritePacket(CMD_ERROR, (uint8_t *)errmsg, errmsg_len);
}
