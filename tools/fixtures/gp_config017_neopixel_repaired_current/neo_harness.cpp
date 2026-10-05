#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <vector>
#include <string>
#include <config.pb.h>

struct TimerCall { std::int64_t from, to, diff; };
static std::vector<std::int64_t> clock_values;
static std::vector<TimerCall> timer_calls;
static std::size_t clock_index = 0;
#ifdef NDEBUG
using absolute_time_t = std::int64_t;
static std::int64_t micros(absolute_time_t t) { return t; }
#else
struct absolute_time_t { std::int64_t _private_us_since_boot = 0; };
static std::int64_t micros(absolute_time_t t) { return t._private_us_since_boot; }
#endif
static void check(bool ok, const char *text) {
    if (!ok) { std::fprintf(stderr,"ASSERTION: %s\n",text); std::exit(92); }
}
inline absolute_time_t get_absolute_time() {
    check(clock_index < clock_values.size(), "unexpected extra clock read");
#ifdef NDEBUG
    return clock_values[clock_index++];
#else
    return {clock_values[clock_index++]};
#endif
}
inline std::int64_t absolute_time_diff_us(absolute_time_t from, absolute_time_t to) {
    auto delta = micros(to) - micros(from);
    timer_calls.push_back({micros(from), micros(to), delta});
    return delta;
}
class InputMode {
public:
    explicit InputMode(GameModeConfig *cfg) : cfg_(cfg) {}
    GameModeConfig *GetConfig() { return cfg_; }
private: GameModeConfig *cfg_;
};
// The builder inserts the exact generated Button enum's numeric identities.
// The immutable016 host schema still supplies Button=int and RGB structures.
// BEGIN_AUTHENTICATED_BUTTON_IDS
constexpr Button BTN_UNSPECIFIED = 0;
constexpr Button BTN_LF1 = 1;
constexpr Button BTN_LF2 = 2;
constexpr Button BTN_LF3 = 3;
constexpr Button BTN_LF4 = 4;
constexpr Button BTN_LF5 = 5;
constexpr Button BTN_LF6 = 6;
constexpr Button BTN_LF7 = 7;
constexpr Button BTN_LF8 = 8;
constexpr Button BTN_LF9 = 9;
constexpr Button BTN_LF10 = 10;
constexpr Button BTN_LF11 = 11;
constexpr Button BTN_LF12 = 12;
constexpr Button BTN_LF13 = 13;
constexpr Button BTN_LF14 = 14;
constexpr Button BTN_LF15 = 15;
constexpr Button BTN_LF16 = 16;
constexpr Button BTN_RF1 = 17;
constexpr Button BTN_RF2 = 18;
constexpr Button BTN_RF3 = 19;
constexpr Button BTN_RF4 = 20;
constexpr Button BTN_RF5 = 21;
constexpr Button BTN_RF6 = 22;
constexpr Button BTN_RF7 = 23;
constexpr Button BTN_RF8 = 24;
constexpr Button BTN_RF9 = 25;
constexpr Button BTN_RF10 = 26;
constexpr Button BTN_RF11 = 27;
constexpr Button BTN_RF12 = 28;
constexpr Button BTN_RF13 = 29;
constexpr Button BTN_RF14 = 30;
constexpr Button BTN_RF15 = 31;
constexpr Button BTN_RF16 = 32;
constexpr Button BTN_LT1 = 33;
constexpr Button BTN_LT2 = 34;
constexpr Button BTN_LT3 = 35;
constexpr Button BTN_LT4 = 36;
constexpr Button BTN_LT5 = 37;
constexpr Button BTN_LT6 = 38;
constexpr Button BTN_LT7 = 39;
constexpr Button BTN_LT8 = 40;
constexpr Button BTN_RT1 = 41;
constexpr Button BTN_RT2 = 42;
constexpr Button BTN_RT3 = 43;
constexpr Button BTN_RT4 = 44;
constexpr Button BTN_RT5 = 45;
constexpr Button BTN_RT6 = 46;
constexpr Button BTN_RT7 = 47;
constexpr Button BTN_RT8 = 48;
constexpr Button BTN_MB1 = 49;
constexpr Button BTN_MB2 = 50;
constexpr Button BTN_MB3 = 51;
constexpr Button BTN_MB4 = 52;
constexpr Button BTN_MB5 = 53;
constexpr Button BTN_MB6 = 54;
constexpr Button BTN_MB7 = 55;
constexpr Button BTN_MB8 = 56;
constexpr Button BTN_MB9 = 57;
constexpr Button BTN_MB10 = 58;
constexpr Button BTN_MB11 = 59;
constexpr Button BTN_MB12 = 60;
// END_AUTHENTICATED_BUTTON_IDS
#include "../../../HAL/pico/include/comms/NeoPixelBackend.hpp"
#include "../../../config/glyph/glyph_mk6/include/neopixel_definitions.hpp"
#include "../../../HAL/pico/src/rgb/ButtonLocations.cpp"

class Probe : public NeoPixelBackend<LED_PIN, LED_COUNT> {
public:
    using NeoPixelBackend::NeoPixelBackend;
    unsigned hue(Button button) const { return _ledsHSV[button - 1].hue; }
};
static void sample(Probe &backend, const char *stage, int step) {
    int shows = FastLED.show_count, brightness_calls = FastLED.brightness_calls;
    auto old_clock = clock_index, old_diff = timer_calls.size();
    std::fprintf(stderr,"reached_SendReport stage=%s step=%d\n",stage,step);
    if (std::strcmp(stage,"null")==0)
        for (int i=0;i<LED_COUNT;++i) FastLED.leds[i]=0xabcdef;
    backend.SendReport();
    check(FastLED.show_count == shows + 1, "one show per update");
    check(FastLED.brightness_calls == brightness_calls + 1, "one brightness publication per update");
    check(timer_calls.size() == old_diff + 1, "one time difference per update");
    check(clock_index == old_clock + (step == 0 ? 2 : 1), "static prevTime initializes once");
    auto t = timer_calls.back();
    std::printf("sample stage=%s step=%d from=%lld to=%lld diff=%lld show_delta=%d brightness_delta=%d brightness=%u pixels=",
        stage,step,(long long)t.from,(long long)t.to,(long long)t.diff,
        FastLED.show_count-shows,FastLED.brightness_calls-brightness_calls,FastLED.brightness);
    for (int i=0;i<LED_COUNT;++i) std::printf("%s%06x",i?",":"",FastLED.leds[i].value);
    std::printf(" hues=");
    for (int i=0;i<LED_COUNT;++i) std::printf("%s%u",i?",":"",backend.hue(pixel_to_button_mappings[i]));
    std::printf("\n");
}
int main(int argc,char **argv) {
    check(argc==2,"exact case argument");
    std::string name=argv[1];
    bool reference = name.rfind("reference_",0)==0;
    bool recovery = name.rfind("recovery_",0)==0;
    if (reference) name=name.substr(10);
    if (recovery) name=name.substr(9);
    clock_values=reference ? std::vector<std::int64_t>{351000,851000} :
        std::vector<std::int64_t>{1000,101000,351000,851000,1876000};
    InputState inputs; std::uint8_t brightness=96;
    RgbConfig configs[3]{};
    Button unique_buttons[36]{}; int unique_count=0;
    for (Button b:pixel_to_button_mappings) {
        bool found=false; for(int i=0;i<unique_count;++i) found|=unique_buttons[i]==b;
        if(!found) { check(unique_count<36,"physical RGB domain too large"); unique_buttons[unique_count++]=b; }
    }
    check(LED_COUNT==76 && unique_count==36,"authenticated Mk6 pixel/domain extent");
    for (int c=0;c<3;++c) {
        configs[c].speed=2;
        configs[c].animation=c==0?RGB_ANIM_STATIC:c==1?RGB_ANIM_RAINBOW_SHIFT:RGB_ANIM_RAINBOW_XWAVE_LEFT;
        configs[c].button_colors_count=36;
        for(int i=0;i<36;++i) configs[c].button_colors[i]={unique_buttons[i],c==0?std::uint32_t(0x123400+i):0x00ffffff};
    }
    Probe backend(inputs,nullptr,0,pixel_to_button_mappings,configs,3,brightness);
    GameModeConfig game{}; InputMode mode(&game);
    bool valid=name=="static"||name=="shift"||name=="xwave";
    if(valid) { game.rgb_config=name=="static"?1:name=="shift"?2:3; if(!recovery) backend.SetGameMode(&mode); }
    else if(name=="startup_null") {}
    else if(name=="no_mode") backend.SetGameMode(nullptr);
    else if(name=="no_config") { InputMode missing(nullptr); backend.SetGameMode(&missing); }
    else if(name=="zero_rgb_index") backend.SetGameMode(&mode);
    else if(name=="out_of_range_rgb_index") { game.rgb_config=4; backend.SetGameMode(&mode); }
    else if(name=="unsupported_animation") { game.rgb_config=1; configs[0].animation=RGB_ANIM_BREATHE; backend.SetGameMode(&mode); }
    else if(name=="unknown_animation_enum") { game.rgb_config=1; configs[0].animation=static_cast<RgbAnimationId>(6); backend.SetGameMode(&mode); }
    else check(false,"unknown case");
    if(recovery) {
        sample(backend,"null",0); sample(backend,"null",1);
        backend.SetGameMode(&mode); sample(backend,"valid",2);
    } else if(reference) sample(backend,"valid",0);
    else for(int i=0;i<4;++i) sample(backend,valid?"valid":"null",i);
    return 0;
}
