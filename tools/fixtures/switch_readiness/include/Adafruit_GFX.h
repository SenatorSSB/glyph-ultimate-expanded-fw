#pragma once
#include "hardware/timer.h"

struct Adafruit_GFX {
    void setTextSize(int) {}
    void setTextColor(int) {}
    void drawBitmap(int, int, unsigned char *, int, int, int) {}
};
