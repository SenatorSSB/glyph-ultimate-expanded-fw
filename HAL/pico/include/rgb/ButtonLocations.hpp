#ifndef _BUTTONLOCATIONS_HPP
#define _BUTTONLOCATIONS_HPP

#pragma once

#include <config.pb.h>
#include <FastLED.h>

//MB1 6.3%

//LF4 6.2%
//LF3 13.4%
//LF2 21.2%
//LF1 28.4%
//LF5 20.0%
//LF6 42.1%
//LF7 35.6%
//LF8 27.9%

//LT1 30.3%
//LT2 36.1%
//LT3 36.7%
//LT4 31.0%
//LT5 24.6%
//LT6 45.4%

//RF1 71.6%
//RF2 78.8%
//RF3 86.6%
//RF4 93.8%
//RF5 71.6%
//RF6 78.8%
//RF7 86.6%
//RF8 93.8%
//RF9 78.0%
//RF10 48.7%
//RF11 55.8%
//RF12 63.7%
//RF13 48.7%
//RF14 55.8%
//RF15 63.7%
//RF16 55.1%

//RT1 69.7%
//RT2 63.9%
//RT3 63.3%
//RT4 69.0%
//RT5 75.4%

typedef struct _ButtonToColorMappingHSV {
    Button button; /* The button to apply the LED color to. */
    CHSV color; /* The RGB color value to apply. */
} ButtonToColorMappingHSV;

extern ButtonToColorMappingHSV RGB_Wave_StarterHSV[36];



extern ButtonToColorMapping RGB_Wave_Starter[36];

#endif