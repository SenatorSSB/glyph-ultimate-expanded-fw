#include "modes/CustomControllerMode.hpp"
#undef _MODES_CUSTOMCONTROLLERMODE_HPP
#undef _CORE_CONTROLLERMODE_HPP
#define ControllerMode LegacyControllerMode
#define CustomControllerMode LegacyCustomControllerMode
#include "frozen_custom/core/ControllerMode.hpp"
#include "modes/CustomControllerMode.hpp"
#undef CustomControllerMode
#undef ControllerMode
#include "core/config_button_validation.hpp"
#include <algorithm>
#include <cstdio>
#include <cstdlib>
#include <type_traits>
static void require(bool yes,const char *message){if(!yes){std::fprintf(stderr,"FAIL %s\n",message);std::exit(1);}}
int main(){
 static_assert(std::extent<decltype(CustomModeConfig::modifiers)>::value==20,"fresh schema/current custom cache20");
 static_assert(std::extent<decltype(Config::game_mode_configs)>::value==30,"fresh schema/current mode capacity30");
 size_t comparisons=0;
 for(int type=0;type<=5;++type)for(unsigned count:{0,1,10,20}) {
    GameModeConfig context{};context.mode_id=MODE_CUSTOM;context.button_remapping_count=3;
    context.button_remapping[0]={BTN_RF11,BTN_RF1};context.button_remapping[1]={BTN_RF12,BTN_RF1};context.button_remapping[2]={BTN_RF13,BTN_UNSPECIFIED};
    context.socd_pairs_count=1;context.socd_pairs[0]={BTN_LF5,BTN_LF2,static_cast<SocdType>(type)};
    static Config config;config=Config_init_default;config.game_mode_configs_count=1;config.game_mode_configs[0]=context;
    require(validate_config_button_bindings(config),"actual Custom preprocessing fixture admitted");
    CustomModeConfig profile{};profile.stick_range=77;profile.digital_button_mappings_count=12;profile.stick_direction_mappings_count=8;
    for(unsigned i=0;i<12;++i)profile.digital_button_mappings[i]=static_cast<Button>(17+i);
    const Button refs[]={BTN_LF2,BTN_LF5,BTN_LF3,BTN_LF1,BTN_RT5,BTN_RT2,BTN_RT3,BTN_RT4};std::copy(refs,refs+8,profile.stick_direction_mappings);
    profile.modifiers_count=count;
    for(unsigned i=0;i<count;++i){auto &m=profile.modifiers[i];m.buttons_count=1;m.buttons[0]=static_cast<Button>(33+i%8);m.axis=static_cast<AnalogAxis>(1+i%4);m.multiplier=0.95f;m.combination_mode=COMBINATION_MODE_COMPOUND;}
    CustomControllerMode actual;LegacyCustomControllerMode old;actual.SetConfig(context,profile);old.SetConfig(context,profile);
    InputState in{};uint32_t random=123;
    for(unsigned i=0;i<4096;++i){random=random*1664525+1013904223;in.buttons=uint64_t(random)|(uint64_t(random^0xabc)<<32);in.nunchuk_buttons=i%8;in.nunchuk_x=19;in.nunchuk_y=-41;OutputState a{},b{};a.buttons=b.buttons=0xa0030000;actual.UpdateOutputs(in,a,COMMS_BACKEND_XINPUT);old.UpdateOutputs(in,b,COMMS_BACKEND_XINPUT);require(a.buttons==b.buttons&&std::equal(a.analog_axes,a.analog_axes+6,b.analog_axes),"current Custom default hook equals frozen ControllerMode preprocessing/output order");++comparisons;}
 }
 // Every admitted raw input ID is independent of Button enum storage width.
 for(unsigned id=1;id<=60;++id){GameModeConfig context{};context.mode_id=MODE_CUSTOM;CustomModeConfig p{};p.digital_button_mappings_count=1;p.digital_button_mappings[0]=static_cast<Button>(id);CustomControllerMode m;m.SetConfig(context,p);InputState in{};in.buttons=uint64_t{1}<<(id-1);OutputState out{};m.UpdateOutputs(in,out,COMMS_BACKEND_XINPUT);require(out.a,"current all60button masks map exact ID to raw bit");}
 std::printf("PASS actual current Custom default hook vs frozen ControllerMode=%zu fulloutputs; all6SOCD/modifiercache0,1,10,20/Nunchuk/remapdisable;60rawButtonIDs; fresh modecapacity30\n",comparisons);
}
