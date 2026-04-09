#include "rgb/ButtonLocations.hpp"

ButtonToColorMappingHSV RGB_Wave_StarterHSV[36] = {
    { .button = BTN_MB1, .color = CHSV((0.063 * 255), 255, 255) },

    { .button = BTN_LF4, .color = CHSV((0.062 * 255), 255, 255) },
    { .button = BTN_LF3, .color = CHSV((0.134 * 255), 255, 255) },
    { .button = BTN_LF2, .color = CHSV((0.212 * 255), 255, 255) },
    { .button = BTN_LF1, .color = CHSV((0.284 * 255), 255, 255) },
    { .button = BTN_LF5, .color = CHSV((0.200 * 255), 255, 255) },
    { .button = BTN_LF6, .color = CHSV((0.421 * 255), 255, 255) },
    { .button = BTN_LF7, .color = CHSV((0.356 * 255), 255, 255) },
    { .button = BTN_LF8, .color = CHSV((0.279 * 255), 255, 255) },

    { .button = BTN_LT1, .color = CHSV((0.303 * 255), 255, 255) },
    { .button = BTN_LT2, .color = CHSV((0.361 * 255), 255, 255) },
    { .button = BTN_LT3, .color = CHSV((0.367 * 255), 255, 255) },
    { .button = BTN_LT4, .color = CHSV((0.310 * 255), 255, 255) },
    { .button = BTN_LT5, .color = CHSV((0.246 * 255), 255, 255) },
    { .button = BTN_LT6, .color = CHSV((0.454 * 255), 255, 255) },

    { .button = BTN_RF1, .color = CHSV((0.716 * 255), 255, 255) },
    { .button = BTN_RF2, .color = CHSV((0.788 * 255), 255, 255) },
    { .button = BTN_RF3, .color = CHSV((0.866 * 255), 255, 255) },
    { .button = BTN_RF4, .color = CHSV((0.938 * 255), 255, 255) },
    { .button = BTN_RF5, .color = CHSV((0.716 * 255), 255, 255) },
    { .button = BTN_RF6, .color = CHSV((0.788 * 255), 255, 255) },
    { .button = BTN_RF7, .color = CHSV((0.866 * 255), 255, 255) },
    { .button = BTN_RF8, .color = CHSV((0.938 * 255), 255, 255) },
    { .button = BTN_RF9, .color = CHSV((0.780 * 255), 255, 255) },

    { .button = BTN_RF10, .color = CHSV((0.487 * 255), 255, 255) },
    { .button = BTN_RF11, .color = CHSV((0.558 * 255), 255, 255) },
    { .button = BTN_RF12, .color = CHSV((0.637 * 255), 255, 255) },
    { .button = BTN_RF13, .color = CHSV((0.487 * 255), 255, 255) },
    { .button = BTN_RF14, .color = CHSV((0.558 * 255), 255, 255) },
    { .button = BTN_RF15, .color = CHSV((0.637 * 255), 255, 255) },
    { .button = BTN_RF16, .color = CHSV((0.551 * 255), 255, 255) },

    { .button = BTN_RT1, .color = CHSV((0.697 * 255), 255, 255) },
    { .button = BTN_RT2, .color = CHSV((0.639 * 255), 255, 255) },
    { .button = BTN_RT3, .color = CHSV((0.633 * 255), 255, 255) },
    { .button = BTN_RT4, .color = CHSV((0.690 * 255), 255, 255) },
    { .button = BTN_RT5, .color = CHSV((0.754 * 255), 255, 255) },

};



ButtonToColorMapping RGB_Wave_Starter[36] = {
    { .button = BTN_MB1, .color = 0xFF6000 },

    { .button = BTN_LF4, .color = 0xFF5F00 },
    { .button = BTN_LF3, .color = 0xFFCC00 },
    { .button = BTN_LF2, .color = 0xBAFF00 },
    { .button = BTN_LF1, .color = 0x4BFF00 },
    { .button = BTN_LF5, .color = 0x86FF00 },
    { .button = BTN_LF6, .color = 0x00FF86 },
    { .button = BTN_LF7, .color = 0x00FF23 },
    { .button = BTN_LF8, .color = 0x53FF00 },

    { .button = BTN_LT1, .color = 0x2EFF00 },
    { .button = BTN_LT2, .color = 0x00FF2A },
    { .button = BTN_LT3, .color = 0x00FF34 },
    { .button = BTN_LT4, .color = 0x24FF00 },
    { .button = BTN_LT5, .color = 0x86FF00 },
    { .button = BTN_LT6, .color = 0x00FFB9 },

    { .button = BTN_RF1, .color = 0x4B00FF },
    { .button = BTN_RF2, .color = 0xBA00FF },
    { .button = BTN_RF3, .color = 0xFF00CD },
    { .button = BTN_RF4, .color = 0xFF005F },
    { .button = BTN_RF5, .color = 0x4B00FF },
    { .button = BTN_RF6, .color = 0xBA00FF },
    { .button = BTN_RF7, .color = 0xFF00CD },
    { .button = BTN_RF8, .color = 0xFF005F },
    { .button = BTN_RF9, .color = 0xAD00FF },

    { .button = BTN_RF10, .color = 0x00FFEB },
    { .button = BTN_RF11, .color = 0x00A6FF },
    { .button = BTN_RF12, .color = 0x002DFF },
    { .button = BTN_RF13, .color = 0x00FFEB },
    { .button = BTN_RF14, .color = 0x00A6FF },
    { .button = BTN_RF15, .color = 0x002DFF },
    { .button = BTN_RF16, .color = 0x00B1FF },

    { .button = BTN_RT1, .color = 0x2E00FF },
    { .button = BTN_RT2, .color = 0x002AFF },
    { .button = BTN_RT3, .color = 0x0034FF },
    { .button = BTN_RT4, .color = 0x2400FF },
    { .button = BTN_RT5, .color = 0x8600FF },
};
