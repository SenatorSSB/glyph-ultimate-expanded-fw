#include <Adafruit_TinyUSB.h>
#include "comms/backend_init.hpp"
#include "glyph_overrides.hpp"
#include "glyph_config_validation.hpp"
#include "friend_profile_provisioning.hpp"
#include "modes/Ultimate.hpp"
#include "util/state_util.hpp"
#include <fstream>
#include <iostream>
#include <string>
#include <vector>
#include <cstdlib>

static Config baked, loaded, changed, injected;
static unsigned checks = 0;
static void require(bool ok, const std::string &label) {
    ++checks;
    if (!ok) { std::cerr << "FAIL " << label << '\n'; std::exit(1); }
}
static uint64_t mask(std::initializer_list<Button> buttons) {
    uint64_t value = 0; for (auto button : buttons) set_button(value, button, true); return value;
}
static OutputState frame(Ultimate &mode, uint64_t buttons, CommunicationBackendId backend = COMMS_BACKEND_GAMECUBE) {
    InputState input{}; input.buttons = buttons; OutputState output{}; mode.UpdateOutputs(input, output, backend); return output;
}
static OutputState output(uint64_t buttons, CommunicationBackendId backend = COMMS_BACKEND_GAMECUBE) {
    Ultimate mode; mode.SetConfig(baked.game_mode_configs[2]); return frame(mode, buttons, backend);
}
struct Point { int x, y; };
static const Point tables[9][9] = {
    {{61,51},{51,128},{195,51},{61,128},{128,128},{195,128},{61,195},{128,195},{195,195}},
    {{98,51},{128,51},{158,51},{98,128},{128,128},{158,128},{98,195},{128,195},{158,195}},
    {{61,100},{128,100},{195,100},{61,128},{128,128},{195,128},{61,156},{128,156},{195,156}},
    {{81,81},{128,81},{175,81},{81,128},{128,128},{175,128},{81,175},{128,175},{175,175}},
    {{69,87},{128,87},{187,87},{69,128},{128,128},{187,128},{69,167},{128,167},{187,167}},
    {{187,88},{128,88},{69,88},{187,128},{128,128},{69,128},{187,168},{128,168},{69,168}},
    {{92,83},{128,83},{164,83},{92,128},{128,128},{164,128},{92,172},{128,172},{164,172}},
    {{128,128},{128,128},{128,128},{128,128},{128,128},{128,128},{128,128},{128,128},{128,128}},
    {{128,195},{128,195},{128,195},{128,195},{128,195},{128,195},{128,195},{128,195},{128,195}}
};
static const char *names[] = {"Default","X1","Y1","Y2","Tilt1","Tilt2","Tilt3","Mode","Up-smash"};
static const uint64_t modifiers[] = {0,mask({BTN_LT4}),mask({BTN_LT3}),mask({BTN_LT6}),mask({BTN_RF4}),mask({BTN_RF3}),mask({BTN_RF4,BTN_RF3}),mask({BTN_RF5}),mask({BTN_LT2})};
static uint64_t direction(int index, Button left, Button up) {
    uint64_t buttons = 0;
    if (index%3 == 0) set_button(buttons,left,true);
    if (index%3 == 2) set_button(buttons,BTN_LF1,true);
    if (index/3 == 0) set_button(buttons,BTN_LF2,true);
    if (index/3 == 2) set_button(buttons,up,true);
    return buttons;
}
static void left_point(const OutputState &out, Point p, const std::string &label) {
    require(out.leftStickX == p.x && out.leftStickY == p.y,
        label+" got="+std::to_string(out.leftStickX)+","+std::to_string(out.leftStickY)+" expected="+std::to_string(p.x)+","+std::to_string(p.y));
}
static void coordinates() {
    for (auto backend : {COMMS_BACKEND_XINPUT,COMMS_BACKEND_DINPUT,COMMS_BACKEND_NINTENDO_SWITCH,COMMS_BACKEND_GAMECUBE})
        for (auto left : {BTN_LF3,BTN_RF8}) for (auto up : {BTN_LF5,BTN_LT5,BTN_RF6})
            for (int table=0;table<9;++table) for (int dir=0;dir<9;++dir) {
                auto p=tables[table][dir]; require(p.x>=0 && p.x<=255 && p.y>=0 && p.y<=255,"raw range");
                left_point(output(direction(dir,left,up)|modifiers[table],backend),p,std::string(names[table])+" dir="+std::to_string(dir+1)+" physical_left="+std::to_string(left));
            }
    // Every combination of seven physical modifiers, plus inferred Tilt3 chord.
    Button keys[]={BTN_LT4,BTN_LT3,BTN_LT6,BTN_RF4,BTN_RF3,BTN_RF5,BTN_LT2};
    for (unsigned combination=0;combination<128;++combination) {
        uint64_t buttons=0; for(int i=0;i<7;++i) if(combination&(1u<<i)) set_button(buttons,keys[i],true);
        int table=(combination&64)?8:(combination&32)?7:((combination&24)==24)?6:(combination&8)?4:(combination&16)?5:(combination&2)?2:(combination&4)?3:(combination&1)?1:0;
        for(int dir=0;dir<9;++dir) left_point(output(buttons|direction(dir,BTN_RF8,BTN_RF6)),tables[table][dir],"priority "+std::to_string(combination));
    }
    // Current SOCD_2IP: initial simultaneous opposition neutral, second wins,
    // release of winner reactivates held loser. Duplicates enter same pair.
    for(auto left : {BTN_LF3,BTN_RF8}) {
        Ultimate mode; mode.SetConfig(baked.game_mode_configs[2]);
        left_point(frame(mode,mask({left,BTN_LF1})),tables[0][4],"SOCD simultaneous");
        frame(mode,0); left_point(frame(mode,mask({left})),tables[0][3],"SOCD left first");
        left_point(frame(mode,mask({left,BTN_LF1})),tables[0][5],"SOCD right second");
        left_point(frame(mode,mask({left})),tables[0][3],"SOCD left reactivated");
        frame(mode,0); frame(mode,mask({BTN_LF1}));
        left_point(frame(mode,mask({left,BTN_LF1})),tables[0][3],"SOCD left second");
    }
    for(auto up : {BTN_LT5,BTN_LF5,BTN_RF6}) {
        Ultimate mode; mode.SetConfig(baked.game_mode_configs[2]);
        left_point(frame(mode,mask({BTN_LF2,up})),tables[0][4],"vertical simultaneous");
        frame(mode,0); frame(mode,mask({BTN_LF2}));
        left_point(frame(mode,mask({BTN_LF2,up})),tables[0][7],"duplicate up second");
        left_point(frame(mode,mask({BTN_LF2})),tables[0][1],"down reactivated");
    }
    std::cout<<"COORDINATES: all 9 entries, all physical Left/Up duplicates, four backends, 128 modifier subsets PASS\nRF8: remap -> LF3 -> SOCD_2IP -> effective Left -> all modifier entries PASS\nSOCD: simultaneous neutral; second input wins; held loser reactivates PASS\n";
}
static void cstick() {
    for (auto backend : {COMMS_BACKEND_XINPUT,COMMS_BACKEND_DINPUT,COMMS_BACKEND_NINTENDO_SWITCH,COMMS_BACKEND_GAMECUBE})
        for(int t=0;t<9;++t) for(int y=-1;y<=1;++y) for(int x=-1;x<=1;++x) {
            uint64_t buttons=modifiers[t];
            if(x<0)set_button(buttons,BTN_RT3,true); if(x>0)set_button(buttons,BTN_RT5,true);
            if(y<0)set_button(buttons,BTN_RT2,true); if(y>0)set_button(buttons,BTN_RT4,true);
            auto out=output(buttons,backend);
            require(out.rightStickX==128+x*89 && out.rightStickY==128+y*127,"physical C-stick grid");
            require(out.rightStickLeft==(x<0)&&out.rightStickRight==(x>0)&&out.rightStickDown==(y<0)&&out.rightStickUp==(y>0),"C digital route");
        }
    std::cout<<"C-STICK physical RT3 Left=(39,128); RT5 Right=(217,128); RT2 Down=(128,1); RT4 Up=(128,255) PASS\nC-STICK neutral + 4 diagonals under every modifier/four backends PASS\n";
}
static void buttons() {
    for(auto key : {BTN_LF1,BTN_LF2,BTN_LF3,BTN_LF4,BTN_LF5,BTN_LF6,BTN_LF7,BTN_LF8,
        BTN_LT1,BTN_LT2,BTN_LT3,BTN_LT4,BTN_LT5,BTN_LT6,BTN_RT1,BTN_RT2,BTN_RT3,BTN_RT4,BTN_RT5,
        BTN_RF1,BTN_RF2,BTN_RF3,BTN_RF4,BTN_RF5,BTN_RF6,BTN_RF7,BTN_RF8,BTN_RF9,BTN_RF10,BTN_RF11,BTN_RF12,BTN_RF13,BTN_RF14,BTN_RF15}) {
        OutputState want{};
        switch(key) {
            case BTN_LF1: want.leftStickRight=true; break;
            case BTN_LF2: want.leftStickDown=true; break;
            case BTN_LF3: case BTN_RF8: want.leftStickLeft=true; break;
            case BTN_LF4: want.buttonL=want.triggerLDigital=true; want.triggerLAnalog=108; break;
            case BTN_LF5: case BTN_LT5: case BTN_RF6: want.leftStickUp=true; break;
            case BTN_LF6: want.dpadRight=true; break;
            case BTN_LF7: want.dpadLeft=true; break;
            case BTN_LF8: want.triggerRDigital=true; want.triggerRAnalog=255; break;
            case BTN_LT1: want.buttonR=true; break;
            case BTN_LT2: case BTN_RT1: want.a=true; break;
            case BTN_RT2: want.rightStickDown=true; break;
            case BTN_RT3: want.rightStickLeft=true; break;
            case BTN_RT4: want.rightStickUp=true; break;
            case BTN_RT5: want.rightStickRight=true; break;
            case BTN_RF1: want.b=true; break;
            case BTN_RF2: want.y=true; break;
            case BTN_RF7: want.x=true; break;
            case BTN_RF10: want.a=want.buttonL=want.triggerLDigital=want.triggerRDigital=true; want.triggerLAnalog=108; want.triggerRAnalog=255; break;
            case BTN_RF11: want.dpadDown=true; break;
            case BTN_RF12: want.a=want.b=true; break;
            case BTN_RF13: want.dpadUp=true; break;
            default: break;
        }
        auto got=output(mask({key}));
        require(got.buttons==want.buttons && got.triggerLAnalog==want.triggerLAnalog && got.triggerRAnalog==want.triggerRAnalog,"every physical button digital mapping "+std::to_string(key));
    }
    auto shield=output(mask({BTN_LF4,BTN_LT3,BTN_RF8}));
    require(shield.buttonL && shield.triggerLDigital && shield.triggerLAnalog==108 && shield.triggerRDigital && shield.triggerRAnalog==255,"LF4+LT3 Y1 + R while L remains");
    left_point(shield,tables[2][3],"LF4+LT3 preserves Y1");
    for(auto blank:{BTN_RF9,BTN_RF14,BTN_RF15}) for(int t=0;t<9;++t) for(int d=0;d<9;++d) {
        auto buttons=modifiers[t]|direction(d,BTN_RF8,BTN_RF6);
        auto plain=output(buttons),extra=output(buttons|mask({blank}));
        require(plain.buttons==extra.buttons && std::memcmp(plain.analog_axes,extra.analog_axes,6)==0,"blank no chord/function effect");
    }
    std::cout<<"BUTTONS: all 34 owner physical bindings; RF9/RF14/RF15 inert with every modifier/direction; LF4=108; R=255; LF4+LT3=Y1+R; L+R+A and A+B PASS\n";
}
static std::vector<uint8_t> encoded(const Config &config) {
    size_t size=0; require(pb_get_encoded_size(&size,Config_fields,&config),"encoded size");
    std::vector<uint8_t> bytes(size); auto stream=pb_ostream_from_buffer(bytes.data(),bytes.size());
    require(pb_encode(&stream,Config_fields,&config),"encode"); return bytes;
}
static void alter_readback() { injected=baked; injected.rgb_brightness=254; require(persistence.SaveConfig(injected),"inject structurally valid changed full Config"); }
static void invalid_readback() { injected=baked; injected.default_usb_backend_config=255; require(persistence.SaveConfig(injected),"inject invalid readback"); }
static void provisioning() {
    using namespace friend_profile;
    ConfigValidationError error{};
    require(persistence.SetValidator(validate_glyph_config),"install production validator");
    require(persistence.ValidateConfig(baked,error),std::string("production baked Config validation ")+error.message);
    changed=baked; changed.rgb_configs[0].button_colors[0].button=BTN_UNSPECIFIED;
    require(!persistence.ValidateConfig(changed,error),"C022 invalid RGB target refused");
    changed=baked; changed.default_usb_backend_config=255;
    require(!persistence.ValidateConfig(changed,error),"C023 invalid USB default index refused");
    changed=baked; changed.game_mode_configs[2].button_remapping[0].physical_button=static_cast<Button>(61);
    require(!persistence.ValidateConfig(changed,error),"C021 invalid physical binding refused");
    changed=baked; changed.game_mode_configs[0].name[0]='X';
    size_t e=0,a=0; require(!config_equal(baked,changed,e,a) && e==a,"full Config equality catches same-size non-Ultimate change");
    auto fail=[](const char *name){ require(!provision_once(changed),name); require(!marker_valid(),std::string(name)+" no valid marker"); std::cout<<"PROVISION "<<name<<" PASS\n"; };
    LittleFS.reset(); changed=baked; changed.game_mode_configs_count=255; fail("A invalid baked"); require(LittleFS.config_writes==0,"A no save");
    LittleFS.reset(); changed=baked; LittleFS.fail_config_write_open=true; fail("B save fails");
    LittleFS.reset(); changed=baked; LittleFS.fail_config_read_open=true; fail("C readback load fails");
    LittleFS.reset(); changed=baked; LittleFS.before_config_read=alter_readback; fail("D valid different full Config");
    LittleFS.reset(); changed=baked; LittleFS.marker_fault.fail_write=true; fail("E marker write fails after open"); require(!LittleFS.exists(kMarkerPath),"E partial entry removed");
    LittleFS.reset(); changed=baked; LittleFS.marker_fault.write_limit=7; fail("E2 marker short/partial write"); require(!LittleFS.exists(kMarkerPath),"E2 partial entry removed");
    LittleFS.reset(); changed=baked; LittleFS.files[kMarkerPath]=std::make_shared<std::vector<uint8_t>>(); require(!marker_valid(),"F empty not applied"); require(provision_once(changed),"F safe retry");
    for(std::string text : {std::string("friend_ultimate_20261011_applied_v0\n"),std::string(kMarkerPayload,kMarkerLength-1),std::string(kMarkerPayload)+"extra"}) {
        LittleFS.reset(); changed=baked; LittleFS.files[kMarkerPath]=std::make_shared<std::vector<uint8_t>>(text.begin(),text.end());
        require(!marker_valid(),"G old/truncated/trailing marker rejected"); require(provision_once(changed),"G retry");
    }
    LittleFS.reset(); changed=baked; require(provision_once(changed),"I first provisioning"); require(marker_valid(),"I marker verified");
    require(persistence.LoadConfigChecked(loaded)==Persistence::LoadResult::Loaded,"I load persisted");
    size_t expected=0,actual=0; require(config_equal(baked,loaded,expected,actual),"I full Config equality");
    std::cout<<"FULL CONFIG baked_encoded_length="<<expected<<" readback_encoded_length="<<actual<<" exact serialized equality=PASS\n";
    unsigned writes=LittleFS.config_writes; require(provision_once(changed),"H marker present"); require(LittleFS.config_writes==writes,"H no overwrite");
    changed=baked; changed.rgb_brightness=37; require(persistence.SaveConfig(changed),"J user later change"); writes=LittleFS.config_writes;
    require(provision_once(baked),"J normal marker path"); require(persistence.LoadConfigChecked(loaded)==Persistence::LoadResult::Loaded,"J normal load");
    require(loaded.rgb_brightness==37 && LittleFS.config_writes==writes,"J later legitimate Config preserved");
    std::cout<<"PROVISION F empty marker retry; G old/truncated/trailing rejection; H valid marker skips write; I exact first adoption + reboot; J later user change preserved PASS\n";
    // A preceding successful use must not leak static readback into later failures.
    LittleFS.reset(); changed=baked; LittleFS.before_config_read=invalid_readback; fail("invalid readback after previous success");
    LittleFS.reset(); changed=baked; LittleFS.fail_marker_read_after_write=true; fail("marker reopen/readback fails");
    LittleFS.reset(); changed=baked; LittleFS.fail_marker_write_open=true; fail("marker open fails");
    LittleFS.reset(); changed=baked; LittleFS.config_fault.fail_write=true; fail("config write I/O failure");
    LittleFS.reset(); changed=baked; LittleFS.config_fault.read_limit=1; fail("config short read");
    std::cout<<"PROVISION A-J; production validator; CRC + real nanopb roundtrip; stale-buffer repeated failure; marker readback/open/partial failures PASS\n";
}
int main(int argc,char **argv) {
    require(argc==2,"output path"); baked=glyph_default_config();
    require(baked.game_mode_configs_count==13 && baked.game_mode_configs[2].mode_id==MODE_ULTIMATE,"counts/profile");
    for(auto id:{COMMS_BACKEND_XINPUT,COMMS_BACKEND_DINPUT,COMMS_BACKEND_NINTENDO_SWITCH,COMMS_BACKEND_GAMECUBE}) {
        bool found=false; for(size_t i=0;i<baked.communication_backend_configs_count;++i) if(baked.communication_backend_configs[i].backend_id==id) {
            require(baked.communication_backend_configs[i].default_mode_config==3,"backend Ultimate default"); found=true;
        } require(found,"backend present");
    }
    auto &rgb=baked.rgb_configs[baked.game_mode_configs[2].rgb_config-1]; require(rgb.button_colors_count==0 && rgb.animation==RGB_ANIM_STATIC,"Ultimate off RGB");
    coordinates(); cstick(); buttons(); provisioning();
    auto bytes=encoded(baked); std::ofstream file(argv[1],std::ios::binary); file.write(reinterpret_cast<const char*>(bytes.data()),bytes.size()); require(bool(file),"reference blob");
    std::cout<<"TOTAL checks="<<checks<<" PASS; hardware NOT_TESTED\n";
}
