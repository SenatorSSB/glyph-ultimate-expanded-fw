#pragma once
#include <Arduino.h>
#if (defined(GLYPH_STRICT_HARDENING_CANDIDATE) && GLYPH_STRICT_HARDENING_CANDIDATE) || defined(GLYPH_CDC_COORDINATION_TEST)
#define GLYPH_CDC_TEST_COUNTERS 1
#else
#define GLYPH_CDC_TEST_COUNTERS 0
#endif
#if defined(ARDUINO_ARCH_RP2040) || defined(GLYPH_CDC_COORDINATION_TEST)
#include <pico/mutex.h>
#include <tusb.h>
extern mutex_t __usb_mutex;
extern "C" void TinyUSB_Device_Task(void);
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
        fillRx(); return _rx_end - _rx_pos;
#else
        return _stream.available();
#endif
    }
    int peek() override {
#if GLYPH_COORDINATED_CDC
        fillRx(); return _rx_pos < _rx_end ? _rx_buffer[_rx_pos] : -1;
#else
        return _stream.peek();
#endif
    }
    int read() override {
#if GLYPH_COORDINATED_CDC
        fillRx();
        if (_rx_pos == _rx_end) return -1;
#if GLYPH_CDC_TEST_COUNTERS
        ++_rx_consumed;
#endif
        return _rx_buffer[_rx_pos++];
#else
        const int byte = _stream.read();
#if GLYPH_CDC_TEST_COUNTERS
        if (byte >= 0) { ++_rx_consumed; ++_rx_fetched; }
#endif
        return byte;
#endif
    }
#if GLYPH_CDC_TEST_COUNTERS
    uint32_t RxConsumed() const { return _rx_consumed; }
    uint32_t RxFetched() const { return _rx_fetched; }
    uint32_t RxTaskPasses() const { return _rx_task_passes; }
#endif
    void serviceRx() {
#if GLYPH_COORDINATED_CDC
#if GLYPH_CDC_TEST_COUNTERS
        ++_rx_task_passes;
#endif
        TinyUSB_Device_Task(); // owns its own try-lock; no foreground Guard
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
    // The pinned IRQ drops deferred work while our mutex is held. Its caller
    // contract requires an explicit task pass afterwards; delay() does not do it.
    // Do not use yield(): its separate FlushCDC call lacks this outer mutex.
    void serviceTx() {
#if GLYPH_COORDINATED_CDC
        TinyUSB_Device_Task(); // owns its own try-lock; no Guard alive here
        Guard guard;
        if (guard.held) tud_cdc_n_write_flush(0);
#endif
    }
    bool txSubmitted() {
#if GLYPH_COORDINATED_CDC
        Guard guard;
        return guard.held && tud_cdc_n_connected(0) &&
            tud_cdc_n_write_available(0) == CFG_TUD_CDC_TX_BUFSIZE;
#else
        return true;
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
            serviceTx();
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
    // Keep PacketIO's byte/peek contract while amortizing native FIFO locking.
    // Cache ownership survives COBS next(): only PacketIO consumes delimiters.
    void fillRx() {
#if GLYPH_COORDINATED_CDC
        if (_rx_pos != _rx_end) return;
        serviceRx();
        {
            Guard guard;
            if (!guard.held) return;
            _rx_pos = 0;
            _rx_end = tud_cdc_n_read(0, _rx_buffer, sizeof(_rx_buffer));
#if GLYPH_CDC_TEST_COUNTERS
            _rx_fetched += _rx_end;
#endif
        }
        // read() may arm OUT; its completion can defer while Guard was alive.
        serviceRx();
#endif
    }
#if GLYPH_COORDINATED_CDC
    uint8_t _rx_buffer[64]{};
    uint8_t _rx_pos = 0, _rx_end = 0;
#endif
#if GLYPH_CDC_TEST_COUNTERS
    uint32_t _rx_consumed = 0, _rx_fetched = 0, _rx_task_passes = 0;
#endif
    Stream &_stream;
};
