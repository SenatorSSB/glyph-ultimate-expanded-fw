
#ifndef _MODES_WORDPROCESSORMODE_HPP
#define _MODES_WORDPROCESSORMODE_HPP

#include "display/DisplayMode.hpp"

class WordProcessorMode : public DisplayMode {
  public:
    WordProcessorMode();
    DisplayModeId GetId();
    void HandleControls(
        IntegratedDisplay *instance,
        const DisplayControls &controls,
        Button button
    );
    void UpdateDisplay(IntegratedDisplay *instance, Adafruit_GFX &display);

  private:
    void save_file();
    void load_file(uint8_t file_index);

    char _text_buffer[148];
    int _cursor_pos;
    uint32_t _cursor_last_blink;
    uint8_t _file_index;
};

#endif 