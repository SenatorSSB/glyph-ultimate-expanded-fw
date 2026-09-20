#pragma once
struct CRGB { int value = 0; };
struct FastLedStub { CRGB *leds() { static CRGB values[76]; return values; } void show() {} void setBrightness(int) {} };
inline FastLedStub FastLED;
inline CRGB bootloaderRGB[76];
