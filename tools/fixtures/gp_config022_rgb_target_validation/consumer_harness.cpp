#include <Arduino.h>
#include <config.pb.h>
#include "glyph_config_validation.hpp"
#include "comms/NeoPixelBackend.hpp"
#include "neopixel_definitions.hpp"
#include <iostream>
#include <cstring>
#include <stdexcept>
#include <string>
#include <vector>
static void require(bool b,const char*s){if(!b)throw std::runtime_error(s);}
class Mode:public InputMode{public:void UpdateOutputs(const InputState&,OutputState&,CommunicationBackendId)override{}};
class Probe:public NeoPixelBackend<LED_PIN,LED_COUNT>{public:using Base=NeoPixelBackend<LED_PIN,LED_COUNT>;using Base::Base;uint32_t slot(size_t n)const{return _button_colors[n];}};
static Config cfg;
int main(int argc,char**argv){try{
 require(argc==3,"consumer case validation args");std::string name=argv[1];bool validate=std::string(argv[2])=="validated";
 cfg=Config_init_default;cfg.rgb_configs_count=1;cfg.rgb_configs[0].animation=name=="shift"?RGB_ANIM_RAINBOW_SHIFT:name=="xwave"?RGB_ANIM_RAINBOW_XWAVE_LEFT:RGB_ANIM_STATIC;cfg.rgb_configs[0].speed=2;
 auto &rgb=cfg.rgb_configs[0];bool seen[61]{};for(Button b:pixel_to_button_mappings)if(!seen[b]){seen[b]=true;rgb.button_colors[rgb.button_colors_count++]={b,name=="static"?uint32_t(0x123400+b):0xffffff};}require(rgb.button_colors_count==36,"actual36targets");
 if(name=="legacy"||name=="corrected"||name=="cyan") {rgb=RgbConfig_init_default;rgb.animation=RGB_ANIM_STATIC;const Button ids[]={BTN_LF1,BTN_LF2,BTN_LF3,BTN_LT1,BTN_RF1,BTN_RF2,BTN_RF5,BTN_RF6,BTN_RT1,BTN_MB1,BTN_LF5};for(size_t i=0;i<11;++i)rgb.button_colors[i]={ids[i],2282478};rgb.button_colors_count=name=="legacy"?20:11;if(name=="corrected")rgb.button_colors[0].color=0;}
 if(validate){ConfigValidationError e;require(validate_glyph_config(cfg,e),"valid unchanged config accepted");}
 InputState inputs{};uint8_t brightness=96;Probe backend(inputs,nullptr,0,pixel_to_button_mappings,cfg.rgb_configs,1,brightness);GameModeConfig game=GameModeConfig_init_default;game.rgb_config=1;Mode mode;mode.SetConfig(game);backend.SetGameMode(&mode);
 std::cout<<"slots=";for(size_t i=0;i<60;++i)std::cout<<(i?",":"")<<backend.slot(i);std::cout<<'\n';
 for(size_t step=0;step<4;++step){int show=FastLED.show_count,bc=FastLED.brightness_calls;size_t oldclock=c022_clock_index,olddiff=c022_timer_calls;backend.SendReport();require(FastLED.show_count==show+1&&FastLED.brightness_calls==bc+1,"one show/brightness each update");require(c022_timer_calls==olddiff+1&&c022_clock_index==oldclock+(step==0?2:1),"actual timer read schedule");require(FastLED.brightness==96,"brightness unchanged");std::cout<<"sample="<<step<<" diff="<<c022_last_diff<<" brightness="<<unsigned(FastLED.brightness)<<" pixels=";for(size_t i=0;i<76;++i)std::cout<<(i?",":"")<<FastLED.leds[i].value;std::cout<<'\n';}
 std::cout<<"consumer_case="<<name<<" all76pixels_all60slots PASS\n";return 0;
 }catch(const std::exception&e){std::cerr<<"FAIL: "<<e.what()<<'\n';return 1;}}
