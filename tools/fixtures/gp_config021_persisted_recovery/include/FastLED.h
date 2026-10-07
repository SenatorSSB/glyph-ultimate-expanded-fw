#pragma once
#include <algorithm>
#include <cstdint>
struct CHSV {
    uint8_t hue = 0, s = 0, v = 0;
    CHSV() = default;
    CHSV(uint8_t h, uint8_t saturation, uint8_t value) : hue(h), s(saturation), v(value) {}
};
struct CRGB {
    uint8_t r = 0, g = 0, b = 0;
    CRGB() = default;
    CRGB(uint8_t red,uint8_t green,uint8_t blue):r(red),g(green),b(blue) {}
    CRGB(uint32_t value) : r(value >> 16), g(value >> 8), b(value) {}
    CRGB(CHSV value) : r(value.hue), g(value.s), b(value.v) {}
    CRGB &operator=(uint32_t value) { *this = CRGB(value); return *this; }
    CRGB &operator=(CHSV value) { *this = CRGB(value); return *this; }
};
inline constexpr int NEOPIXEL = 1;
struct HostFastLed {
    CRGB *led_array = nullptr;
    CRGB *leds() { return led_array; }
    unsigned add_calls = 0, show_calls = 0, brightness_calls = 0, clear_calls = 0;
    template <int, int> HostFastLed &addLeds(CRGB *a, int) { led_array=a; ++add_calls; return *this; }
    void setMaxPowerInVoltsAndMilliamps(int, int) {}
    void setMaxRefreshRate(int) {}
    void setBrightness(uint8_t) { ++brightness_calls; }
    void show() { ++show_calls; }
    void clear(bool) { ++clear_calls; }
};
inline HostFastLed FastLED;
