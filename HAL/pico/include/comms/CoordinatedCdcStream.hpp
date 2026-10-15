#pragma once
#include <Arduino.h>
#if defined(ARDUINO_ARCH_RP2040) || defined(GLYPH_CDC_COORDINATION_TEST)
#include <pico/mutex.h>
#include <tusb.h>
extern mutex_t __usb_mutex;
#define GLYPH_COORDINATED_CDC 1
#else
#define GLYPH_COORDINATED_CDC 0
#endif

// The two production Configurator constructors pass the sole CDC Serial
// instance (TinyUSB instance 0). Share the pinned USB task IRQ's outer mutex
// before touching FIFO/endpoint locks. Never wait, yield, or run tud_task while
// holding it: an IRQ preempting this section simply defers its task work.
class CoordinatedCdcStream final : public Stream {
  public:
    explicit CoordinatedCdcStream(Stream &stream) : _stream(stream) {}
    int available() override {
#if GLYPH_COORDINATED_CDC
        Guard guard; return guard.held ? tud_cdc_n_available(0) : 0;
#else
        return _stream.available();
#endif
    }
    int peek() override {
#if GLYPH_COORDINATED_CDC
        Guard guard; uint8_t byte;
        return guard.held && tud_cdc_n_peek(0, &byte) ? byte : -1;
#else
        return _stream.peek();
#endif
    }
    int read() override {
#if GLYPH_COORDINATED_CDC
        Guard guard; return guard.held ? tud_cdc_n_read_char(0) : -1;
#else
        return _stream.read();
#endif
    }
    int availableForWrite() override {
#if GLYPH_COORDINATED_CDC
        Guard guard; return guard.held ? tud_cdc_n_write_available(0) : 0;
#else
        return _stream.availableForWrite();
#endif
    }
    void flush() override {
#if GLYPH_COORDINATED_CDC
        Guard guard; if (guard.held) tud_cdc_n_write_flush(0);
#else
        _stream.flush();
#endif
    }
    // Single nonblocking attempt for the caller-owned whole-packet deadline.
    size_t writeAvailable(const uint8_t *bytes, size_t length) {
#if GLYPH_COORDINATED_CDC
        Guard guard;
        if (!guard.held || !tud_cdc_n_connected(0)) return 0;
        const size_t free = tud_cdc_n_write_available(0);
        const size_t count = length < free ? length : free;
        return count ? tud_cdc_n_write(0, bytes, count) : 0;
#else
        return _stream.write(bytes, length);
#endif
    }
    size_t write(uint8_t byte) override { return write(&byte, 1); }
    size_t write(const uint8_t *bytes, size_t length) override {
#if GLYPH_COORDINATED_CDC
        size_t sent = 0;
        const uint32_t start = millis();
        while (sent < length && static_cast<uint32_t>(millis() - start) < 2000u) {
            {
                Guard guard;
                if (guard.held) {
                    if (!tud_cdc_n_connected(0)) break;
                    const size_t free = tud_cdc_n_write_available(0);
                    const size_t count = length - sent < free ? length - sent : free;
                    if (count) sent += tud_cdc_n_write(0, bytes + sent, count);
                }
            }
            if (sent < length) delay(1);
        }
        return sent;
#else
        return _stream.write(bytes, length);
#endif
    }
  private:
#if GLYPH_COORDINATED_CDC
    struct Guard {
        bool held;
        Guard() : held(mutex_try_enter(&__usb_mutex, nullptr)) {}
        ~Guard() { if (held) mutex_exit(&__usb_mutex); }
    };
#endif
    Stream &_stream;
};
