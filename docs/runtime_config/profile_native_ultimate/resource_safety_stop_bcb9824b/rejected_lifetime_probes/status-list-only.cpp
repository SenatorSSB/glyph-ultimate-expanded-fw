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
#include <new>

#include "core/InputSource.hpp"
#include "core/Persistence.hpp"
#include "core/ProfileStore.hpp"
#include "core/ConfigWriteCandidate.hpp"
#include "core/ProfileStoreRequestIdentity.hpp"
#include "core/ResourceDiagnostics.hpp"
#include "core/ProfileStoreFaultControls.hpp"
#include "core/RuntimeIdentityWire.hpp"
#include "core/config_validation.hpp"
#include "reboot.hpp"
#include "arduino/Adafruit_USBD_Device.h"

#include <pb_arduino.h>
#include <pb_decode.h>
#include "modes/UltimateNativeProfile.hpp"
#include <pb_encode.h>
#include "core/ProfileStoreReadTrace.hpp"
#include <cstdio>
#include <cstring>

namespace {
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
    explicit ProfilePacketWriter(CoordinatedCdcStream &stream) : _stream(stream), _start(millis()) {}
    size_t write(uint8_t byte) override { return write(&byte, 1); }
    size_t write(const uint8_t *bytes, size_t length) override {
        size_t sent = 0;
        while (sent < length && static_cast<uint32_t>(millis() - _start) < 2000u) {
            const int available = _stream.availableForWrite();
            if (available > 0) {
                const size_t count = length - sent < static_cast<size_t>(available)
                    ? length - sent : static_cast<size_t>(available);
                const size_t written = _stream.writeAvailable(bytes + sent, count);
                sent += written;
                _accepted += written;
                _stream.serviceTx();
                if (written != 0) continue;
            }
            _stream.serviceTx();
            delay(1);
        }
        return sent;
    }
    size_t accepted() const { return _accepted; }
    bool finish() {
        while (static_cast<uint32_t>(millis() - _start) < 2000u) {
            _stream.serviceTx();
            if (_stream.txSubmitted()) return true;
            delay(1);
        }
        return false;
    }
  private:
    size_t _accepted = 0;
    CoordinatedCdcStream &_stream;
    uint32_t _start;
};
}

bool ConfiguratorBackend::WriteProfilePacket(Command command, const uint8_t *bytes, size_t length, size_t *accepted, bool *flushRequested) {
    ProfilePacketWriter writer(_base_stream);
    // A failed packet may have left a prefix on the wire. Delimit it before
    // starting a fresh COBS encoder; do not retain failed encoder state.
    if (_profile_tx_needs_sync && writer.write(uint8_t{0}) != 1) return false;
    packetio::COBSPrint packet(writer);
    const bool encoded = packet.write(static_cast<uint8_t>(command)) == 1 &&
        packet.write(bytes, length) == length && packet.end();
    if (accepted) *accepted = writer.accepted();
    if (flushRequested) *flushRequested = encoded;
    const bool ok = encoded && writer.finish();
    _profile_tx_needs_sync = !ok;
    return ok;
}

#if GLYPH_STRICT_HARDENING_CANDIDATE
// Small candidate-only frames are emitted before the suspected synchronous
// phases. The host journals these before waiting for the final response. No
// flash writes, watchdog, IRQ/core1 instrumentation, or stack-sized protobuf.
bool ConfiguratorBackend::TraceProfileStage(const ProfileStoreRequest &request, uint32_t stage, uint32_t value) {
    if (!kStrictHardeningCandidate || !request.liveness_trace) return true;
    uint8_t bytes[32]; size_t count = 0;
    auto varint = [&](uint64_t value) {
        do { bytes[count++] = uint8_t(value & 127u) | (value > 127u ? 128u : 0u); value >>= 7; } while(value);
    };
    varint(8); varint(request.protocol_version);
    varint(16); varint(request.request_token);
    varint(42u << 3); varint(stage);
    varint(43u << 3); varint(value);
    return WriteProfilePacket(CMD_PROFILE_STORE, bytes, count);
}

#endif

ConfiguratorBackend::ConfiguratorBackend(
    InputState &inputs,
    InputSource **input_sources,
    size_t input_source_count,
    Config &config,
    Stream &stream
)
    : CommunicationBackend(inputs, input_sources, input_source_count),
      _coordinated_stream(stream),
      _in(_coordinated_stream),
      _out(_coordinated_stream),
      _base_stream(_coordinated_stream),
      _config(config) {

    TinyUSBDevice.setID(0x2E8A, 0x1092);
}

CommunicationBackendId ConfiguratorBackend::BackendId() {
    return COMMS_BACKEND_CONFIGURATOR;
}

// Delimiter-writer scratch ends before command dispatch enters storage.
static __attribute__((noinline)) bool SendProfileDelimiter(CoordinatedCdcStream &stream) {
    ProfilePacketWriter writer(stream);
    return writer.write(uint8_t{0}) == 1;
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
        if (!SendProfileDelimiter(_base_stream)) {
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
        case CMD_RUNTIME_IDENTITY:
            HandleRuntimeIdentity();
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

bool ConfiguratorBackend::HandleRuntimeIdentity() {
    uint8_t request[runtime_identity::kRequestBytes + 1];
    const size_t length = ReadPacket(request, sizeof(request));
    uint64_t token = 0;
    if (_packet_timed_out || !runtime_identity::DecodeRequest(request, length, token)) return false;
    runtime_identity::Snapshot snapshot;
    snapshot.status = _recovery_service ? runtime_identity::Status::Recovery
                                        : runtime_identity::Status::Configurator;
    snapshot.backend = static_cast<uint8_t>(COMMS_BACKEND_CONFIGURATOR);
    uint8_t response[runtime_identity::kResponseBytes];
    runtime_identity::EncodeResponse(token, snapshot, response);
    return WriteProfilePacket(CMD_RUNTIME_IDENTITY, response, sizeof(response));
}

size_t ConfiguratorBackend::ReadPacket(uint8_t *buffer, size_t max_len) {
    size_t bytes_read = 0;
    _packet_timed_out = false;
    const uint32_t started = millis();
#if GLYPH_STRICT_HARDENING_CANDIDATE
    const uint32_t raw_start = _base_stream.RxConsumed();
    const uint32_t fetched_start = _base_stream.RxFetched();
    const uint32_t tasks_start = _base_stream.RxTaskPasses();
    _rx = {}; _rx.phase = 1;
    auto sample = [&]() {
        const uint32_t raw = _base_stream.RxConsumed() - raw_start;
        _rx.elapsed = millis() - started;
        if (raw != _rx.raw) _rx.last_progress = _rx.elapsed;
        _rx.raw = raw; _rx.decoded = bytes_read;
        _rx.fetched = _base_stream.RxFetched() - fetched_start;
        _rx.task_passes = _base_stream.RxTaskPasses() - tasks_start;
    };
    _rx.phase = 2;
#endif
    while (true) {
#if GLYPH_STRICT_HARDENING_CANDIDATE
        sample();
#endif
        if (static_cast<uint32_t>(millis() - started) >= 5000u) {
            _packet_timed_out = true;
#if GLYPH_STRICT_HARDENING_CANDIDATE
            _rx.phase = 10; _rx.flags |= 2;
#endif
            _in.next();
            return 0;
        }
        if (!_in.available()) {
            delay(1);
            continue;
        }
        int result = _in.read();
        if (result == _in.EOF) continue;
        if (result == _in.EOP) {
#if GLYPH_STRICT_HARDENING_CANDIDATE
            sample(); _rx.phase = 4; _rx.flags |= 1;
#endif
            break;
        }
        buffer[bytes_read++] = result;
        if (bytes_read >= max_len) {
#if GLYPH_STRICT_HARDENING_CANDIDATE
            sample(); _rx.phase = 11; _rx.flags |= 4;
#endif
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
    if (!_recovery_storage_available || _recovery_config_invalid) {
        static const char error[] = "Config unavailable in recovery";
        return WritePacket(CMD_ERROR, (uint8_t *)error, sizeof(error));
    }
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
    if (_recovery_service || _recovery_config_invalid || !_recovery_storage_available ||
        _reference_unknown || persistence.IsMutationFenced() || profile_store.IsTransactionUncertain() ||
        profile_store.MigrationPending()) {
        static const char error[] = "Recovery state is read-only";
        return WritePacket(CMD_ERROR, (uint8_t *)error, sizeof(error));
    }
    // Keep the accepted live configuration untouched until the complete
    // decode, validation, and persistence sequence succeeds.  The candidate
    // is static because Config contains the fixed-size embedded arrays used
    // by the selected input modes and is too large for the call stack.
    Config &candidate = ConfigWriteCandidate();
    uint64_t receipt_token = 0;
    uint8_t receipt_digest[32] = {}, migration_receipt[32] = {};
    uint32_t receipt_id = 0, receipt_generation = 0, receipt_mode = 0, root_format = 0;
    if (_config.ultimate_profile_store_format == ProfileStore::kCompactConfigFormat) {
        if (persistence.LoadConfigChecked(candidate) != Persistence::LoadResult::Loaded) {
            static const char error[] = "Failed to load durable Config";
            return WritePacket(CMD_ERROR, (uint8_t *)error, sizeof(error));
        }
        receipt_token = candidate.profile_reference_token;
        std::memcpy(receipt_digest, candidate.profile_reference_digest, 32);
        receipt_id = candidate.profile_reference_result_id;
        receipt_generation = candidate.profile_reference_result_store_generation;
        receipt_mode = candidate.profile_reference_result_mode_index;
        root_format = candidate.ultimate_profile_root_format;
        std::memcpy(migration_receipt, candidate.ultimate_profile_migration_receipt, 32);
    }

    // Reset config defaults first, so config is completely replaced rather than merged.
    candidate = Config_init_default;

    ultimate_native::RejectEmbedded(candidate);
    pb_istream_t istream = as_pb_istream(_in);
    if (!pb_decode(&istream, Config_fields, &candidate)) {
        char errmsg[100];
        size_t errmsg_len =
            snprintf(errmsg, sizeof(errmsg), "Failed to decode config: %s", istream.errmsg);
        WritePacket(CMD_ERROR, (uint8_t *)errmsg, errmsg_len);

        return false;
    }

    ultimate_native::ClearEmbeddedCallbacks(candidate);

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

    candidate.ultimate_profile_root_format = root_format;
    candidate.profile_reference_token = receipt_token;
    std::memcpy(candidate.profile_reference_digest, receipt_digest, 32);
    candidate.profile_reference_result_id = receipt_id;
    candidate.profile_reference_result_store_generation = receipt_generation;
    candidate.profile_reference_result_mode_index = receipt_mode;
    std::memcpy(candidate.ultimate_profile_migration_receipt, migration_receipt, 32);
    ConfigValidationError validation_error;
    if (!persistence.ValidateConfig(candidate, validation_error)) {
        WritePacket(CMD_ERROR, (uint8_t *)validation_error.message, validation_error.length);
        return false;
    }

    // A whole-Config client cannot change the expected engine of a known
    // selected record. Missing native records remain loadable but unavailable.
    for (size_t i = 0; i < candidate.game_mode_configs_count; ++i) {
        const auto &mode = candidate.game_mode_configs[i];
        if (mode.mode_id != MODE_ULTIMATE || !mode.ultimate_profile_id) continue;
        UltimateProfile &selected = candidate.ultimate_profiles[0];
        if (profile_store.Read(mode.ultimate_profile_id, selected) == ProfileStore::Status::Ok &&
            mode.ultimate_profile_engine != (selected.schema_version == ultimate_native::kSchema ? 1 : 0)) {
            static const char message[] = "Selected Ultimate engine mismatch";
            return WritePacket(CMD_ERROR, (uint8_t *)message, sizeof(message));
        }
    }
    if (candidate.ultimate_profiles_count == 0) candidate.ultimate_profiles[0] = UltimateProfile_init_default;
    if (!persistence.SaveConfig(candidate)) {
        char errmsg[] = "Failed to save config to memory";
        WritePacket(CMD_ERROR, (uint8_t *)errmsg, sizeof(errmsg));
        return false;
    }

    // Reference receipts are firmware-owned. A whole-Config client cannot
    // forge a successful transaction receipt or erase its query evidence.
    _config = candidate;

    WritePacket(CMD_SUCCESS, nullptr, 0);
    return true;
}

#if GLYPH_STRICT_HARDENING_CANDIDATE
bool ConfiguratorBackend::PrepareProfileMutation(const ProfileStoreRequest &request) {
    _last_profile_rx.phase = 7;
    if (!TraceProfileStage(request, 39, request.fault_ticket)) return false;
    if (request.fault_ticket && !ProfileStoreFaultControls::BeginMutation(request.fault_ticket)) return false;
    _last_profile_rx.phase = 8;
    return TraceProfileStage(request, 40, request.fault_ticket);
}

bool ConfiguratorBackend::TraceProfileDispatch(const ProfileStoreRequest &request) {
    // Entered this operation branch; this does not prove a storage call ran.
    _last_profile_rx.phase = 9;
    return TraceProfileStage(request, 41, request.operation);
}

#endif

// Keep pure identity/capacity phases off the later filesystem call stack.
// The existing handler is synchronous core0 and already owns static RX/TX state.
static __attribute__((noinline)) bool PrepareStoreIdentity(ProfileStoreRequest &request, ProfileStoreTransactionIdentity &identity) {
    return ProfileStoreRequestIdentity(request, identity);
}
static __attribute__((noinline)) void CaptureStoreCapacity(ProfileStore::CapacityInfo &capacity) {
    capacity = profile_store.Capacity();
}
namespace {
constexpr size_t kFrameLimit = 8192;
static ProfileStoreRequest request;
static ProfileStoreResponse response;
static uint8_t frame[kFrameLimit];
static ultimate_native::PayloadLease incoming_native;
static bool profile_received;
static ProfileStoreTransactionIdentity identity;
static ProfileStore::TransactionResult result;
}
bool ConfiguratorBackend::HandleProfileStore() {
    incoming_native.Release();
    struct IncomingScope { ~IncomingScope() { incoming_native.Release(); } } incoming_scope;
    profile_received = false;
    const bool received = ReceiveProfileStore();
    if (!profile_received) return received;
    if (!DispatchProfileStore()) return false;
    return RespondProfileStore();
}
__attribute__((noinline)) bool ConfiguratorBackend::ReceiveProfileStore() {
    const size_t length = ReadPacket(frame, sizeof(frame));
    if (_packet_timed_out) {
#if GLYPH_STRICT_HARDENING_CANDIDATE
        _last_profile_rx = _rx;
        {
            // Reuse the abandoned frame storage; bounded metadata only.
            const int count = snprintf(reinterpret_cast<char *>(frame), 192,
                "Profile store frame timeout phase=%lu raw=%lu decoded=%lu elapsed_ms=%lu tasks=%lu last_ms=%lu fetched=%lu eop=0",
                (unsigned long)_rx.phase, (unsigned long)_rx.raw, (unsigned long)_rx.decoded,
                (unsigned long)_rx.elapsed, (unsigned long)_rx.task_passes,
                (unsigned long)_rx.last_progress, (unsigned long)_rx.fetched);
            return count > 0 && count < 192 && WriteProfilePacket(CMD_ERROR, frame, count);
        }
#endif
        static constexpr char timeout[] = "Profile store frame timeout";
        return WriteProfilePacket(CMD_ERROR, (const uint8_t *)timeout, sizeof(timeout) - 1);
    }
    if (length == sizeof(frame)) {
#if GLYPH_STRICT_HARDENING_CANDIDATE
        _last_profile_rx = _rx;
#endif
        return WriteProfilePacket(CMD_ERROR, (const uint8_t *)"Profile store frame too large", 29);
    }
    request = ProfileStoreRequest_init_default;
    if (!ultimate_native::PrepareRequest(frame, length, request, incoming_native))
        return WriteProfilePacket(CMD_ERROR, (const uint8_t *)"Invalid profile store request", 29);
#if GLYPH_STRICT_HARDENING_CANDIDATE
    _rx.phase = 5; // record before decode, with no competing USB trace traffic
#endif
    static pb_istream_t input; input = pb_istream_from_buffer(frame, length);
    if (!pb_decode(&input, ProfileStoreRequest_fields, &request) || (request.protocol_version != 1 && request.protocol_version != 2)) {
#if GLYPH_STRICT_HARDENING_CANDIDATE
        _rx.phase = 12; _rx.flags |= 8; _last_profile_rx = _rx;
#endif
        return WriteProfilePacket(CMD_ERROR, (const uint8_t *)"Invalid profile store request", 29);
    }
    if (incoming_native.live) ultimate_native::Bind(request.profile, incoming_native);
    else request.profile.native_payload = {};
#if GLYPH_STRICT_HARDENING_CANDIDATE
    _rx.phase = 6;
    const bool mutationTrace = request.operation >= PROFILE_STORE_CREATE &&
        request.operation <= PROFILE_STORE_SET_MODE_REFERENCE;
    if (request.operation != PROFILE_STORE_LIVENESS) _last_profile_rx = _rx;
    // Retrospective receive evidence, emitted only AFTER EOP and decode.
    // No diagnostic TX competes with a still-arriving mutation body.
    if (mutationTrace && (!TraceProfileStage(request, 30, 1) ||
        !TraceProfileStage(request, 31, 1) ||
        !TraceProfileStage(request, 32, _rx.raw) ||
        !TraceProfileStage(request, 33, _rx.decoded) ||
        !TraceProfileStage(request, 34, _rx.task_passes) ||
        !TraceProfileStage(request, 35, _rx.flags & 1) ||
        !TraceProfileStage(request, 36, _rx.elapsed) ||
        !TraceProfileStage(request, 37, _rx.last_progress) ||
        !TraceProfileStage(request, 38, 1))) return false;
#endif
    if (!TraceProfileStage(request, 1)) return false; // decoded; before Config CRC
    profile_received = true;
    return true;
}
__attribute__((noinline)) unsigned ConfiguratorBackend::PrepareStoreMutation() {
    const bool query = request.operation == PROFILE_STORE_QUERY_TRANSACTION;
    // Both receipt domains share tokens. Look them up BEFORE checking any
    // stale expectations: exact completed requests replay their result.
    result = query ? profile_store.QueryTransaction(request.request_token)
                   : profile_store.QueryTransaction(identity);
    Config &candidate = ConfigWriteCandidate();
    const auto loaded = persistence.LoadConfigChecked(candidate);
    const uint64_t high_water = loaded == Persistence::LoadResult::Loaded &&
        candidate.profile_reference_token > profile_store.LastTransactionToken() ?
        candidate.profile_reference_token : profile_store.LastTransactionToken();
    response.transaction_token_high_water = high_water;
    if (loaded == Persistence::LoadResult::Loaded &&
        candidate.profile_reference_token == request.request_token) {
        if (!query && std::memcmp(candidate.profile_reference_digest, identity.digest, 32) != 0)
            result.status = ProfileStore::Status::Conflict;
        else {
            result = {ProfileStore::Status::Ok, candidate.profile_reference_result_id, 0,
                candidate.profile_reference_result_store_generation};
            response.transaction_operation = PROFILE_STORE_SET_MODE_REFERENCE;
        }
    }
    if (result.status != ProfileStore::Status::NotFound) {
        // Durable replay, conflict, or unresolved store result wins.
    } else if (_reference_unknown || persistence.IsMutationFenced() || profile_store.IsTransactionUncertain()) {
        result.status = ProfileStore::Status::UnknownOutcome;
    } else if (query) {
        if (loaded != Persistence::LoadResult::Loaded) result.status = ProfileStore::Status::IoFailure;
        else if (request.request_token <= high_water) {
            response.status = PROFILE_STORE_TRANSACTION_EXPIRED;
            return 2;
        }
    } else if (profile_store.MigrationPending()) {
        result.status = ProfileStore::Status::MigrationFenced;
    } else if (_recovery_service || _recovery_config_invalid || profile_store.IsReadOnlyRecovery()) {
        result.status = ProfileStore::Status::ReadOnlyRecovery;
    } else if (loaded != Persistence::LoadResult::Loaded) {
        result.status = ProfileStore::Status::IoFailure;
    } else if (candidate.ultimate_profile_root_format != 2) {
        result.status = ProfileStore::Status::ReadOnlyRecovery;
    } else if (request.request_token <= high_water) {
        result.status = ProfileStore::Status::Conflict;
    } else if ((request.expected_store_incarnation && request.expected_store_incarnation != profile_store.Incarnation()) ||
               request.expected_store_generation > UINT32_MAX ||
               request.expected_profile_revision > UINT32_MAX ||
               request.expected_store_generation != profile_store.Generation()) {
        result.status = ProfileStore::Status::Conflict;
    } else if (!PrepareProfileMutation(request)) {
        result.status = ProfileStore::Status::Invalid;
    } else return 1;
    return 0;
}
__attribute__((noinline)) void ConfiguratorBackend::PerformCheckedReference() {
    Config &candidate = ConfigWriteCandidate();
    if (!profile_store.IsReady()) result.status = ProfileStore::Status::IoFailure;
    else if (request.expected_config_generation != persistence.ConfigGeneration(candidate) ||
             candidate.ultimate_profile_store_format != ProfileStore::kCompactConfigFormat ||
             candidate.ultimate_profile_store_incarnation != profile_store.Incarnation() ||
             request.mode_config_index >= candidate.game_mode_configs_count)
        result.status = ProfileStore::Status::Conflict;
    else if (candidate.game_mode_configs[request.mode_config_index].mode_id != MODE_ULTIMATE)
        result.status = ProfileStore::Status::Invalid;
    else {
        // Reuse the response's unpublished profile slot for validation;
        // reference responses keep has_profile false. No third payload.
        const auto selected_status = request.profile_id == 0 ? ProfileStore::Status::Ok :
            profile_store.Read(request.profile_id, response.profile);
        if (selected_status != ProfileStore::Status::Ok && selected_status != ProfileStore::Status::RecoveredPrevious)
            result.status = ProfileStore::Status::NotFound;
        else {
            GameModeConfig &mode = candidate.game_mode_configs[request.mode_config_index];
            mode.ultimate_profile_id = request.profile_id;
            mode.ultimate_profile_engine = request.profile_id && response.profile.schema_version == ultimate_native::kSchema ? 1 : 0;
            mode.ultimate_profile_config = 0;
            candidate.profile_reference_token = identity.token;
            std::memcpy(candidate.profile_reference_digest, identity.digest, 32);
            candidate.profile_reference_result_id = request.profile_id;
            candidate.profile_reference_result_store_generation = profile_store.Generation();
            candidate.profile_reference_result_mode_index = request.mode_config_index;
            // Same synchronous workspace lifetime as the request/response; validation
            // resets it before use, and no filesystem call retains a pointer.
            static ConfigValidationError error; error = {};
            if (!persistence.ValidateConfig(candidate, error)) result.status = ProfileStore::Status::Invalid;
            else {
                const auto saved = persistence.SaveConfigIfGenerationMatches(candidate, request.expected_config_generation);
                if (saved == Persistence::SaveResult::Conflict) result.status = ProfileStore::Status::Conflict;
                else if (saved == Persistence::SaveResult::Uncertain) {
                    _reference_unknown = true; result.status = ProfileStore::Status::UnknownOutcome;
                } else if (saved != Persistence::SaveResult::Saved) result.status = ProfileStore::Status::IoFailure;
                else result = {ProfileStore::Status::Ok, request.profile_id, 0, profile_store.Generation()};
            }
        }
    }
}
__attribute__((noinline)) bool ConfiguratorBackend::ReadStoreProfile() {
#if GLYPH_STRICT_HARDENING_CANDIDATE
    struct TraceContext { ConfiguratorBackend *backend; const ProfileStoreRequest *request; } context{this, &request};
    ProfileStoreReadTrace::Scope trace(kStrictHardeningCandidate && request.liveness_trace
        ? +[](void *opaque, uint32_t stage, uint32_t value) {
            auto &c = *static_cast<TraceContext *>(opaque);
            return c.backend->TraceProfileStage(*c.request, stage, value);
          } : nullptr, &context);
#endif
    uint32_t revision = 0;
    const auto status = profile_store.Read(request.profile_id, response.profile, &revision);
    response.has_profile = status == ProfileStore::Status::Ok || status == ProfileStore::Status::RecoveredPrevious;
    if (ProfileStoreReadTrace::Failed() || !TraceProfileStage(request, 19, response.has_profile)) return false;
    result = {status, request.profile_id, revision, profile_store.Generation()};
    return true;
}
__attribute__((noinline)) bool ConfiguratorBackend::FillStoreStatus() {
    response.status = _recovery_storage_available && profile_store.IsReady() &&
        !profile_store.IsReadOnlyRecovery() && !_recovery_config_invalid &&
        !persistence.IsMutationFenced() && !_reference_unknown &&
        !profile_store.IsTransactionUncertain() ? PROFILE_STORE_OK : PROFILE_STORE_IO_FAILURE;
    if (!_recovery_storage_available) strlcpy(response.diagnostic, "filesystem.unavailable", sizeof(response.diagnostic));
    else if (_recovery_config_invalid) strlcpy(response.diagnostic, "config.invalid", sizeof(response.diagnostic));
    else if (persistence.IsMutationFenced() || _reference_unknown) strlcpy(response.diagnostic, "config.commit_unknown", sizeof(response.diagnostic));
    else if (profile_store.IsTransactionUncertain()) strlcpy(response.diagnostic, "directory.commit_unknown", sizeof(response.diagnostic));
    else if (profile_store.MigrationPending()) strlcpy(response.diagnostic, "migration.fenced", sizeof(response.diagnostic));
    else if (profile_store.IsReadOnlyRecovery()) strlcpy(response.diagnostic, "directory.recovery", sizeof(response.diagnostic));
    if (_recovery_storage_available) {
        if (!TraceProfileStage(request, 3)) return false; // before filesystem capacity
        static ProfileStore::CapacityInfo capacity; CaptureStoreCapacity(capacity);
        if (!TraceProfileStage(request, 4)) return false; // capacity complete
        response.filesystem_total_bytes = capacity.total_bytes;
        response.filesystem_used_bytes = capacity.used_bytes;
        response.filesystem_free_bytes = capacity.free_bytes;
        response.filesystem_block_bytes = capacity.block_size;
        response.filesystem_program_bytes = capacity.page_size;
        response.reserved_bytes = capacity.reserve_bytes;
        response.protected_bytes = capacity.protected_bytes;
        response.staging_bytes = capacity.staging_bytes;
        response.admissible_profiles = capacity.admissible_profiles;
        response.mutation_feasible = capacity.mutation_feasible && !_recovery_service && !_recovery_config_invalid &&
            !_reference_unknown && !persistence.IsMutationFenced();
    }
    response.transaction_token_high_water = profile_store.LastTransactionToken();
    if (_recovery_storage_available && !_recovery_config_invalid) {
        if (!TraceProfileStage(request, 5)) return false; // before durable Config read
        Config &durable = ConfigWriteCandidate();
        if (persistence.LoadConfigChecked(durable) == Persistence::LoadResult::Loaded) {
            if (durable.profile_reference_token > response.transaction_token_high_water)
                response.transaction_token_high_water = durable.profile_reference_token;
            if (durable.ultimate_profile_root_format != 2) {
                response.mutation_feasible = false;
                response.recovery_flags |= 1u << 20;
            }
        }
    }
    if (!TraceProfileStage(request, 6)) return false; // Config complete; before diagnostics
#if GLYPH_STRICT_HARDENING_CANDIDATE
    const auto resources = ReadResourceDiagnostics();
    if (!TraceProfileStage(request, 7)) return false; // diagnostics complete
    response.core0_stack_min_free_bytes = resources.core0_stack_min_free_bytes;
    response.core1_stack_min_free_bytes = resources.core1_stack_min_free_bytes;
    response.heap_arena_peak_bytes = resources.heap_arena_peak_bytes;
    response.heap_arena_current_bytes = resources.heap_arena_current_bytes;
    response.heap_arena_capacity_bytes = resources.heap_arena_capacity_bytes;
    response.resource_diagnostics_enabled = resources.resource_diagnostics_enabled;
    response.strict_hardening_candidate = kStrictHardeningCandidate;
#endif
    return true;
}
__attribute__((noinline)) void ConfiguratorBackend::FillStoreList() {
    const size_t cursor = request.page_cursor;
    const size_t count = request.page_size == 0 ? 8 : request.page_size;
    if (!profile_store.IsReady()) response.status = PROFILE_STORE_IO_FAILURE;
    else if (count > 8 || cursor > profile_store.Count()) response.status = PROFILE_STORE_INVALID;
    else {
        const size_t end = cursor + count < profile_store.Count() ? cursor + count : profile_store.Count();
        for (size_t i = cursor; i < end; ++i) {
            const ProfileStore::Entry *entry = profile_store.EntryAt(i);
            ProfileStoreEntry &out = response.entries[response.entries_count++];
            out.profile_id = entry->id; out.revision = entry->revision; out.display_rank = entry->rank;
            out.payload_version = entry->payload_version;
            strlcpy(out.name, entry->name, sizeof(out.name));
            // Zero means uninspected. Enumeration never reads payloads.
        }
        response.next_page_cursor = end < profile_store.Count() ? end : 0;
        response.status = PROFILE_STORE_OK;
    }
}
__attribute__((noinline)) bool ConfiguratorBackend::DispatchProfileStore() {
    response = ProfileStoreResponse_init_default;
    response.protocol_version = request.protocol_version;
    response.mutation_protocol_version = 2;
    response.store_incarnation = _recovery_storage_available ? profile_store.Incarnation() : 0;
    response.request_token = request.request_token;
    response.store_generation = profile_store.Generation();
    const bool pulse = request.operation == PROFILE_STORE_LIVENESS;
    response.config_generation = pulse ? 0 : persistence.ConfigGeneration(_config);
    response.status = PROFILE_STORE_UNSUPPORTED;
    profile_store.ResetDiagnostic();
    const bool mutation = request.operation >= PROFILE_STORE_CREATE &&
        request.operation <= PROFILE_STORE_SET_MODE_REFERENCE;
    const bool query = request.operation == PROFILE_STORE_QUERY_TRANSACTION;
    identity = {};
    result = {};
    bool handled = false;
#if GLYPH_STRICT_HARDENING_CANDIDATE
    const bool ticket_invalid = request.fault_ticket &&
        (!mutation || request.protocol_version != 2 || !kStrictHardeningCandidate);
#else
    // Retired acceptance controls must never silently request a real mutation
    // or trigger reconciliation. Keep their wire tags inert and reject them
    // before either receipt domain can perform storage work.
    const bool ticket_invalid = request.fault_kind || request.fault_operation ||
        request.fault_phase || request.fault_result || request.fault_path_class ||
        request.fault_skip || request.fault_clear || request.fault_ticket || request.liveness_trace;
#endif
    // Scope ends before encoding/TX, including failed/unused rules. Pending
    // rules never affect STATUS, QUERY, replay without ticket, or legacy SET.
#if GLYPH_STRICT_HARDENING_CANDIDATE
    struct FaultScope { ~FaultScope(){ProfileStoreFaultControls::EndMutation();} } fault_scope;
#endif
    if (!TraceProfileStage(request, 2)) return false; // CRC complete; before reconciliation

    // Reconcile durable publications before using RAM for replay or admitting
    // another mutation. A failed authoritative reread leaves the fence intact.
    if (!ticket_invalid && _recovery_storage_available && (mutation || query)) {
        if (profile_store.IsTransactionUncertain()) profile_store.ReconcileTransaction();
        if (_reference_unknown || persistence.IsMutationFenced()) {
            Config &durable = ConfigWriteCandidate();
            if (persistence.ReconcileConfig(durable) == Persistence::SaveResult::Saved)
                _reference_unknown = false;
        }
    }
    if (ticket_invalid) {
        response.status = PROFILE_STORE_INVALID;
        handled = true;
    } else if (pulse) {
        response.status = kStrictHardeningCandidate && request.protocol_version == 2 ? PROFILE_STORE_OK : PROFILE_STORE_UNSUPPORTED;
#if GLYPH_STRICT_HARDENING_CANDIDATE
        response.strict_hardening_candidate = kStrictHardeningCandidate;
        if (kStrictHardeningCandidate) {
            response.rx_phase = _last_profile_rx.phase;
            response.rx_raw_bytes = _last_profile_rx.raw;
            response.rx_decoded_bytes = _last_profile_rx.decoded;
            response.rx_elapsed_ms = _last_profile_rx.elapsed;
            response.rx_task_passes = _last_profile_rx.task_passes;
            response.rx_last_progress_ms = _last_profile_rx.last_progress;
            response.rx_fetched_bytes = _last_profile_rx.fetched;
            response.rx_flags = _last_profile_rx.flags;
        }
#endif
        handled = true;
#if !GLYPH_STRICT_HARDENING_CANDIDATE
    } else if (request.operation == PROFILE_STORE_ARM_STORAGE_FAULT) {
        response.status = PROFILE_STORE_UNSUPPORTED;
        handled = true;
#endif
    } else if (mutation && request.protocol_version != 2) {
        response.status = PROFILE_STORE_UNSUPPORTED;
        handled = true;
    } else if (request.operation == PROFILE_STORE_STATUS) {
        if (!FillStoreStatus()) return false;
        handled = true;
    } else if (!_recovery_storage_available) {
        result.status = ProfileStore::Status::IoFailure;
        strlcpy(response.diagnostic, "filesystem.unavailable", sizeof(response.diagnostic));
    } else if (request.operation == PROFILE_STORE_ARM_STORAGE_FAULT) {
#if GLYPH_STRICT_HARDENING_CANDIDATE
        if (!kStrictHardeningCandidate || request.protocol_version != 2)
            response.status = PROFILE_STORE_UNSUPPORTED;
        else if (_recovery_service) response.status = PROFILE_STORE_IO_FAILURE;
        else response.status = ProfileStoreFaultControls::Arm(request.fault_kind,request.fault_operation,
            request.fault_phase,request.fault_result,request.fault_path_class,request.fault_skip,request.fault_clear)
                ? PROFILE_STORE_OK : PROFILE_STORE_INVALID;
#else
        response.status = PROFILE_STORE_UNSUPPORTED;
#endif
        handled = true;
    } else if (request.operation == PROFILE_STORE_LIST) {
        FillStoreList();
        handled = true;
    } else if (request.operation == PROFILE_STORE_INSPECT_HEALTH) {
        response.profile_id = request.profile_id;
        response.profile_health = static_cast<uint32_t>(profile_store.Health(request.profile_id)) + 1;
        response.status = PROFILE_STORE_OK;
        handled = true;
    } else if (request.operation == PROFILE_STORE_READ) {
        if (!ReadStoreProfile()) return false;
    } else if (!mutation && !query) {
        response.status = PROFILE_STORE_UNSUPPORTED;
        handled = true;
    } else if (!request.request_token || !PrepareStoreIdentity(request, identity)) {
        result.status = ProfileStore::Status::Invalid;
    } else {
        const unsigned admission = PrepareStoreMutation();
        if (admission == 2) handled = true;
        else if (admission == 1) {
            Config &candidate = ConfigWriteCandidate();
            if (request.operation == PROFILE_STORE_CREATE) {
                if (!TraceProfileDispatch(request)) return false;
                if (request.has_profile) ::new (&result) ProfileStore::TransactionResult(profile_store.Create(request.profile, request.name,
                    request.display_rank, identity)); else result = {ProfileStore::Status::Invalid};
            } else if (request.operation == PROFILE_STORE_UPDATE) {
                if (!TraceProfileDispatch(request)) return false;
                if (request.has_profile) ::new (&result) ProfileStore::TransactionResult(profile_store.Update(request.profile_id, request.profile,
                    static_cast<uint32_t>(request.expected_profile_revision), identity)); else result = {ProfileStore::Status::Invalid};
            } else if (request.operation == PROFILE_STORE_DUPLICATE) {
                if (!TraceProfileDispatch(request)) return false;
                ::new (&result) ProfileStore::TransactionResult(profile_store.Duplicate(request.profile_id,
                    static_cast<uint32_t>(request.expected_profile_revision), request.name, request.display_rank, identity));
            } else if (request.operation == PROFILE_STORE_RENAME) {
                if (!TraceProfileDispatch(request)) return false;
                ::new (&result) ProfileStore::TransactionResult(profile_store.Rename(request.profile_id, request.name,
                    static_cast<uint32_t>(request.expected_store_generation), identity));
            } else if (request.operation == PROFILE_STORE_REORDER) {
                if (!TraceProfileDispatch(request)) return false;
                ::new (&result) ProfileStore::TransactionResult(profile_store.Reorder(request.profile_id, request.display_rank,
                    static_cast<uint32_t>(request.expected_store_generation), identity));
            } else if (request.operation == PROFILE_STORE_DELETE) {
                if (!TraceProfileDispatch(request)) return false;
                const uint32_t referenced = ReferencesProfile(_config, request.profile_id) ||
                    ReferencesProfile(candidate, request.profile_id) ? request.profile_id : 0;
                ::new (&result) ProfileStore::TransactionResult(profile_store.Delete(request.profile_id,
                    static_cast<uint32_t>(request.expected_store_generation), referenced, identity));
            } else if (request.operation == PROFILE_STORE_SET_MODE_REFERENCE) {
                if (!TraceProfileDispatch(request)) return false;
                PerformCheckedReference();
            }
        }
    }
    if (!handled) {
        response.profile_id = result.id;
        response.profile_revision = result.revision;
        response.store_generation = result.status == ProfileStore::Status::Ok ? result.generation : profile_store.Generation();
        response.config_generation = persistence.ConfigGeneration(_config);
        switch (result.status) {
            case ProfileStore::Status::Ok:
            case ProfileStore::Status::RecoveredPrevious: response.status = PROFILE_STORE_OK; break;
            case ProfileStore::Status::NotFound: response.status = PROFILE_STORE_NOT_FOUND; break;
            case ProfileStore::Status::Referenced: response.status = PROFILE_STORE_REFERENCED; break;
            case ProfileStore::Status::Conflict: response.status = PROFILE_STORE_CONFLICT; break;
            case ProfileStore::Status::Full: response.status = PROFILE_STORE_FULL; break;
            case ProfileStore::Status::Aborted: response.status = PROFILE_STORE_TRANSACTION_ABORTED; break;
            case ProfileStore::Status::UnknownOutcome: response.status = PROFILE_STORE_COMMIT_UNKNOWN; break;
            case ProfileStore::Status::IoFailure:
            case ProfileStore::Status::ReadOnlyRecovery:
            case ProfileStore::Status::MigrationFenced: response.status = PROFILE_STORE_IO_FAILURE; break;
            default: response.status = PROFILE_STORE_INVALID; break;
        }
        if (!response.diagnostic[0] && (response.status == PROFILE_STORE_IO_FAILURE || response.status == PROFILE_STORE_COMMIT_UNKNOWN))
            strlcpy(response.diagnostic, profile_store.LastDiagnostic(), sizeof(response.diagnostic));
    }
#if GLYPH_STRICT_HARDENING_CANDIDATE
    ProfileStoreFaultControls::EndMutation();
    response.storage_fault_ticket = ProfileStoreFaultControls::Current().ticket;
    response.storage_fault_pending = ProfileStoreFaultControls::Current().pending;
    response.fault_control_version = kStrictHardeningCandidate ? 2 : 0;
    response.storage_fault_capable = kStrictHardeningCandidate;
    response.storage_fault_armed = ProfileStoreFaultControls::Current().armed;
    response.storage_fault_triggered = ProfileStoreFaultControls::Current().triggered;
    response.storage_fault_operation = ProfileStoreFaultControls::Current().operation;
#endif
    response.recovery_flags |= _recovery_storage_available ? profile_store.HealthFlags() : 0;
    // Bits 16+ are the Configurator layer; store flags occupy the low 16 bits.
    if (_recovery_config_invalid) response.recovery_flags |= 1u << 16;
    if (_recovery_service) response.recovery_flags |= 1u << 19;
    if (!_recovery_storage_available) response.recovery_flags |= 1u << 17;
    if (_reference_unknown || persistence.IsMutationFenced()) response.recovery_flags |= 1u << 18;
    return true;
}
__attribute__((noinline)) bool ConfiguratorBackend::RespondProfileStore() {
    // Release the borrowed immutable RX bytes after all identity/transaction
    // work, before response encoding reuses that same frame. READ leases use
    // the separate record wire and remain synchronous through this encode.
    incoming_native.Release();
    request.profile.native_payload = {};
    // The request is decoded into owned static fields before reusing frame.
    // Encoding and transport are separate bounded stages, with no FS frames
    // alive during either stage.
    if (!TraceProfileStage(request, 8)) return false; // before bounded protobuf encode
    static pb_ostream_t output; output = pb_ostream_from_buffer(frame, sizeof(frame));
    if (!pb_encode(&output, ProfileStoreResponse_fields, &response)) {
        return false;
    }
    if (!TraceProfileStage(request, 9, output.bytes_written)) return false;
    const bool traceRead = kStrictHardeningCandidate && request.liveness_trace && request.operation == PROFILE_STORE_READ;
    if (traceRead && !TraceProfileStage(request, 20, output.bytes_written)) return false;
    size_t accepted = 0; bool flushRequested = false;
    const bool sent = WriteProfilePacket(CMD_PROFILE_STORE, frame, output.bytes_written, &accepted, &flushRequested);
    // Never interleave diagnostic frames inside a COBS response. These trailing
    // observations describe that attempt; a failed prefix is delimited first.
    if (traceRead) {
        if (!TraceProfileStage(request, 21, accepted)) return false;
        if (!TraceProfileStage(request, 22, flushRequested)) return false;
        // Completed means FIFO submitted to endpoint, not host ACK observed.
        if (!TraceProfileStage(request, 23, sent)) return false;
        if (!TraceProfileStage(request, sent ? 24 : 25, accepted)) return false;
    }
    return sent;
}

// Error formatting scratch must not remain live during unrelated storage commands.
__attribute__((noinline)) bool ConfiguratorBackend::HandleUnknownCommand(Command command) {
    char errmsg[50];
    size_t errmsg_len =
        snprintf(errmsg, sizeof(errmsg), "Unknown command ID: %d", (uint8_t)command);
    return WritePacket(CMD_ERROR, (uint8_t *)errmsg, errmsg_len);
}
