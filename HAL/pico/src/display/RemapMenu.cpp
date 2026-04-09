#include "display/RemapMenu.hpp"
#include "display/ConfigMenuAssets/GlyphMenuBitmaps.h"
#include "config/glyph/common/include/display/Font4x7Fixed.h"
#include "img/remap.hpp"
#include "reboot.hpp"

#include "comms/IntegratedDisplay.hpp"

RemapMenu::RemapMenu() {}

DisplayModeId RemapMenu::GetId() {
    return DISPLAY_MODE_REMAPPER;
}

void RemapMenu::HandleControls(
    IntegratedDisplay *instance,
    const DisplayControls &controls,
    Button button
) {
}

void RemapMenu::UpdateDisplay(IntegratedDisplay *instance, Adafruit_GFX &display) {
    //broken - interferes with updates
    //InputState &inputs = instance->GetInputs(); 
    /*
    if(inputs.mb7) {
        watchdog_hw->scratch[0] = 0;
        watchdog_hw->scratch[1] = 0;
        reboot_firmware();
    }
    */

    uint8_t font_width = instance->font_width;
    uint8_t font_height = instance->font_height;
    display.drawBitmap(0, 0, Bitmap_Remap, 128, 64, 1);
}