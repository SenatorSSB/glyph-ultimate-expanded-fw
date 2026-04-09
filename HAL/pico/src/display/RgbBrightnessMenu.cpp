#include "display/RgbBrightnessMenu.hpp"
#include "display/ConfigMenuAssets/GlyphMenuBitmaps.h"
#include "config/glyph/common/include/display/Font4x7Fixed.h"

#include "comms/IntegratedDisplay.hpp"

RgbBrightnessMenu::RgbBrightnessMenu(Config &config) : _config(config) {}

DisplayModeId RgbBrightnessMenu::GetId() {
    return DISPLAY_MODE_RGB_BRIGHTNESS;
}

uint8_t RGBuiRange(uint8_t backend_range) { 
    if (backend_range == 255)
        return 4;
    else if (backend_range == 30)
        return 3;
    else if (backend_range == 20)
        return 2;
    else if (backend_range == 10)
        return 1;
    else
        return 0;
}

uint8_t RGBBackendRange(uint8_t ui_range) {
    if(ui_range == 4)
        return 255;
    else if (ui_range == 3)
        return 30;
    else if (ui_range == 2)
        return 20;
    else if (ui_range == 1)
        return 10;
    else
        return 0;
}

void RgbBrightnessMenu::HandleControls(
    IntegratedDisplay *instance,
    const DisplayControls &controls,
    Button button
) {
    // const DisplayControls &controls = instance->_controls;
    if (button == controls.down) {
        if(_config.rgb_brightness == 255) return;
        _config.rgb_brightness = RGBBackendRange(RGBuiRange(_config.rgb_brightness) + 1);
    } else if (button == controls.up) {
        if(_config.rgb_brightness == 0) return;
        _config.rgb_brightness = RGBBackendRange(RGBuiRange(_config.rgb_brightness) - 1);
    } else if (button == controls.back) {
        instance->SetDisplayMode(DISPLAY_MODE_CONFIG);
    }
}

void RgbBrightnessMenu::UpdateDisplay(IntegratedDisplay *instance, Adafruit_GFX &display) {
    InputState &inputs = instance->GetInputs();
    uint8_t font_width = instance->font_width;
    uint8_t font_height = instance->font_height;
    display.setFont(&Font4x7Fixed);

    const unsigned char* bmp = bitmap_brightness_0;

    switch(RGBuiRange(_config.rgb_brightness)) {
        case 0: 
            bmp = bitmap_brightness_0;
            break;
        case 1: 
            bmp = bitmap_brightness_1;
            break;
        case 2: 
            bmp = bitmap_brightness_2;
            break;
        case 3: 
            bmp = bitmap_brightness_3;
            break;
        case 4: 
            bmp = bitmap_brightness_4;
            break;
        default:
            break; 
    }
    display.drawBitmap(0, 0, bmp, 128, 64, 1);

    // Current brightness value.
    display.setCursor(62, 26);
    display.print(RGBuiRange(_config.rgb_brightness));

    display.setCursor(2, 11);
    display.print("RGB Brightness");

    if(inputs.mb1) {
        display.fillRect(2, 46, 18, 18, 1);
    }
    if(inputs.mb2) {
        display.fillRect(20, 46, 18, 18, 1);
    }
    if(inputs.mb3) {
        display.fillRect(38, 46, 18, 18, 1);
    }
}