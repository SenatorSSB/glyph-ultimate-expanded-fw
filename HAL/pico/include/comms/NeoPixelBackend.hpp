#ifndef _COMMS_NEOPIXELBACKEND_HPP
#define _COMMS_NEOPIXELBACKEND_HPP

#include "core/CommunicationBackend.hpp"

#include "rgb/ButtonLocations.hpp"

#include <FastLED.h>
#include <config.pb.h>
#include <time.h>

template <uint8_t data_pin, int led_count> class NeoPixelBackend : public CommunicationBackend {
  public:
    NeoPixelBackend(
        InputState &inputs,
        InputSource **input_sources,
        size_t input_source_count,
        const Button *button_mappings,
        const RgbConfig *rgb_configs,
        const size_t rgb_configs_count,
        const uint8_t &brightness
    )
        : CommunicationBackend(inputs, input_sources, input_source_count),
          _button_mappings(button_mappings),
          _rgb_configs(rgb_configs),
          _rgb_configs_count(rgb_configs_count),
          _brightness(brightness) {
        FastLED.addLeds<NEOPIXEL, data_pin>(_leds, led_count);
        FastLED.setMaxPowerInVoltsAndMilliamps(5, 200);
        FastLED.setMaxRefreshRate(0);
    }

    ~NeoPixelBackend() { FastLED.clear(true); }

    virtual void SetGameMode(InputMode *gamemode) {
        // Clear current button colors.
        for (size_t i = 0; i < button_colors_count; i++) {
            _button_colors[i] = 0;
        }

        if (gamemode == nullptr || gamemode->GetConfig() == nullptr) {
            _config = nullptr;
            return;
        }

        uint8_t rgb_config_id = gamemode->GetConfig()->rgb_config;
        if (rgb_config_id == 0 || rgb_config_id > _rgb_configs_count) {
            _config = nullptr;
            return;
        }
        _config = &_rgb_configs[rgb_config_id - 1];

        RgbAnimationId id = _config->animation;

        switch(id) {
            case RGB_ANIM_BREATHE:
                //not a real thing yet lol
                _config = nullptr;
                return;
            case RGB_ANIM_REACTIVE_SIMPLE:
                //not a real thing yet lol
                _config = nullptr;
                return;
            case RGB_ANIM_STATIC:
                // Build new mapping array to give O(n) lookup later.
                for (size_t i = 0; i < _config->button_colors_count; i++) {
                    ButtonToColorMapping mapping = _config->button_colors[i];
                    _button_colors[max(0, mapping.button - 1)] = mapping.color;
                }
                break;
            case RGB_ANIM_RAINBOW_SHIFT:
                for (size_t i = 0; i < 36; i++) {
                    ButtonToColorMappingHSV mapping = RGB_Wave_StarterHSV[i];
                    mapping.color = CHSV(0, 255, 255);
                    bool mappable = false;
                    for(size_t j = 0; j < _config->button_colors_count; j++) {
                        if(_config->button_colors[j].button == mapping.button) {
                            if(_config->button_colors[j].color < 0x00FFFFFF) {
                                mappable = false;
                            } else {
                                mappable = true;
                            }
                        } 
                    }
                    if(!mappable) {
                        mapping.color.v = 0;
                        mapping.color.s = 0;
                    }
                    _ledsHSV[max(0, mapping.button - 1)] = mapping.color;
                }
                break;
            case RGB_ANIM_RAINBOW_XWAVE_LEFT:
                for (size_t i = 0; i < 36; i++) {
                    ButtonToColorMappingHSV mapping = RGB_Wave_StarterHSV[i];
                    bool mappable = false;
                    for(size_t j = 0; j < _config->button_colors_count; j++) {
                        if(_config->button_colors[j].button == mapping.button) {
                            if(_config->button_colors[j].color < 0x00FFFFFF) {
                                mappable = false;
                            } else {
                                mappable = true;
                            }
                        } 
                    }
                    if(!mappable) {
                        mapping.color.v = 0;
                        mapping.color.s = 0;
                    }
                    _ledsHSV[max(0, mapping.button - 1)] = mapping.color;
                }
                break;
            default:
                _config = nullptr;
                return;
        }
    }

    //For use before going into modes like ConfigMode and Manual FW mode
    //where you can't/won't be calling SendReport()
    virtual void ManualSendReport(CRGB led_map[led_count], uint8_t brightness) {
        for(int i = 0; i < led_count; i++) {
            _leds[i] = led_map[i];
        }
        FastLED.setBrightness(brightness);
        FastLED.show();
    }

    virtual void SendReport() {
        // Use timeout to avoid refreshing too fast which results in FastLED library blocking.
        /*
        if (!time_reached(_refresh_timeout)) {
            return;
        }
        _refresh_timeout = make_timeout_time_ms(refresh_interval_ms);
        */

        static absolute_time_t prevTime = get_absolute_time();
        absolute_time_t time = get_absolute_time();
        #ifdef NDEBUG
            absolute_time_t diff = abs(absolute_time_diff_us(prevTime, time));
        #else
            int64_t diff = abs(absolute_time_diff_us(prevTime, time));
        #endif
        prevTime = time;
        float interval = 0.08;
        uint8_t deltaHue = (diff/1000) * (interval * _config->speed);

        if(_config == nullptr) {
            for (int i = 0; i < led_count; i++) {
                Button button = this->_button_mappings[i];
                _leds[i] = 0;
            }
            FastLED.setBrightness(0);
            FastLED.show();
            return;
        }

        RgbAnimationId id = _config->animation;

        if(id == RGB_ANIM_STATIC) {
            for (int i = 0; i < led_count; i++) {
                Button button = this->_button_mappings[i];
                _leds[i] = _button_colors[max(0, button - 1)];
            }
        } else if(id == RGB_ANIM_RAINBOW_XWAVE_LEFT) {
            for (int i = 0; i < led_count; i++) {
                _ledsHSV[i].hue += deltaHue;
            }
            for (int i = 0; i < led_count; i++) {
                Button button = this->_button_mappings[i];
                _leds[i] = _ledsHSV[max(0, button - 1)];
            }
        } else if(id == RGB_ANIM_RAINBOW_SHIFT) {
            for (int i = 0; i < led_count; i++) {
                _ledsHSV[i].hue += deltaHue / 2;
            }
            for (int i = 0; i < led_count; i++) {
                Button button = this->_button_mappings[i];
                _leds[i] = _ledsHSV[max(0, button - 1)];
            }
        } 

        FastLED.setBrightness(_brightness);
        FastLED.show();
    }

  protected:
    static constexpr size_t button_colors_count =
        sizeof(RgbConfig::button_colors) / sizeof(ButtonToColorMapping);
    static constexpr uint64_t refresh_interval_ms = 4; // 250Hz refresh rate

    const Button *_button_mappings;
    const RgbConfig *_rgb_configs;
    const size_t _rgb_configs_count;
    const RgbConfig *_config = nullptr;
    const uint8_t &_brightness;

    CRGB _leds[led_count];
    CHSV _ledsHSV[led_count];
    uint32_t _button_colors[button_colors_count];
    #ifdef NDEBUG
        absolute_time_t _refresh_timeout = 0;
    #else
        absolute_time_t _refresh_timeout = {._private_us_since_boot = 0};
    #endif
};

#endif