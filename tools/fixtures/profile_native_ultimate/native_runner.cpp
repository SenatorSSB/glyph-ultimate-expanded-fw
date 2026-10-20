#include "modes/Ultimate.hpp"
#include "modes/UltimateNativeEvaluator.hpp"
#include "core/RuntimeProfileDigest.hpp"
#include "core/config_button_validation.hpp"
#include "core/ProfileStoreRequestIdentity.hpp"
#include <pb_decode.h>
#include <pb_encode.h>
#include <fstream>
#include <iterator>
#include <vector>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <algorithm>
#undef _MODES_ULTIMATE_HPP
#define Ultimate LegacyUltimate
#include "frozen/modes/Ultimate.hpp"
#undef Ultimate
namespace {
void require(bool value,const char *label) {if(!value){std::fprintf(stderr,"FAIL %s\n",label);std::exit(1);}}
std::vector<uint8_t> bytes(const char *path) {std::ifstream s(path,std::ios::binary);return {(std::istreambuf_iterator<char>(s)),{}};}
size_t checks=0;
uint64_t bits(std::initializer_list<int> ids) {uint64_t out=0;for(int id:ids)out|=uint64_t{1}<<(id-1);return out;}
uint64_t mask_tokens(uint32_t mask,const uint8_t *ids,size_t n) {uint64_t out=0;for(size_t i=0;i<n;++i)if(mask&(1u<<i))out|=uint64_t{1}<<(ids[i]-1);return out;}
void compare(Ultimate &native,LegacyUltimate &legacy,const InputState &in) {
    OutputState a{},b{};a.buttons=b.buttons=0xa0030000;
    native.UpdateOutputs(in,a,COMMS_BACKEND_XINPUT);legacy.UpdateOutputs(in,b,COMMS_BACKEND_XINPUT);
    if(a.buttons!=b.buttons||!std::equal(a.analog_axes,a.analog_axes+6,b.analog_axes)) {
        std::fprintf(stderr,"FAIL native differential input=%016llx expected=%08x/%u,%u,%u,%u,%u,%u actual=%08x/%u,%u,%u,%u,%u,%u\n",
            (unsigned long long)in.buttons,b.buttons,b.leftStickX,b.leftStickY,b.rightStickX,b.rightStickY,b.triggerLAnalog,b.triggerRAnalog,
            a.buttons,a.leftStickX,a.leftStickY,a.rightStickX,a.rightStickY,a.triggerLAnalog,a.triggerRAnalog);std::exit(1);
    }++checks;
}
}
int main(int argc,char **argv) {
    require(argc>=3,"usage native_runner profile.pb HEX | matrix config.pb");
    auto raw=bytes(argv[1]);static UltimateProfile p;static ultimate_native::PayloadLease lease;
    require(ultimate_native::DecodeProfile(raw.data(),raw.size(),p,lease),"native profile callback decode");
    require(ultimate_native::ValidProfile(p),"native prepare");
    static ultimate_native::OwnedProgram active;static ultimate_native::PayloadLease active_lease;
    require(ultimate_native::CopyProgram(ultimate_native::CandidateView(),active,7,true),"owned publication");
    require(ultimate_native::BindOwned(p,active,active_lease),"active wrapper rebind");
    std::fill(raw.begin(),raw.end(),0xa5);lease.Release();
    GameModeConfig mc{};mc.mode_id=MODE_ULTIMATE;mc.ultimate_profile_engine=1;
    if(!std::strcmp(argv[2],"sequence")) {
        require(argc==5,"sequence context.pb frames.txt");
        const auto context_raw=bytes(argv[3]);auto decoder=pb_istream_from_buffer(context_raw.data(),context_raw.size());
        require(pb_decode(&decoder,GameModeConfig_fields,&mc),"sequence context decode");mc.ultimate_profile_engine=1;
    }
    Ultimate mode;mode.SetConfig(mc,&p,&active.view);require(mode.ActiveEngine()==Ultimate::Engine::NativeAbi1,"context and engine accepted");
    if(!std::strcmp(argv[2],"sequence")) {
        std::ifstream frames(argv[4]);unsigned long long value;
        while(frames>>std::hex>>value) {
            InputState in{};in.buttons=value;OutputState out{};out.buttons=0xa0030000;
            mode.UpdateOutputs(in,out,COMMS_BACKEND_XINPUT);
            std::printf("%08x %u %u %u %u %u %u\n",out.buttons,out.leftStickX,out.leftStickY,out.rightStickX,out.rightStickY,out.triggerLAnalog,out.triggerRAnalog);
        }
        return 0;
    }
    if(std::strcmp(argv[2],"matrix")) {
        InputState in{};in.buttons=std::strtoull(argv[2],nullptr,16);OutputState out{};out.buttons=0xa0030000;
        mode.UpdateOutputs(in,out,COMMS_BACKEND_XINPUT);
        std::printf("%08x %u %u %u %u %u %u\n",out.buttons,out.leftStickX,out.leftStickY,out.rightStickX,out.rightStickY,out.triggerLAnalog,out.triggerRAnalog);
        return 0;
    }
    require(argc==4,"matrix legacy config required");raw=bytes(argv[3]);static Config config;
    auto stream=pb_istream_from_buffer(raw.data(),raw.size());require(pb_decode(&stream,Config_fields,&config),"legacy decode");
    GameModeConfig lc{};lc.mode_id=MODE_ULTIMATE;LegacyUltimate legacy;legacy.SetConfig(lc,&config.ultimate_profiles[0]);
    const uint8_t selector[]={4,18,19,20,24,25,34,35,36,37,41,42,43,44,45};const uint8_t dirs[]={1,2,3,5};InputState in{};
    for(uint32_t mask=0;mask<(1u<<15);++mask)for(uint32_t d=0;d<16;++d){in.buttons=mask_tokens(mask,selector,15)|mask_tokens(d,dirs,4);compare(mode,legacy,in);compare(mode,legacy,in);}
    const uint8_t specials[]={21,22,23,29,38,33,32};const uint8_t mixed[]={4,17,18,19,20,24,25,26,34,35,36,37,41,42,43,44,45,52,53,54,55};uint32_t rng=0x6178c3;
    for(uint32_t special=0;special<128;++special)for(uint32_t sample=0;sample<512;++sample){rng=rng*1664525u+1013904223u;in.buttons=mask_tokens(special,specials,7)|mask_tokens(rng,mixed,21)|mask_tokens(sample,dirs,4);compare(mode,legacy,in);}
    for(int state=0;state<8;++state)for(uint32_t mask=0;mask<1024;++mask){in.buttons=mask_tokens(mask,specials,7)|bits({1,19,25,43,45});in.nunchuk_buttons=state;in.nunchuk_x=-37;in.nunchuk_y=91;compare(mode,legacy,in);}
    in = {};
    for(int type=0;type<=5;++type) {
        GameModeConfig transformed=lc;
        transformed.button_remapping_count=3;
        transformed.button_remapping[0]={BTN_RF11,BTN_RF6};
        transformed.button_remapping[1]={BTN_RF12,BTN_RF6};
        transformed.button_remapping[2]={BTN_RF13,BTN_RF7};
        transformed.socd_pairs_count=1;
        transformed.socd_pairs[0].button_dir1=BTN_LF3;transformed.socd_pairs[0].button_dir2=BTN_LF1;
        transformed.socd_pairs[0].socd_type=static_cast<SocdType>(type);
        static Config context_config;context_config=Config_init_default;context_config.game_mode_configs_count=1;
        context_config.game_mode_configs[0]=transformed;
        require(validate_config_button_bindings(context_config),"transformed fixture production button/remap admission");
        uint8_t digest[32];require(ultimate_native::ContextDigest(transformed,digest),"all supported SOCD contexts");
        std::memcpy(active.body+28,digest,32);
        require(ultimate_native::Prepare(active.body,active.view.body_length,7,active.view),"transformed prepared test context");
        require(ultimate_native::CopyProgram(active.view,active,7,true),"context fixture publication");
        require(ultimate_native::BindOwned(p,active,active_lease),"context fixture rebind");
        Ultimate fresh;LegacyUltimate old;old.SetConfig(transformed,&config.ultimate_profiles[0]);
        transformed.ultimate_profile_engine=1;fresh.SetConfig(transformed,&p,&active.view);
        const uint64_t sequence[]={0,bits({3}),bits({3,1}),bits({1}),0,bits({1}),bits({1,3}),bits({3}),0};
        for(int repeat=0;repeat<32;++repeat)for(uint64_t state:sequence){in.buttons=state|bits({27,28,19,45});compare(fresh,old,in);}
    }
    std::printf("PASS native/full-output frozen legacy comparisons=%zu including all6SOCD histories/many-to-one remap/Nunchuk\n",checks);
}
