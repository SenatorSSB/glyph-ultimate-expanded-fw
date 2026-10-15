#pragma once
#include <algorithm>
#include <cstddef>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <memory>
#include <vector>
#include <thread>
#include <chrono>
#include <stdexcept>
#include <pico/stdlib.h>
#include "Print.h"
#include "Stream.h"
#ifdef EOF
#undef EOF
#endif
using std::size_t;
using byte = uint8_t;
using uint = unsigned int;
using std::max;
template<class A,class B> constexpr auto min(A a,B b) -> decltype(a<b?a:b) { return a<b?a:b; }
template <class T, size_t N> constexpr size_t count_of(const T (&)[N]) { return N; }
inline unsigned long millis() { return 0; }
inline void delay(unsigned) { std::this_thread::yield(); }
struct WatchdogState { uint32_t scratch[8]{}; };
inline WatchdogState host_watchdog{};
inline WatchdogState *watchdog_hw = &host_watchdog;
inline bool host_watchdog_reboot = false;
inline bool watchdog_caused_reboot() { return host_watchdog_reboot; }
class VectorStream : public Stream {
public:
    std::vector<uint8_t> input, output;
    size_t position = 0;
    int available() override { return static_cast<int>(input.size() - position); }
    int read() override { return position < input.size() ? input[position++] : -1; }
    int peek() override { return position < input.size() ? input[position] : -1; }
    void flush() override {}
    size_t write(uint8_t byte) override { output.push_back(byte); return 1; }
    size_t write(const uint8_t *data, size_t length) override {
        output.insert(output.end(), data, data + length); return length;
    }
    void begin(unsigned) {}
    void end() {}
    int availableForWrite() { return 1024; }
    size_t print(const char *s) { return write(reinterpret_cast<const uint8_t*>(s), std::strlen(s)); }
};
inline VectorStream Serial;

struct HostBootloaderRequest {};
struct HostFirmwareReboot {};
struct HostRp2040 {
 void idleOtherCore() {}
 void resumeOtherCore() {}
 void reboot() { throw HostFirmwareReboot{}; }
 void rebootToBootloader() { throw HostBootloaderRequest{}; }
};
inline HostRp2040 rp2040;
enum class PinStatus { RISING, FALLING };
inline void attachInterrupt(unsigned,void(*)(),PinStatus) {}
inline void detachInterrupt(unsigned) {}
#ifndef __no_inline_not_in_flash_func
#define __no_inline_not_in_flash_func(f) f
#endif
