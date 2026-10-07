#pragma once
#include <Adafruit_GFX.h>
#include <Wire.h>
#include <string>
#include <vector>
inline constexpr int SSD1306_SWITCHCAPVCC = 2;
inline constexpr int SSD1306_WHITE = 1;
class Adafruit_SSD1306 : public Adafruit_GFX {
public:
    bool begin_ok = true;
    unsigned begin_calls = 0, clear_calls = 0, display_calls = 0, bitmap_calls = 0;
    std::vector<std::string> lines;
    Adafruit_SSD1306(int, int, HostWire *) {}
    bool begin(int, int, bool, bool) { ++begin_calls; return begin_ok; }
    void clearDisplay() { ++clear_calls; lines.clear(); }
    void display() { ++display_calls; }
    void drawBitmap(int, int, const uint8_t *, int, int, uint16_t) { ++bitmap_calls; }
    size_t println(const char *line) { lines.emplace_back(line); return lines.back().size(); }
};
