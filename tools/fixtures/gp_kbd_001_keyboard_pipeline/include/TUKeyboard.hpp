#ifndef GLYPH_GP_KBD_001_TUKEYBOARD_HPP
#define GLYPH_GP_KBD_001_TUKEYBOARD_HPP
#include <array>
#include <cstdint>
#include <utility>
#include <vector>
// Host observation boundary only: no USB transport, rollover or HID encoding.
class TUKeyboard {
public:
    inline static unsigned begins = 0, releases = 0;
    inline static std::array<bool, 256> keys{};
    inline static std::vector<std::array<bool, 256>> reports{};
    inline static std::vector<char> events{};
    inline static std::vector<std::pair<uint8_t, bool>> presses{};
    void begin() { ++begins; events.push_back('B'); }
    void setPressed(uint8_t key, bool pressed) { events.push_back('P'); keys[key] = pressed; presses.emplace_back(key, pressed); }
    void releaseAll() { events.push_back('R'); ++releases; keys.fill(false); }
    void sendState() { events.push_back('S'); reports.push_back(keys); }
    static void reset() { begins = releases = 0; keys.fill(false); reports.clear(); presses.clear(); events.clear(); }
};
#endif
