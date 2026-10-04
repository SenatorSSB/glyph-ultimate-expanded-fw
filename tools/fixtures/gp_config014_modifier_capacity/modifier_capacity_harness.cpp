#include <array>
#include <cstddef>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <iostream>
#include <limits>
#include <string>
#include <type_traits>
#include <sanitizer/asan_interface.h>

// Visibility changes let the host inspect storage; method bodies stay production.
#define private public
#define protected public
#include "modes/CustomControllerMode.hpp"
#undef protected
#undef private
#include "../../../src/modes/CustomControllerMode.cpp"

namespace {
void check(bool ok, const char *message) {
    if (!ok) { std::cerr << "ASSERTION: " << message << '\n'; std::exit(90); }
}
template<class T> auto bytes(const T &value) {
    std::array<unsigned char, sizeof(T)> result;
    std::memcpy(result.data(), &value, sizeof(T));
    return result;
}
template<class T, size_t N> void unchanged(const T &value, const std::array<unsigned char,N> &before) {
    check(bytes(value) == before, "entire object representation changed");
}
uint64_t bit(Button b) { return uint64_t(1) << (unsigned(b) - 1); }
void populate(CustomModeConfig &c, unsigned n) {
    c.modifiers_count = n; c.stick_range = 64;
    c.stick_direction_mappings_count = 8;
    c.stick_direction_mappings[SD_LSTICK_LEFT-1] = BTN_LF1;
    c.stick_direction_mappings[SD_LSTICK_RIGHT-1] = BTN_LF2;
    c.stick_direction_mappings[SD_LSTICK_DOWN-1] = BTN_LF4;
    c.stick_direction_mappings[SD_LSTICK_UP-1] = BTN_LF5;
    c.stick_direction_mappings[SD_RSTICK_LEFT-1] = BTN_RF1;
    c.stick_direction_mappings[SD_RSTICK_RIGHT-1] = BTN_RF2;
    c.stick_direction_mappings[SD_RSTICK_DOWN-1] = BTN_RF3;
    c.stick_direction_mappings[SD_RSTICK_UP-1] = BTN_RF4;
    for (unsigned i=0;i<n && i<20;++i) {
        auto &m=c.modifiers[i]; m.buttons_count=3;
        m.buttons[0]=static_cast<Button>(BTN_LF1+i);
        m.buttons[1]=BTN_RF16; m.buttons[2]=BTN_MB1;
        m.axis=AXIS_LSTICK_X; m.multiplier=(i%2==0 ? 0.5f : 1.0f);
        m.combination_mode=COMBINATION_MODE_COMPOUND;
    }
}
void initial() {
    CustomControllerMode mode; // normal construction; no storage zeroing
    check(mode._custom_mode_config==nullptr && mode.GetConfig()==nullptr,"initial pointers");
    check(sizeof(mode._modifier_button_masks)/sizeof(uint64_t)==20,"cache extent");
    for (auto mask:mode._modifier_button_masks) check(mask==0,"initial cache zero");
    auto before=bytes(mode); InputState in{}; OutputState out{};
    out.buttons=0x123456; out.leftStickX=31; auto ob=bytes(out);
    mode.UpdateDigitalOutputs(in,out);
    mode.UpdateAnalogOutputs(in,out,COMMS_BACKEND_CONFIGURATOR);
    unchanged(mode,before); unchanged(out,ob);
}
void valid(unsigned n) {
    CustomControllerMode mode; GameModeConfig game{}; CustomModeConfig c{}; populate(c,n);
    mode.SetConfig(game,c);
    check(mode.GetConfig()==&game && mode._custom_mode_config==&c,"accepted pointers");
    for (unsigned i=0;i<20;++i) {
        const uint64_t expected=i<n ? bit(static_cast<Button>(BTN_LF1+i))|bit(BTN_RF16)|bit(BTN_MB1):0;
        check(mode._modifier_button_masks[i]==expected,"independent mask/cache boundary");
    }
    InputState in{}; OutputState out{}; in.buttons=UINT64_MAX;
    mode.UpdateOutputs(in,out,COMMS_BACKEND_CONFIGURATOR);
    uint8_t expected=64;
    for (unsigned i=0;i<n;++i) expected=128+(int(expected)-128)*(i%2==0?0.5f:1.0f);
    check(out.leftStickX==expected,"compound arithmetic/overlap order");
    check(out.leftStickY==64 && out.rightStickX==64 && out.rightStickY==64,"direction priorities");
    in.buttons=bit(BTN_LF2); out=OutputState{};
    mode.UpdateOutputs(in,out,COMMS_BACKEND_CONFIGURATOR);
    check(out.leftStickX==192 && out.leftStickY==128,"inactive modifiers");
}
void outputs() {
    CustomControllerMode mode; GameModeConfig game{}; CustomModeConfig c{}; populate(c,3);
    for (unsigned i=0;i<3;++i) { c.modifiers[i].buttons_count=1; c.modifiers[i].buttons[0]=BTN_LF6; }
    c.modifiers[0].multiplier=.5f;
    c.modifiers[1].multiplier=.75f; c.modifiers[1].combination_mode=COMBINATION_MODE_OVERRIDE;
    c.modifiers[2].multiplier=.5f;
    c.button_combo_mappings_count=1; auto &combo=c.button_combo_mappings[0];
    combo.buttons_count=2; combo.buttons[0]=BTN_LF1; combo.buttons[1]=BTN_LF3; combo.digital_output=GP_B;
    c.digital_button_mappings_count=1; c.digital_button_mappings[0]=BTN_LF1;
    c.analog_trigger_mappings_count=3;
    c.analog_trigger_mappings[0]={BTN_LF6,TRIGGER_LT,17};
    c.analog_trigger_mappings[1]={BTN_LF6,TRIGGER_LT,33};
    c.analog_trigger_mappings[2]={BTN_LF6,TRIGGER_RT,44};
    mode.SetConfig(game,c);
    check(mode._button_combo_mappings_masks[0]==(bit(BTN_LF1)|bit(BTN_LF3)),"combo mask");
    InputState in{}; in.buttons=bit(BTN_LF1)|bit(BTN_LF2)|bit(BTN_LF3)|bit(BTN_LF6);
    OutputState out{}; mode.UpdateOutputs(in,out,COMMS_BACKEND_CONFIGURATOR);
    check(!out.a && out.b,"combo filtering/digital output");
    check(mode._filtered_buttons==(bit(BTN_LF2)|bit(BTN_LF6)),"filtered inputs");
    check(out.leftStickX==152,"compound override compound order");
    check(out.triggerLAnalog==33 && out.triggerRAnalog==44,"last analog mapping wins");
    // Existing override SIGNUM uses the raw uint8 output, including a leftward value.
    c.button_combo_mappings_count=0; in.buttons=bit(BTN_LF1)|bit(BTN_LF6);
    out=OutputState{}; mode.UpdateOutputs(in,out,COMMS_BACKEND_CONFIGURATOR);
    check(out.leftStickX==152,"source-supported raw unsigned override sign");
    out.triggerLDigital=true; out.triggerRDigital=true;
    mode.UpdateAnalogOutputs(in,out,COMMS_BACKEND_CONFIGURATOR);
    check(out.triggerLAnalog==255 && out.triggerRAnalog==255,"digital trigger priority");
    in.nunchuk_connected=true; in.nunchuk_x=51; in.nunchuk_y=72; in.nunchuk_z=true;
    mode.UpdateDigitalOutputs(in,out); mode.UpdateAnalogOutputs(in,out,COMMS_BACKEND_CONFIGURATOR);
    check(out.leftStickX==51 && out.leftStickY==72 && out.triggerLDigital,"injected Nunchuk priority");
}
void oversize(pb_size_t count, bool fresh) {
    CustomControllerMode mode; GameModeConfig old_game{},new_game{}; CustomModeConfig accepted{},bad{};
    populate(accepted,20); accepted.button_combo_mappings_count=1;
    old_game.socd_pairs_count=1;
    old_game.socd_pairs[0]={BTN_RF1,BTN_RF2,SOCD_2IP};
    accepted.button_combo_mappings[0].buttons_count=1; accepted.button_combo_mappings[0].buttons[0]=BTN_LF3;
    accepted.button_combo_mappings[0].digital_output=GP_B;
    InputState in{}; in.buttons=UINT64_MAX; OutputState out{};
    if (!fresh) {
        mode.SetConfig(old_game,accepted);
        in.buttons=bit(BTN_RF1); mode.UpdateOutputs(in,out,COMMS_BACKEND_CONFIGURATOR);
        check(mode._socd_states[0].was_dir1,"seed prior SOCD state");
        in.buttons=UINT64_MAX; mode.UpdateOutputs(in,out,COMMS_BACKEND_CONFIGURATOR);
    }
    auto mb=bytes(mode); auto gb=bytes(old_game); auto cb=bytes(accepted); auto ob=bytes(out);
    new_game.socd_pairs_count=1; bad.modifiers_count=count;
    mode.SetConfig(new_game,bad);
    unchanged(mode,mb); unchanged(old_game,gb); unchanged(accepted,cb); unchanged(out,ob);
    check(mode.GetConfig()==(fresh?nullptr:&old_game),"rejected InputMode pointer");
}
void live(pb_size_t count) {
    CustomControllerMode mode; GameModeConfig game{}; CustomModeConfig c{}; populate(c,20);
    mode.SetConfig(game,c); InputState in{}; in.buttons=UINT64_MAX; OutputState out{};
    mode.UpdateOutputs(in,out,COMMS_BACKEND_CONFIGURATOR); c.modifiers_count=count;
    auto mb=bytes(mode); auto cb=bytes(c); auto gb=bytes(game); auto ob=bytes(out);
    __asan_poison_memory_region(mode._modifier_button_masks,sizeof(mode._modifier_button_masks));
    __asan_poison_memory_region(c.modifiers,sizeof(c.modifiers));
    __asan_poison_memory_region(c.stick_direction_mappings,sizeof(c.stick_direction_mappings));
    __asan_poison_memory_region(c.analog_trigger_mappings,sizeof(c.analog_trigger_mappings));
    check(!__asan_address_is_poisoned(&c.modifiers_count),"count remains readable");
    check(__asan_address_is_poisoned(c.modifiers) && __asan_address_is_poisoned(c.stick_direction_mappings)
          && __asan_address_is_poisoned(c.analog_trigger_mappings) && __asan_address_is_poisoned(mode._modifier_button_masks),"array poison active");
    mode.UpdateAnalogOutputs(in,out,COMMS_BACKEND_CONFIGURATOR);
    __asan_unpoison_memory_region(mode._modifier_button_masks,sizeof(mode._modifier_button_masks));
    __asan_unpoison_memory_region(&c,sizeof(c));
    unchanged(mode,mb); unchanged(c,cb); unchanged(game,gb); unchanged(out,ob);
    // Digital retains its policy when the live modifier count is impossible.
    c.digital_button_mappings_count=1; c.digital_button_mappings[0]=BTN_LF1;
    out=OutputState{}; mode.UpdateDigitalOutputs(in,out); check(out.a,"live-count digital policy unchanged");
}
void rebind() {
    CustomControllerMode mode; GameModeConfig game{}; CustomModeConfig c{}; populate(c,1);
    c.modifiers[0].buttons_count=1; c.modifiers[0].buttons[0]=BTN_LF6;
    mode.SetConfig(game,c); auto mask=mode._modifier_button_masks[0];
    c.modifiers[0].buttons[0]=BTN_LF7; // mutate pointed config without SetConfig
    check(mode._modifier_button_masks[0]==mask,"historical stale same-session cache observation");
    InputState in{}; in.buttons=bit(BTN_LF2)|bit(BTN_LF7); OutputState out{};
    mode.UpdateOutputs(in,out,COMMS_BACKEND_CONFIGURATOR); check(out.leftStickX==192,"no new 018 coherence claim");
}
}
int main(int argc,char **argv) {
    check(argc==2,"case argument"); const std::string name=argv[1];
    if(name=="initial") initial();
    else if(name.rfind("valid_",0)==0) valid(std::stoul(name.substr(6)));
    else if(name=="outputs") outputs();
    else if(name=="rebind") rebind();
    else if(name.rfind("direct_",0)==0) oversize(name.find("max")!=std::string::npos?std::numeric_limits<pb_size_t>::max():21,name.find("fresh")!=std::string::npos);
    else if(name=="live_21" || name=="live_max") live(name=="live_21"?21:std::numeric_limits<pb_size_t>::max());
    else check(false,"unknown case");
    std::cout << "case=" << name << " PASS\n";
}
