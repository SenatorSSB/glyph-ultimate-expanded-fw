#pragma once
#include "core/RuntimeIdentity.hpp"
#include "core/NativeTargetMetrics.hpp"
#if GLYPH_NATIVE_TARGET_METRICS && (defined(ARDUINO_ARCH_RP2040) || defined(GLYPH_CDC_COORDINATION_TEST))
#include <pico/mutex.h>
#include <tusb.h>
extern mutex_t __usb_mutex;
#define GLYPH_BOUNDED_OBSERVER_CDC 1
#else
#define GLYPH_BOUNDED_OBSERVER_CDC 0
#endif

namespace runtime_identity {
#if GLYPH_BOUNDED_OBSERVER_CDC
// The production caller passes the sole CDC Serial (instance 0). Reuse the
// Configurator's outer USB task coordination: one try-lock, never a wait. The
// task IRQ defers while this bounded pass touches FIFO/endpoint locks. In
// particular, no Arduino available()/yield(), Task(), flush(), or retry loop
// runs here. Ordinary loop service handles deferred USB work after return.
class ObserverCdcPass {
  public:
    ObserverCdcPass() : held(mutex_try_enter(&__usb_mutex, nullptr)) {}
    ~ObserverCdcPass() { if (held) mutex_exit(&__usb_mutex); }
    bool Ready() const { return held; }
    int available() const { return tud_cdc_n_available(0); }
    int read() const { return tud_cdc_n_read_char(0); }
    int availableForWrite() const { return tud_cdc_n_write_available(0); }
    size_t write(const uint8_t *bytes, size_t length) const {
        if (!tud_cdc_n_connected(0)) return 0;
        const size_t free = tud_cdc_n_write_available(0);
        const size_t count = length < free ? length : free;
        return count ? tud_cdc_n_write(0, bytes, count) : 0;
    }
  private:
    const bool held;
};
#endif
class Service {
  public:
    template<class Wire>
    __attribute__((noinline)) void Poll(Wire &source, CommunicationBackend *primary, const Config &config,
              const ProfileStore &store, const Ultimate &ultimate, uint32_t now) {
        // This reader exists only in the current primary XInput session.
        if (!primary || primary->BackendId() != COMMS_BACKEND_XINPUT) return;
#if GLYPH_NATIVE_TARGET_METRICS
        const uint32_t service_begin = native_metrics::Now();
        struct ServiceObservation {
            uint32_t begin;
            ~ServiceObservation() { native_metrics::RecordObserver(begin); }
        } observation{service_begin};
#endif
#if GLYPH_BOUNDED_OBSERVER_CDC
        (void)source;
        ObserverCdcPass wire;
        if (!wire.Ready()) return;
#else
        Wire &wire = source;
#endif
#if GLYPH_NATIVE_TARGET_METRICS
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
