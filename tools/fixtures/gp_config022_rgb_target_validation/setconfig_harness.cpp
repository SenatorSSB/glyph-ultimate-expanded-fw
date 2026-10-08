#include <cstdint>
#include <cstring>
#include <iostream>
#include <iterator>
#include <limits>
#include <memory>
#include <stdexcept>
#include <string>
#include <vector>
#include <Arduino.h>
#include <LittleFS.h>
#include <pb_encode.h>
#include <pb_decode.h>
#include <config.pb.h>
#include "comms/ConfiguratorBackend.hpp"
#include "core/Persistence.hpp"
#include "core/config_validation.hpp"
#include "glyph_config_validation.hpp"
#include "config_rgb_target_domain.hpp"

void reboot_firmware() {}
void reboot_bootloader() {}
using Bytes=std::vector<uint8_t>;
static Config live, candidate, reloaded;
static unsigned char prior_live[sizeof(Config)];
static size_t cases=0, successes=0, errors=0, observed_writes=0, reference_cases=0,
              decode_cases=0, order_cases=0, controls=0;
static void require(bool condition,const std::string &message) {
    if(!condition)throw std::runtime_error(message);
}
static Config valid_config() {
    Config config=Config_init_default;
    config.game_mode_configs_count=1;config.game_mode_configs[0].mode_id=MODE_CUSTOM;
    config.custom_modes_count=10;config.game_mode_configs[0].custom_mode_config=1;
    return config;
}
static void reset_candidate() {
    candidate=Config_init_default;
    candidate.game_mode_configs_count=std::size(candidate.game_mode_configs);
    candidate.communication_backend_configs_count=std::size(candidate.communication_backend_configs);
    candidate.custom_modes_count=std::size(candidate.custom_modes);
    candidate.keyboard_modes_count=std::size(candidate.keyboard_modes);
    for(auto &mode:candidate.game_mode_configs)mode.mode_id=MODE_ULTIMATE;
}
static Bytes encode(const Config &config) {
    size_t size=0;require(pb_get_encoded_size(&size,Config_fields,&config),"real encoded size");
    Bytes bytes(size);auto stream=pb_ostream_from_buffer(bytes.data(),bytes.size());
    require(pb_encode(&stream,Config_fields,&config)&&stream.bytes_written==size,"real encode length");return bytes;
}
static void write_observer() {
    require(std::memcmp(&live,prior_live,sizeof(live))==0,"actual SaveConfig observed premature live publication");
    ++observed_writes;
}
static Bytes packet(const Bytes &body) {
    static InputState inputs{};VectorStream stream;
    stream.input={static_cast<uint8_t>(CMD_SET_CONFIG)};stream.input.insert(stream.input.end(),body.begin(),body.end());
    ConfiguratorBackend backend(inputs,nullptr,0,live,stream);backend.SendReport();return stream.output;
}
static void check(const std::string &label,const Bytes &body,bool success,
                  const std::string &text="",bool includes_nul=false,bool fail_open=false) {
    std::memcpy(prior_live,&live,sizeof(live));
    const Bytes old_file=*LittleFS.bytes;const unsigned write_opens=LittleFS.write_opens;
    const size_t write_before=observed_writes;
    LittleFS.faults.write_observer=write_observer;
    LittleFS.write_open_ok=!fail_open;
    const Bytes response=packet(body);
    LittleFS.write_open_ok=true;
    Bytes expected{static_cast<uint8_t>(success?CMD_SUCCESS:CMD_ERROR)};
    if(!success) {expected.insert(expected.end(),text.begin(),text.end());if(includes_nul)expected.push_back(0);}
    if(response!=expected) {
        std::cerr<<label<<" actual_packet=";
        for(uint8_t b:response)std::cerr<<unsigned(b)<<',';
        std::cerr<<" expected_text="<<text<<" expected_nul="<<includes_nul<<'\n';
    }
    require(response==expected,label+": exact command/error packet bytes and length");
    if(success) {
        require(observed_writes>write_before&&LittleFS.write_opens==write_opens+1,label+": real save writes missing");
        reloaded=Config_init_default;
        require(persistence.LoadConfigChecked(reloaded)==Persistence::LoadResult::Loaded,label+": real saved file reload");
        require(encode(reloaded)==encode(live),label+": saved/live roundtrip mismatch");
        // Body may contain repeated singular fields; independent actual buffer
        // decode gives the whole accepted Config for comparison below.
        static Config expected_config;expected_config=Config_init_default;
        auto stream=pb_istream_from_buffer(body.data(),body.size());
        require(pb_decode(&stream,Config_fields,&expected_config)&&stream.bytes_left==0,label+": independent actual decode");
        require(encode(expected_config)==encode(live),label+": wrong published candidate");
        ++successes;
    } else {
        require(std::memcmp(&live,prior_live,sizeof(live))==0,label+": full live object changed");
        require(*LittleFS.bytes==old_file,label+": stored bytes changed");
        require(observed_writes==write_before,label+": actual writer reached rejection");
        require(LittleFS.write_opens==write_opens+(fail_open?1:0),label+": unexpected save open");
        ++errors;
    }
    ++cases;
    std::cout<<"set_case="<<label<<" command="<<(success?"CMD_SUCCESS":"CMD_ERROR")
             <<" payload_length="<<response.size()-1<<" nul="<<includes_nul
             <<" live="<<(success?"PUBLISHED_AFTER_REAL_SAVE":"BYTE_EXACT")
             <<" stored="<<(success?"REAL_RELOAD_EQUAL":"BYTE_EXACT")
             <<" write_calls="<<observed_writes-write_before<<" PASS\n";
}
static void candidate_check(const std::string &label,bool valid,const std::string &error="",bool nul=false) {
    check(label,encode(candidate),valid,error,nul);
}
static std::vector<uint32_t> unique(std::initializer_list<uint32_t> input) {
    std::vector<uint32_t> result;
    for(uint32_t x:input) {bool found=false;for(uint32_t old:result)found|=old==x;if(!found)result.push_back(x);}
    return result;
}
static Bytes varint(uint64_t n) {
    Bytes b;do {uint8_t v=n&127;n>>=7;b.push_back(v|(n?128:0));}while(n);return b;
}
static void append(Bytes &a,const Bytes &b) {a.insert(a.end(),b.begin(),b.end());}
static Bytes scalar(unsigned tag,uint64_t n) {Bytes b=varint(uint64_t(tag)<<3);append(b,varint(n));return b;}
static Bytes message(unsigned tag,const Bytes &body) {
    Bytes b=varint((uint64_t(tag)<<3)|2);append(b,varint(body.size()));append(b,body);return b;
}

static void references() {
    for(size_t count:{size_t(0),size_t(1),size_t(15)})
        for(uint32_t ref:unique({0,1,uint32_t(count),uint32_t(count+1),255})) {
            reset_candidate();candidate.communication_backend_configs_count=count;candidate.default_backend_config=ref;
            const bool valid=ref<=count;
            candidate_check("default_backend/"+std::to_string(count)+"/"+std::to_string(ref),valid,
                valid?"":"Default backend ID is "+std::to_string(ref)+" but only "+std::to_string(count)+" backend configs are defined");++reference_cases;
        }
    for(bool last:{false,true}) {
        const size_t g=last?29:0,b=last?14:0;const std::string game=std::to_string(g+1),backend=std::to_string(b+1);
        for(size_t count:{size_t(0),size_t(1),size_t(30)})
            for(uint32_t ref:unique({0,1,uint32_t(count),uint32_t(count+1),255})) {
                reset_candidate();candidate.game_mode_configs_count=count;candidate.communication_backend_configs[b].default_mode_config=ref;
                const bool valid=ref<=count;
                candidate_check("backend_mode/"+backend+"/"+std::to_string(count)+"/"+std::to_string(ref),valid,
                    valid?"":"Default mode ID is "+std::to_string(ref)+" for backend "+backend+" but only "+std::to_string(count)+" modes are defined");++reference_cases;
            }
        for(size_t count:{size_t(0),size_t(1),size_t(10)})
            for(GameModeId mode:{MODE_UNSPECIFIED,MODE_MELEE,MODE_PROJECT_M,MODE_ULTIMATE,MODE_FGC,
                MODE_RIVALS_OF_AETHER,MODE_KEYBOARD,MODE_CUSTOM,MODE_64,MODE_RIVALS2,MODE_NUM_VALUES}) {
                for(uint32_t ref:unique({0,1,uint32_t(count),uint32_t(count+1),255})) {
                    reset_candidate();candidate.keyboard_modes_count=count;auto &row=candidate.game_mode_configs[g];row.mode_id=mode;row.keyboard_mode_config=ref;
                    const bool wrong=ref>0&&mode!=MODE_KEYBOARD,valid=!wrong&&ref<=count;
                    const std::string error=wrong?"keyboard_mode_id is set for game mode "+game+" but mode_id is not MODE_KEYBOARD"
                        :"Keyboard mode ID "+std::to_string(ref)+" is for game mode "+game+" but only "+std::to_string(count)+" keyboard modes are defined";
                    candidate_check("keyboard/"+game+"/"+std::to_string(mode)+"/"+std::to_string(count)+"/"+std::to_string(ref),valid,valid?"":error);++reference_cases;
                }
                for(uint32_t ref:unique({0,1,uint32_t(count),uint32_t(count+1),255,256,257,65536,std::numeric_limits<uint32_t>::max()})) {
                    reset_candidate();candidate.custom_modes_count=count;auto &row=candidate.game_mode_configs[g];row.mode_id=mode;row.custom_mode_config=ref;
                    const bool wrong=ref>0&&mode!=MODE_CUSTOM,valid=!wrong&&ref<=count;
                    const std::string error=wrong?"custom_mode_id is set for game mode "+game+" but mode_id is not MODE_CUSTOM"
                        :"Custom mode ID "+std::to_string(ref)+" is for game mode config "+game+" but only "+std::to_string(count)+" custom modes are defined";
                    candidate_check("custom32/"+game+"/"+std::to_string(mode)+"/"+std::to_string(count)+"/"+std::to_string(ref),valid,valid?"":error);++reference_cases;
                }
            }
    }
}
static void error_order() {
    const std::string binding="Config contains an invalid button binding";
    for(bool last:{false,true}) {
        const size_t g=last?29:0,b=last?14:0;const std::string game=std::to_string(g+1),backend=std::to_string(b+1);
        reset_candidate();candidate.default_backend_config=16;candidate.game_mode_configs[g].activation_binding_count=1;candidate.game_mode_configs[g].activation_binding[0]=BTN_UNSPECIFIED;
        candidate_check("order/binding_before_default/"+game,false,binding,true);++order_cases;
        reset_candidate();candidate.default_backend_config=16;candidate.communication_backend_configs[b].default_mode_config=31;
        candidate_check("order/default_before_backend_mode/"+game,false,"Default backend ID is 16 but only 15 backend configs are defined");++order_cases;
        reset_candidate();candidate.communication_backend_configs[b].default_mode_config=31;candidate.game_mode_configs[g].keyboard_mode_config=1;
        candidate_check("order/backend_mode_before_game/"+game,false,"Default mode ID is 31 for backend "+backend+" but only 30 modes are defined");++order_cases;
        reset_candidate();candidate.game_mode_configs[g].keyboard_mode_config=11;candidate.game_mode_configs[g].custom_mode_config=256;
        candidate_check("order/keyboard_condition_before_custom/"+game,false,"keyboard_mode_id is set for game mode "+game+" but mode_id is not MODE_KEYBOARD");++order_cases;
        reset_candidate();candidate.game_mode_configs[g].mode_id=MODE_KEYBOARD;candidate.game_mode_configs[g].keyboard_mode_config=11;candidate.game_mode_configs[g].custom_mode_config=256;
        candidate_check("order/custom_condition_before_keyboard_bound/"+game,false,"custom_mode_id is set for game mode "+game+" but mode_id is not MODE_CUSTOM");++order_cases;
        reset_candidate();candidate.game_mode_configs[0].mode_id=MODE_CUSTOM;candidate.game_mode_configs[0].custom_mode_config=11;candidate.game_mode_configs[29].keyboard_mode_config=1;
        candidate_check("order/earlier_game_first/"+game,false,"Custom mode ID 11 is for game mode config 1 but only 10 custom modes are defined");++order_cases;
        reset_candidate();candidate.communication_backend_configs[0].default_mode_config=31;candidate.communication_backend_configs[14].default_mode_config=32;
        candidate_check("order/earlier_backend_first/"+game,false,"Default mode ID is 31 for backend 1 but only 30 modes are defined");++order_cases;
    }
    // Current caller integration includes actual wire and final nested binding rejection;
    // the unchanged020 and semantic/Persistence suites cover all12 classes.
    for(unsigned tag:{5U}) {
        check("binding/actual_wire_raw61",message(1,scalar(tag,61)),false,binding,true);++order_cases;
    }
    reset_candidate();candidate.custom_modes[9].modifiers_count=20;candidate.custom_modes[9].modifiers[19].buttons_count=3;
    for(auto &button:candidate.custom_modes[9].modifiers[19].buttons)button=BTN_LF1;
    candidate.custom_modes[9].modifiers[19].buttons[2]=BTN_UNSPECIFIED;
    candidate_check("binding/last_nested_modifier_zero",false,binding,true);++order_cases;
}
static void malformed() {
    // Expected decoder reasons are fixed actual Nanopb contract words.
    const Bytes good=encode(valid_config());Bytes bad=good;bad.push_back(0x80);
    check("decode/partial_then_truncated_varint",bad,false,"Failed to decode config: io error");++decode_cases;
    bad=good;append(bad,varint((uint64_t(500)<<3)|7));
    check("decode/invalid_unknown_wiretype",bad,false,"Failed to decode config: invalid wire_type");++decode_cases;
    bad=good;append(bad,varint((uint64_t(500)<<3)|0));bad.insert(bad.end(),11,0x80);
    check("decode/unterminated_unknown_varint",bad,false,"Failed to decode config: io error");++decode_cases;
    bad=varint(uint64_t(Config_default_backend_config_tag)<<3);bad.insert(bad.end(),11,0x80);
    check("decode/known_overlong_varint",bad,false,"Failed to decode config: varint overflow");++decode_cases;
    bad=good;append(bad,varint((uint64_t(1)<<3)|2));append(bad,varint(16));bad.push_back(8);
    check("decode/truncated_repeated_submessage",bad,false,"Failed to decode config: io error");++decode_cases;
    check("decode/wrong_known_wiretype",message(Config_default_backend_config_tag,Bytes{1}),false,"Failed to decode config: wrong wire type");++decode_cases;
    for(unsigned tag:{Config_default_backend_config_tag,Config_default_usb_backend_config_tag,Config_rgb_brightness_tag}) {
        check("decode/uint8_top_overflow_"+std::to_string(tag),scalar(tag,256),false,"Failed to decode config: integer too large");++decode_cases;
    }
    check("decode/uint8_keyboard_overflow",message(1,scalar(GameModeConfig_keyboard_mode_config_tag,256)),false,"Failed to decode config: integer too large");++decode_cases;
    check("decode/uint8_backend_mode_overflow",message(2,scalar(CommunicationBackendConfig_default_mode_config_tag,256)),false,"Failed to decode config: integer too large");++decode_cases;
    for(uint64_t ref:{uint64_t(4294967296ULL),std::numeric_limits<uint64_t>::max()}) {
        check("decode/uint32_custom_overflow_"+std::to_string(ref),message(1,scalar(GameModeConfig_custom_mode_config_tag,ref)),false,"Failed to decode config: integer too large");++decode_cases;
    }
    Bytes excessive;for(unsigned i=0;i<31;++i)append(excessive,message(1,{}));
    check("decode/game_array_overflow",excessive,false,"Failed to decode config: array overflow");++decode_cases;
    // After partial/error decoding, an empty packet must reset every private field.
    check("decode/empty_after_malformed_private_reset",{},true);++decode_cases;
    Bytes repeated=scalar(Config_default_backend_config_tag,255);append(repeated,scalar(Config_default_backend_config_tag,0));
    check("decode/repeated_singular_last_zero",repeated,true);++decode_cases;
    repeated=scalar(Config_default_backend_config_tag,0);append(repeated,scalar(Config_default_backend_config_tag,1));
    check("decode/repeated_singular_last_invalid",repeated,false,"Default backend ID is 1 but only 0 backend configs are defined");++decode_cases;
}
static void valid_controls() {
    reset_candidate();candidate_check("valid/all_zero_refs",true);++controls;
    candidate=Config_init_default;candidate_check("valid/all_zero_counts",true);++controls;
    reset_candidate();auto &mode=candidate.game_mode_configs[12];mode.button_remapping_count=3;
    mode.button_remapping[0]=ButtonRemap{BTN_RF3,BTN_LT1};mode.button_remapping[1]=ButtonRemap{BTN_RF4,BTN_LT2};mode.button_remapping[2]=ButtonRemap{BTN_LT3,BTN_LT3};
    candidate_check("valid/qualified_three_remaps",true);++controls;
    mode.button_remapping[0].activates=mode.button_remapping[1].activates=mode.button_remapping[2].activates=BTN_UNSPECIFIED;
    candidate_check("valid/remap_disable_zero",true);++controls;
    candidate=valid_config();candidate.game_mode_configs[0].custom_mode_config=0;
    check("save/write_open_failure_prior_file_preserved",encode(candidate),false,"Failed to save config to memory",true,true);++controls;
    candidate_check("save/success_after_failed_open",true);++controls;
    reset_candidate();candidate.default_usb_backend_config=255;
    candidate_check("valid/usb_reference_policy_unchanged",true);++controls;
}

static void rgb_cases() {
 const std::string error="Config contains an invalid RGB target";
 for(unsigned raw=0;raw<256;++raw) {
  bool allowed=(raw>=1&&raw<=8)||(raw>=17&&raw<=38)||(raw>=41&&raw<=45)||raw==49;
  check("rgb/domain/"+std::to_string(raw),message(5,message(1,scalar(1,raw))),allowed,allowed?"":error,!allowed);
 }
 for(uint64_t raw:{uint64_t(256),uint64_t(257),uint64_t(300),uint64_t(4294967295ULL),std::numeric_limits<uint64_t>::max()}) {
  bool overflow=sizeof(Button)==1||raw>UINT32_MAX;
  check("rgb/raw_boundary/"+std::to_string(raw),message(5,message(1,scalar(1,raw))),false,
        overflow?"Failed to decode config: integer too large":error,!overflow);
 }
 for(bool last:{false,true})for(size_t n:{size_t(0),size_t(60),size_t(61)}) {
  Bytes colors;for(size_t i=0;i<n;++i)append(colors,message(1,scalar(1,1)));
  Bytes body;for(size_t i=0;i<(last?29:0);++i)append(body,message(5,{}));append(body,message(5,colors));
  check("rgb/decoded_count/"+std::to_string(last)+"/"+std::to_string(n),body,n<=60,n<=60?"":"Failed to decode config: array overflow");
  if(n==60){colors.clear();for(size_t i=0;i<60;++i)append(colors,message(1,scalar(1,i==59?0:1)));body.clear();for(size_t i=0;i<(last?29:0);++i)append(body,message(5,{}));append(body,message(5,colors));check("rgb/last_populated_zero",body,false,error,true);}
 }
 reset_candidate();candidate.rgb_configs_count=1;auto &rgb=candidate.rgb_configs[0];rgb.button_colors_count=20;
 for(size_t i=0;i<11;++i)rgb.button_colors[i]={BTN_LF1,2282478};candidate_check("rgb/legacy20_nine_zero",false,error,true);
 rgb.button_colors_count=11;rgb.button_colors[0].color=0;candidate_check("rgb/corrected11_LF1black",true);
}

int main(int argc,char **argv) {
    try {
        require(persistence.IsAvailable(),"global mount available");
        live=valid_config();live.game_mode_configs[0].custom_mode_config=2;
        LittleFS.bytes=std::make_shared<Bytes>(Bytes{1,2,3});
        if(argc==2&&std::string(argv[1])=="--missing-callback") {
            require(!persistence.SetValidator(nullptr),"null callback rejected");
            check("callback/fresh_process_missing_shared_callback",encode(valid_config()),false,"Config validator is not installed",true);
            require(LittleFS.format_calls==0&&!LittleFS.saw_auto_format_true,"no format");
            std::cout<<"set_missing_callback cases="<<cases<<" live=BYTE_EXACT stored=BYTE_EXACT PASS\n";return 0;
        }
        require(argc==1,"unknown harness argument");
        require(persistence.SetValidator(validate_glyph_config),"shared validator installed");
        rgb_cases();references();error_order();malformed();valid_controls();
        require(LittleFS.format_calls==0&&!LittleFS.saw_auto_format_true,"no formatter");
        std::cout<<"set_matrix references="<<reference_cases<<" order_and_binding="<<order_cases<<" decoder="<<decode_cases
                 <<" controls="<<controls<<" errors="<<errors<<" successes="<<successes<<" observed_save_writes="<<observed_writes
                 <<" total="<<cases<<" button_width="<<sizeof(Button)<<" actual_cobs_wire=NOT_TESTED PASS\n";
        std::cout<<"case=literal_set_fullwidth_reference_errors_transactional PASS\n"
                 <<"case=literal_set_save_failure_no_publication PASS\n"
                 <<"case=literal_set_save_then_publish_real_roundtrip PASS\n";return 0;
    } catch(const std::exception &error) {std::cerr<<"FAIL: "<<error.what()<<'\n';return 1;}
}
