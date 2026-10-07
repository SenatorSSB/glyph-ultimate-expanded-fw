#pragma once
#include <Arduino.h>
#ifndef PROGMEM
#define PROGMEM
#endif
struct GFXglyph {
    uint16_t bitmapOffset;
    uint8_t width, height, xAdvance;
    int8_t xOffset, yOffset;
};
struct GFXfont {
    uint8_t *bitmap;
    GFXglyph *glyph;
    uint16_t first, last;
    uint8_t yAdvance;
};
class Adafruit_GFX : public Print {
public:
    virtual ~Adafruit_GFX() = default;
    size_t write(uint8_t) override { return 1; }
    size_t write(const uint8_t *, size_t count) override { return count; }
    void fillScreen(uint16_t) {}
    void fillRect(int16_t,int16_t,int16_t,int16_t,uint16_t) {}
    void fillCircle(int16_t,int16_t,int16_t,uint16_t) {}
    void drawCircle(int16_t,int16_t,int16_t,uint16_t) {}
    int16_t width() const { return 128; }
    void setTextWrap(bool) {}
    void setFont(const GFXfont *) {}
    void setTextSize(uint8_t) {}
    void setTextColor(uint16_t) {}
    void setCursor(int16_t, int16_t) {}
    void drawBitmap(int16_t, int16_t, const uint8_t *, int16_t, int16_t, uint16_t) {}
    size_t print(const char *) { return 1; }
    size_t print(int) { return 1; }
    size_t println(const char *) { return 1; }
};
