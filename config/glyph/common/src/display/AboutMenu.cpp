#include "display/AboutMenu.hpp"
#include "display/ConfigMenuAssets/GlyphMenuBitmaps.h"
#include "display/Font4x7Fixed.h"
#include "icons/menubases.hpp"

#include "comms/IntegratedDisplay.hpp"

AboutMenu::AboutMenu(Config &config) : _config(config) {}

DisplayModeId AboutMenu::GetId() {
    return DISPLAY_MODE_ABOUT;
}

void AboutMenu::HandleControls(
    IntegratedDisplay *instance,
    const DisplayControls &controls,
    Button button
) {
    if (button == controls.back) {
        instance->SetDisplayMode(DISPLAY_MODE_CONFIG);
    }
}

void AboutMenu::UpdateDisplay(IntegratedDisplay *instance, Adafruit_GFX &display) {
    InputState &inputs = instance->GetInputs();
    uint8_t font_width = instance->font_width;
    uint8_t font_height = instance->font_height;
    display.setFont(&Font4x7Fixed);

    const unsigned char* bmp = Bitmap_AboutMenu_Base;

    display.drawBitmap(0, 0, bmp, 128, 64, 1);
    display.setCursor(2, 10);
    display.print("Firmware: Glyph ");
    display.print(FIRMWARE_NAME);

    display.setCursor(2, 19);
    display.print("Version: ");
    display.print(FIRMWARE_VERSION);

    display.setCursor(2, 28);
    display.print("Device: ");
    display.print(DEVICE_NAME);

    // display.setCursor(2, 37);
    // display.print("User Name: ");
    // display.print("something");

}