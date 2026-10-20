#pragma once
#include "core/RuntimeIdentity.hpp"
#include "core/NativeTargetMetrics.hpp"

namespace runtime_identity {
class Service {
  public:
    template<class Wire>
    __attribute__((noinline)) void Poll(Wire &wire, CommunicationBackend *primary, const Config &config,
              const ProfileStore &store, const Ultimate &ultimate, uint32_t now) {
        // This reader exists only in the current primary XInput session.
        if (!primary || primary->BackendId() != COMMS_BACKEND_XINPUT) return;
#if GLYPH_NATIVE_TARGET_METRICS
        const uint32_t service_begin = native_metrics::Now();
        struct ServiceObservation {
            uint32_t begin;
            ~ServiceObservation() { native_metrics::RecordObserver(begin); }
        } observation{service_begin};
        _parser.Expire(now);
        native_metrics::ExpireRequest(now);
        unsigned diagnostic_candidates = 0;
        for (unsigned consumed = 0; consumed < 32 && wire.available() > 0; ++consumed) {
            const int byte = wire.read();
            if (byte < 0) { native_metrics::DiscardRequest(); return; }
            if (!_parser.HasPartialFrame()) {
                bool complete = false;
                const bool owned = native_metrics::ConsumeRequest(static_cast<uint8_t>(byte), now, complete);
                if (complete) ++diagnostic_candidates;
                if (owned) continue;
            }
            uint64_t token = 0;
            if (!_parser.Consume(static_cast<uint8_t>(byte), now, token)) continue;
            // Identity owns its opaque body and always wins an admitted poll.
            native_metrics::DiscardRequest();
            if (wire.availableForWrite() >= static_cast<int>(kResponseBytes + 32)) {
                uint8_t response[kResponseBytes];
                EncodeResponse(token, Observe(primary, config, store, ultimate), response);
                wire.write(response, sizeof(response));
            }
            return;
        }
        if (diagnostic_candidates == 1 && !_parser.HasPartialFrame() && wire.available() == 0 &&
            native_metrics::CanRespond(now) && wire.availableForWrite() >= 192) {
            const uint8_t *response = native_metrics::Snapshot(now, ultimate.DiagnosticNativeGeneration());
            // One admitted write, never a retry loop. Short transport writes
            // remain an unexpected failure visible in the host byte evidence.
            wire.write(response, native_metrics::kResponseBytes);
            native_metrics::ResponseAdmitted(now);
        } else if (diagnostic_candidates) native_metrics::DiscardRequest();
#else
        _parser.Expire(now);
        for (unsigned consumed = 0; consumed < 32 && wire.available() > 0; ++consumed) {
            const int byte = wire.read();
            if (byte < 0) return;
            uint64_t token = 0;
            if (!_parser.Consume(static_cast<uint8_t>(byte), now, token)) continue;
            // Complete admission before digest work or transmission. Leave the
            // existing viewer's admission reserve and never wait for the host.
            if (wire.availableForWrite() >= static_cast<int>(kResponseBytes + 32)) {
                uint8_t response[kResponseBytes];
                EncodeResponse(token, Observe(primary, config, store, ultimate), response);
                wire.write(response, sizeof(response));
            }
            return;
        }
#endif
    }
  private:
    RequestParser _parser;
};
} // namespace runtime_identity
