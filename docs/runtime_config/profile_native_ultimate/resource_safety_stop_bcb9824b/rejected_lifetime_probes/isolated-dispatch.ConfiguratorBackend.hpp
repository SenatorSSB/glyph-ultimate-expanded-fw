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

#ifndef _COMMS_CONFIGURATORBACKEND_HPP
#define _COMMS_CONFIGURATORBACKEND_HPP

#include "comms/CoordinatedCdcStream.hpp"
#include "core/ResourceDiagnostics.hpp"
#if GLYPH_STRICT_HARDENING_CANDIDATE
#include "core/ProfileStoreRxDiagnostics.hpp"
#endif
#include "cobs/Print.h"
#include "cobs/Stream.h"
#include "core/CommunicationBackend.hpp"

#include <config.pb.h>

class ConfiguratorBackend : public CommunicationBackend {
  public:
    ConfiguratorBackend(
        InputState &inputs,
        InputSource **input_sources,
        size_t input_source_count,
        Config &config,
        Stream &stream
    );
    CommunicationBackendId BackendId();
    void SendReport();
    void SetRecoveryState(bool config_invalid, bool storage_available) {
        _recovery_service = true;
        _recovery_config_invalid = config_invalid;
        _recovery_storage_available = storage_available;
    }

  private:
    size_t ReadPacket(uint8_t *buffer, size_t max_len);
    int ReadByte();
    void SkipToNextPacket();
    bool WritePacket(Command command_id, uint8_t *buffer, size_t len);
    bool HandleUnknownCommand(Command command);
    bool HandleGetDeviceInfo();
    bool HandleGetConfig();
    bool HandleSetConfig();
    bool HandleProfileStore();
    bool ReceiveProfileStore();
    bool FillStoreStatus();
    void FillStoreList();
    void FinishStoreDispatch();
    bool DispatchProfileStore();
    unsigned PrepareStoreMutation();
    void PerformCheckedReference();
    bool ReadStoreProfile();
    bool RespondProfileStore();
    bool HandleRuntimeIdentity();
#if GLYPH_STRICT_HARDENING_CANDIDATE
    bool PrepareProfileMutation(const ProfileStoreRequest &request);
    bool TraceProfileDispatch(const ProfileStoreRequest &request);
    bool TraceProfileStage(const ProfileStoreRequest &request, uint32_t stage, uint32_t value = 0);
#else
    bool PrepareProfileMutation(const ProfileStoreRequest &request) { return request.fault_ticket == 0; }
    bool TraceProfileDispatch(const ProfileStoreRequest &) { return true; }
    bool TraceProfileStage(const ProfileStoreRequest &, uint32_t, uint32_t = 0) { return true; }
#endif
    bool WriteProfilePacket(Command command, const uint8_t *bytes, size_t length, size_t *accepted = nullptr, bool *flushRequested = nullptr);

    CoordinatedCdcStream _coordinated_stream;
    packetio::COBSStream _in;
    packetio::COBSPrint _out;
    CoordinatedCdcStream &_base_stream;
    Config &_config;
    bool _recovery_service = false;
    bool _recovery_config_invalid = false;
    bool _recovery_storage_available = true;
    bool _reference_unknown = false;
#if GLYPH_STRICT_HARDENING_CANDIDATE
    ProfileStoreRxDiagnostics _rx, _last_profile_rx;
#endif
    bool _packet_timed_out = false;
    bool _profile_tx_needs_sync = false;
};

#endif
