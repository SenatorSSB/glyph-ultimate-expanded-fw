#include "display/OopsieMenu.hpp"
#include "display/ConfigMenuAssets/GlyphMenuBitmaps.h"
#include "display/Font4x7Fixed.h"
#include "icons/menubases.hpp"
#include "icons/12x12bitmaps.hpp"
#include "core/config_utils.hpp"

#include "comms/IntegratedDisplay.hpp"
#include "reboot.hpp"

OopsieMenu::OopsieMenu(Config &config, CommunicationBackend **backends, size_t backends_count) 
    : _config(config),
    _backends(backends),
    _backends_count(backends_count) {}

DisplayModeId OopsieMenu::GetId() {
    return DISPLAY_MODE_OOPSIE;
}

void OopsieMenu::HandleControls(
    IntegratedDisplay *instance,
    const DisplayControls &controls,
    Button button
) {
    if(button == Button_BTN_MB1) {
        //instance->SetDisplayMode(DISPLAY_MODE_BUTTON_HINTS);
    }
    if(button == Button_BTN_MB2) {
        if(_highlighted_item > 0) {
            _highlighted_item--;
        }
        return;
    }
    if(button == Button_BTN_MB3) {
        if(_highlighted_item < _backend_options_count - 1) {
            _highlighted_item++;
        }
        return;
    }
    if(button == Button_BTN_MB4) {
        CommunicationBackendId backend = _backend_options[_highlighted_item].backendId;
        if(_backend_options[_highlighted_item].retry) {
            //rp2040.idleOtherCore();
            watchdog_hw->scratch[0] = 0;
            reboot_firmware();
        }
        if(_backend_options[_highlighted_item].screenOff) {
            instance->Clear();
            instance->UpdateDisplay();
            rp2040.idleOtherCore();
            while(1);
        };
        for(size_t i = 0; i < _config.communication_backend_configs_count; i++) {
            if(backend == _config.communication_backend_configs[i].backend_id) {
                //rp2040.idleOtherCore();
                watchdog_hw->scratch[0] = i + 1;
                reboot_firmware();
            }
        }
        return;
    }
}

void OopsieMenu::UpdateDisplay(IntegratedDisplay *instance, Adafruit_GFX &display) {
    InputState &inputs = instance->GetInputs();
    uint8_t font_width = instance->font_width;
    uint8_t font_height = instance->font_height;
    display.setFont(&Font4x7Fixed);

    const unsigned char* bmp = bitmap_glyph_list_menu_base;

    display.drawBitmap(0, 0, bmp, 128, 64, 1);

    display.setCursor(0, 8);
    display.print("No Console\nDetected");

    for(size_t i = 0; i < _backend_options_count; i++) {
        display.setCursor(78, (i * (7 + 1)) + 8);
        if(i == _highlighted_item) {
            display.print("> ");
        }
        display.print(_backend_options[i].text);
        if(i == _highlighted_item) {
            display.print(" <");
        }
    }

    display.fillRect(4, 48, 12, 12, 0);
    //if(inputs.mb1) {
        //display.fillRect(2, 46, 18, 18, 1);
        //display.drawBitmap(4, 48, Back12, 12, 12, 0);
    //}
    if(inputs.mb2) {
        display.fillRect(20, 46, 18, 18, 1);
        display.drawBitmap(22, 48, UpArrow12, 12, 12, 0);
    }
    if(inputs.mb3) {
        display.fillRect(38, 46, 18, 18, 1);
        display.drawBitmap(40, 48, DownArrow12, 12, 12, 0);
    }
    if(inputs.mb4) {
        display.drawBitmap(58, 48, Confirm12, 12, 12, 0);
    }
    /*
    display.setCursor(2, 10);
    display.print("We couldn't detect a console!");

    display.setCursor(2, 19);
    display.print("Please retry or manually select a console");
    */
    


}