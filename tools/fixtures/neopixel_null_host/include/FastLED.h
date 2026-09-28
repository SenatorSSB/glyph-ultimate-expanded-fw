#pragma once
#include <cstdint>
struct CRGB {
    std::uint32_t value = 0;
    CRGB &operator=(std::uint32_t v) { value = v; return *this; }
    CRGB &operator=(const struct CHSV &v);
};
struct CHSV { std::uint8_t hue = 0, s = 0, v = 0; CHSV() = default; CHSV(std::uint8_t h, std::uint8_t sat, std::uint8_t val) : hue(h), s(sat), v(val) {} };
inline CRGB &CRGB::operator=(const CHSV &v) { value = (std::uint32_t(v.hue)<<16)|(std::uint32_t(v.s)<<8)|v.v; return *this; }
struct FastLEDHost {
    int show_count = 0;
    std::uint8_t brightness = 0;
    template<int, std::uint8_t> void addLeds(CRGB *, int) {}
    void setMaxPowerInVoltsAndMilliamps(int, int) {}
    void setMaxRefreshRate(int) {}
    void clear(bool) {}
    void setBrightness(std::uint8_t value) { brightness = value; }
    void show() { ++show_count; }
};
inline FastLEDHost FastLED;
constexpr int NEOPIXEL = 0;
template<class A, class B> constexpr auto max(A a, B b) { return a > b ? a : b; }
