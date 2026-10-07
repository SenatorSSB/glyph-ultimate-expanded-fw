#include <algorithm>
#include <cstdint>
#include <cstring>
#include <functional>
#include <iostream>
#include <iterator>
#include <limits>
#include <stdexcept>
#include <string>
#include <vector>
#include <LittleFS.h>
#include <CRC32.h>
#include <pb_encode.h>
#include <pb_decode.h>
#include <config.pb.h>
#include "core/Persistence.hpp"
#include "core/config_validation.hpp"

using Bytes = std::vector<uint8_t>;
using Result = Persistence::LoadResult;
static size_t cases = 0, recoveries = 0, decoder_extents = 0;
static unsigned callback_calls = 0;
static Config caller, expected_config, valid;
static void require(bool condition, const std::string &message) {
    if (!condition) throw std::runtime_error(message);
}
static bool counted_validator(const Config &config, ConfigValidationError &error) {
    ++callback_calls;
    return validate_config_semantics(config, error);
}
static bool other_validator(const Config &config, ConfigValidationError &error) {
    return validate_config_semantics(config, error);
}
static Config valid_config() {
    Config config = Config_init_default;
    config.game_mode_configs_count = 1;
    config.game_mode_configs[0].mode_id = MODE_CUSTOM;
    config.game_mode_configs[0].custom_mode_config = 1;
    config.custom_modes_count = 10;
    return config;
}
static Bytes encode(const Config &config) {
    size_t size = 0;
    require(pb_get_encoded_size(&size, Config_fields, &config), "real encoded size");
    Bytes bytes(size);
    auto stream = pb_ostream_from_buffer(bytes.data(), bytes.size());
    require(pb_encode(&stream, Config_fields, &config), "real nanopb encode");
    require(stream.bytes_written == size, "encoded length exact");
    return bytes;
}
static Bytes file_for(const Bytes &body) {
    CRC32 crc; crc.update(body.data(), body.size());
    Persistence::ConfigHeader header{};
    header.config_size = body.size(); header.config_crc = crc.finalize();
    Bytes bytes(sizeof(header) + body.size());
    std::memcpy(bytes.data(), &header, sizeof(header));
    if (!body.empty()) std::memcpy(bytes.data() + sizeof(header), body.data(), body.size());
    return bytes;
}
static void install_file(const Bytes &file) {
    LittleFS.bytes = std::make_shared<Bytes>(file);
}
static void emit(const std::string &label, Result result) {
    ++cases;
    const char *name = result == Result::Loaded ? "Loaded" : result == Result::Rejected ? "Rejected"
        : result == Result::StorageFailure ? "StorageFailure" : "Absent";
    std::cout << "persistence_case=" << label << " result=" << name
              << " stored=BYTE_EXACT writes=0 PASS\n";
}
static void accepted(const std::string &label, const Bytes &body) {
    install_file(file_for(body));
    const Bytes before = *LittleFS.bytes;
    const unsigned writes = LittleFS.write_opens;
    // Decode the expected object using the same authenticated real decoder
    // through its ordinary buffer stream, independently of File callbacks.
    expected_config = Config_init_default;
    auto stream = pb_istream_from_buffer(body.data(), body.size());
    require(pb_decode(&stream, Config_fields, &expected_config), label + ": independent decode");
    require(stream.bytes_left == 0, label + ": independent full decode");
    std::memset(&caller, 0x6d, sizeof(caller));
    require(persistence.LoadConfigChecked(caller) == Result::Loaded, label + ": load verdict");
    require(encode(caller) == encode(expected_config), label + ": accepted whole encoded Config");
    require(*LittleFS.bytes == before && LittleFS.write_opens == writes, label + ": load rewrote file");
    emit(label, Result::Loaded);
}
static void recover(const std::string &after) {
    LittleFS.faults = HostFileFaults{};
    LittleFS.read_open_ok = LittleFS.write_open_ok = true;
    LittleFS.set_config_ok = LittleFS.begin_ok = LittleFS.mounted = true;
    // Alternate rich and empty input. Empty must not inherit any private
    // candidate fields from a preceding partial/repeated decode.
    const Bytes body = recoveries % 2 ? encode(valid) : Bytes{};
    accepted("recovery_after/" + after, body); ++recoveries;
}
static void rejected(const std::string &label, const Bytes &file, Result result,
                     bool recover_after = true) {
    install_file(file);
    std::memset(&caller, 0x6d, sizeof(caller));
    unsigned char previous[sizeof(Config)]; std::memcpy(previous, &caller, sizeof(caller));
    const Bytes before = *LittleFS.bytes; const unsigned writes = LittleFS.write_opens;
    require(persistence.LoadConfigChecked(caller) == result, label + ": bounded result");
    require(std::memcmp(&caller, previous, sizeof(caller)) == 0, label + ": caller changed");
    require(*LittleFS.bytes == before && LittleFS.write_opens == writes, label + ": file/writer changed");
    if (LittleFS.faults.decoder_block_read_negative ||
        LittleFS.faults.decoder_read_cutoff != std::numeric_limits<size_t>::max()) {
        require(LittleFS.faults.seek_calls == 2 && LittleFS.faults.position_calls == 1 &&
                LittleFS.faults.size_calls == 3, label + ": did not reach postCRC decoder phase");
        std::cout << "io_stage=POST_CRC_DECODER header_and_crc=PASSED seek_calls=2 PASS\n";
    }
    emit(label, result);
    if (recover_after) recover(label);
}
static void crc_valid_rejected(const std::string &label, const Bytes &body) {
    install_file(file_for(body));
    require(persistence.CheckSavedConfig(), label + ": recomputed CRC/header must pass before decoder");
    rejected(label, *LittleFS.bytes, Result::Rejected);
}
static Bytes varint(uint64_t number) {
    Bytes bytes;
    do { uint8_t byte = number & 0x7f; number >>= 7; bytes.push_back(byte | (number ? 0x80 : 0)); } while (number);
    return bytes;
}
static void append(Bytes &to, const Bytes &from) { to.insert(to.end(), from.begin(), from.end()); }
static Bytes scalar(unsigned tag, uint64_t number) {
    Bytes bytes = varint(uint64_t(tag) << 3); append(bytes, varint(number)); return bytes;
}
static Bytes message(unsigned tag, const Bytes &body) {
    Bytes bytes = varint((uint64_t(tag) << 3) | 2); append(bytes, varint(body.size())); append(bytes, body); return bytes;
}
static Bytes repeated(unsigned tag, size_t count, const Bytes &body) {
    Bytes bytes; for (size_t i = 0; i < count; ++i) append(bytes, message(tag, body)); return bytes;
}
static Bytes packed(unsigned tag, size_t count, uint64_t number = 1) {
    Bytes body; for (size_t i = 0; i < count; ++i) append(body, varint(number)); return message(tag, body);
}
static Bytes child(unsigned tag, size_t count, const Bytes &last) {
    Bytes bytes = repeated(tag, count-1, {}); append(bytes, message(tag, last)); return bytes;
}

static void decoder_payloads() {
    const Bytes base = encode(valid);
    Bytes bad = base; bad.push_back(0x80); crc_valid_rejected("decoder/partial_valid_then_truncated_tag", bad);
    bad = base; append(bad, varint((uint64_t(500)<<3)|7)); crc_valid_rejected("decoder/invalid_unknown_wire_type", bad);
    bad = base; append(bad, varint((uint64_t(500)<<3)|0)); bad.insert(bad.end(), 11, 0x80);
    crc_valid_rejected("decoder/overlong_varint", bad);
    bad = base; append(bad, varint((uint64_t(1)<<3)|2)); append(bad, varint(16)); bad.push_back(8);
    crc_valid_rejected("decoder/partial_repeated_submessage_truncated", bad);
    bad = message(Config_default_backend_config_tag, Bytes{1}); crc_valid_rejected("decoder/known_wrong_wire_type", bad);
    bad = base; bad.pop_back(); crc_valid_rejected("decoder/truncated_actual_encoded_payload", bad);
    for (unsigned tag : {Config_default_backend_config_tag, Config_default_usb_backend_config_tag, Config_rgb_brightness_tag})
        crc_valid_rejected("decoder/uint8_top_overflow_"+std::to_string(tag), scalar(tag,256));
    crc_valid_rejected("decoder/uint8_keyboard_reference_overflow", message(1,scalar(GameModeConfig_keyboard_mode_config_tag,256)));
    crc_valid_rejected("decoder/uint8_backend_mode_reference_overflow", message(2,scalar(CommunicationBackendConfig_default_mode_config_tag,256)));
    crc_valid_rejected("decoder/uint8_rgb_speed_overflow", message(5,scalar(RgbConfig_speed_tag,256)));
    for (uint64_t reference : {uint64_t(4294967296ULL), std::numeric_limits<uint64_t>::max()})
        crc_valid_rejected("decoder/uint32_custom_overflow_"+std::to_string(reference),
            message(1,scalar(GameModeConfig_custom_mode_config_tag,reference)));
    // A real decoder must preserve repeated singular-field last-value semantics.
    Bytes duplicate = scalar(Config_default_backend_config_tag,255); append(duplicate,scalar(Config_default_backend_config_tag,0));
    accepted("decoder/repeated_singular_last_zero", duplicate);
    duplicate = scalar(Config_default_backend_config_tag,0); append(duplicate,scalar(Config_default_backend_config_tag,1));
    crc_valid_rejected("decoder/repeated_singular_last_invalid", duplicate);
    Bytes refs = scalar(GameModeConfig_mode_id_tag, MODE_CUSTOM);
    append(refs,scalar(GameModeConfig_custom_mode_config_tag,256)); append(refs,scalar(GameModeConfig_custom_mode_config_tag,0));
    accepted("decoder/repeated_custom32_last_zero", message(1,refs));
    refs = scalar(GameModeConfig_mode_id_tag, MODE_CUSTOM); append(refs,scalar(GameModeConfig_custom_mode_config_tag,0));
    append(refs,scalar(GameModeConfig_custom_mode_config_tag,256));
    crc_valid_rejected("decoder/repeated_custom32_last_256", message(1,refs));
    for (size_t length : {size_t(0),size_t(1),size_t(31),size_t(32),size_t(33),size_t(100),size_t(257)}) {
        Bytes unknown = base; append(unknown,message(500,Bytes(length,0xa7)));
        accepted("decoder/unknown_length_nullskip_"+std::to_string(length), unknown);
    }
    Bytes unknown = base; append(unknown,scalar(500,std::numeric_limits<uint64_t>::max()));
    append(unknown,varint((uint64_t(501)<<3)|5)); append(unknown,Bytes(4,0x6e));
    append(unknown,varint((uint64_t(502)<<3)|1)); append(unknown,Bytes(8,0x9c));
    accepted("decoder/unknown_varint_fixed32_fixed64", unknown);
}

struct ExtentWire {
    const char *name; size_t capacity; bool nested;
    std::function<Bytes(size_t,bool)> wire;
};
static void wire_extents() {
    const Bytes pair = [] { Bytes b=scalar(1,1);append(b,scalar(2,17));return b; }();
    const ExtentWire fields[] = {
        {"top.game",30,false,[](size_t n,bool){return repeated(1,n,{});}},
        {"top.backend",15,false,[](size_t n,bool){return repeated(2,n,{});}},
        {"top.custom",10,false,[](size_t n,bool){return repeated(3,n,{});}},
        {"top.keyboard",10,false,[](size_t n,bool){return repeated(4,n,{});}},
        {"top.rgb",30,false,[](size_t n,bool){return repeated(5,n,{});}},
        {"game.socd",10,true,[pair](size_t n,bool last){return child(1,last?30:1,repeated(3,n,pair));}},
        {"game.remap",60,true,[pair](size_t n,bool last){return child(1,last?30:1,repeated(4,n,pair));}},
        {"game.activation",4,true,[](size_t n,bool last){return child(1,last?30:1,packed(5,n));}},
        {"game.applicable_backends",15,true,[](size_t n,bool last){return child(1,last?30:1,packed(201,n));}},
        {"game.menu_icon",7,true,[](size_t n,bool last){return child(1,last?30:1,packed(202,n));}},
        {"backend.activation",2,true,[](size_t n,bool last){return child(2,last?15:1,packed(3,n));}},
        {"custom.digital",18,true,[](size_t n,bool last){return child(3,last?10:1,packed(2,n));}},
        {"custom.stick",8,true,[](size_t n,bool last){return child(3,last?10:1,packed(3,n));}},
        {"custom.triggers",4,true,[](size_t n,bool last){return child(3,last?10:1,repeated(4,n,scalar(1,1)));}},
        {"custom.modifiers",20,true,[](size_t n,bool last){return child(3,last?10:1,repeated(5,n,{}));}},
        {"custom.combos",5,true,[](size_t n,bool last){return child(3,last?10:1,repeated(7,n,{}));}},
        {"modifier.buttons",3,true,[](size_t n,bool last){return child(3,last?10:1,child(5,last?20:1,packed(1,n)));}},
        {"combo.buttons",3,true,[](size_t n,bool last){return child(3,last?10:1,child(7,last?5:1,packed(1,n)));}},
        {"keyboard.keys",60,true,[](size_t n,bool last){return child(4,last?10:1,repeated(2,n,scalar(1,1)));}},
        {"rgb.colors",60,true,[](size_t n,bool last){return child(5,last?30:1,repeated(1,n,{}));}},
    };
    require(std::size(fields)==20,"complete generated decoder extent inventory");
    for (const auto &field:fields) for (bool last:{false,true}) {
        if (last&&!field.nested) continue;
        for (size_t count:{size_t(0),field.capacity,field.capacity+1}) {
            const std::string label=std::string("decoder_extent/")+field.name+(last?"/last/":"/first/")+std::to_string(count);
            const Bytes body=field.wire(count,last);
            if(count>field.capacity) crc_valid_rejected(label,body); else accepted(label,body);
            ++decoder_extents;
        }
    }
}

static void decoded_binding_leaves() {
    const auto list = [](unsigned tag,size_t count) {
        Bytes body; for(size_t i=0;i<count;++i) append(body,varint(i+1==count?61:1));
        return message(tag,body);
    };
    const auto pair = [](bool invalid_first) {
        Bytes body=scalar(1,invalid_first?61:1);append(body,scalar(2,invalid_first?17:61));return body;
    };
    for(bool last:{false,true}) {
        const std::string position=last?"last":"first";
        const size_t game=last?30:1,backend=last?15:1,custom=last?10:1,keyboard=last?10:1;
        crc_valid_rejected("binding_leaf/game.activation/"+position,child(1,game,list(5,last?4:1)));
        Bytes remap_valid=scalar(1,1);append(remap_valid,scalar(2,17));
        Bytes remaps=repeated(4,last?59:0,remap_valid);append(remaps,message(4,pair(true)));
        crc_valid_rejected("binding_leaf/game.remap.physical/"+position,child(1,game,remaps));
        remaps=repeated(4,last?59:0,remap_valid);append(remaps,message(4,pair(false)));
        crc_valid_rejected("binding_leaf/game.remap.activates/"+position,child(1,game,remaps));
        // Prior remap/SOCD elements must themselves have valid buttons.
        Bytes valid_pair=scalar(1,1);append(valid_pair,scalar(2,17));
        for(bool first:{true,false}) {
            Bytes nested=repeated(3,last?9:0,valid_pair);append(nested,message(3,pair(first)));
            crc_valid_rejected("binding_leaf/game.socd."+std::string(first?"dir1/":"dir2/")+position,child(1,game,nested));
        }
        crc_valid_rejected("binding_leaf/backend.activation/"+position,child(2,backend,list(3,last?2:1)));
        crc_valid_rejected("binding_leaf/custom.digital/"+position,child(3,custom,list(2,last?18:1)));
        crc_valid_rejected("binding_leaf/custom.stick/"+position,child(3,custom,list(3,last?8:1)));
        crc_valid_rejected("binding_leaf/custom.modifier/"+position,child(3,custom,child(5,last?20:1,list(1,last?3:1))));
        crc_valid_rejected("binding_leaf/custom.combo/"+position,child(3,custom,child(7,last?5:1,list(1,last?3:1))));
        Bytes triggers=repeated(4,last?3:0,scalar(1,1));append(triggers,message(4,scalar(1,61)));
        crc_valid_rejected("binding_leaf/custom.trigger/"+position,child(3,custom,triggers));
        Bytes keys=repeated(2,last?59:0,scalar(1,1));append(keys,message(2,scalar(1,61)));
        crc_valid_rejected("binding_leaf/keyboard.key/"+position,child(4,keyboard,keys));
        Bytes remap=scalar(1,1);append(remap,scalar(2,0));
        accepted("binding_leaf/remap_disable_control/"+position,child(1,game,repeated(4,last?60:1,remap)));
    }
}

static void semantic_rejections() {
    for (uint32_t reference:{uint32_t(11),uint32_t(255),uint32_t(256),uint32_t(257),uint32_t(65536),std::numeric_limits<uint32_t>::max()}) {
        static Config invalid; invalid=valid; invalid.game_mode_configs[0].custom_mode_config=reference;
        crc_valid_rejected("semantic/custom_full32_"+std::to_string(reference),encode(invalid));
        invalid.game_mode_configs[0].mode_id=MODE_ULTIMATE;
        crc_valid_rejected("semantic/custom_wrongmode_full32_"+std::to_string(reference),encode(invalid));
    }
    static Config invalid; invalid=valid; invalid.default_backend_config=1;
    crc_valid_rejected("semantic/default_backend_out_of_count",encode(invalid));
    invalid=valid; invalid.communication_backend_configs_count=1; invalid.communication_backend_configs[0].default_mode_config=2;
    crc_valid_rejected("semantic/default_mode_out_of_count",encode(invalid));
    invalid=valid; invalid.game_mode_configs[0].keyboard_mode_config=1;
    crc_valid_rejected("semantic/keyboard_wrongmode",encode(invalid));
    invalid.game_mode_configs[0].mode_id=MODE_KEYBOARD; invalid.game_mode_configs[0].custom_mode_config=0;
    crc_valid_rejected("semantic/keyboard_out_of_count",encode(invalid));
    invalid=valid; invalid.game_mode_configs[0].activation_binding_count=1;
    invalid.game_mode_configs[0].activation_binding[0]=BTN_UNSPECIFIED;
    crc_valid_rejected("semantic/invalid_button_zero",encode(invalid));
    const Bytes malformed_button=message(1,packed(5,1,61));
    crc_valid_rejected("semantic/real_decoded_invalid_button_61",malformed_button);
}

class Capture : public Print {
public:
    Bytes bytes;
    size_t write(uint8_t byte) override {bytes.push_back(byte);return 1;}
    size_t write(const uint8_t *data,size_t length) override {bytes.insert(bytes.end(),data,data+length);return length;}
};
static void unavailable() {
    for (bool config_failure:{true,false}) {
        LittleFS.faults=HostFileFaults{};
        LittleFS.set_config_ok=!config_failure; LittleFS.begin_ok=config_failure;
        const unsigned configs=LittleFS.set_config_calls,begins=LittleFS.begin_calls,ends=LittleFS.end_calls;
        {
            Persistence instance;
            const std::string label=config_failure?"unavailable/setConfig_false":"unavailable/begin_false";
            require(!instance.IsAvailable(),label+": available unexpectedly");
            require(LittleFS.set_config_calls==configs+1 && LittleFS.begin_calls==begins+(config_failure?0:1),label+": configure/mount sequence");
            require(instance.SetValidator(validate_config_semantics),label+": callback installation");
            ConfigValidationError error; require(instance.ValidateConfig(valid,error),label+": pure callback remains available without FS");
            const unsigned reads=LittleFS.read_opens,writes=LittleFS.write_opens,exists=LittleFS.exists_calls;
            const Bytes before=*LittleFS.bytes;
            std::memset(&caller,0x6d,sizeof(caller));unsigned char prior[sizeof(Config)];std::memcpy(prior,&caller,sizeof(caller));
            Capture output;
            require(instance.LoadConfigChecked(caller)==Result::StorageFailure,label+": load classification");
            require(!instance.LoadConfig(caller)&&!instance.CheckSavedConfig(),label+": bool adapters");
            require(instance.LoadConfigRaw(output)==0 && instance.LoadConfigRaw(output,false)==0,label+": both raw guards");
            require(!instance.SaveConfig(valid),label+": save guard");
            require(std::memcmp(prior,&caller,sizeof(caller))==0,label+": caller changed");
            require(output.bytes.empty()&&*LittleFS.bytes==before,label+": data changed");
            require(LittleFS.read_opens==reads&&LittleFS.write_opens==writes&&LittleFS.exists_calls==exists,label+": FS operation after unavailable");
            emit(label,Result::StorageFailure);
        }
        require(LittleFS.end_calls==ends,"unavailable destructor must not unmount");
        // Restore the disposable host's singleton state only. This is not a
        // firmware remount/recovery path or a real filesystem reinitialization.
        recover(config_failure?"setConfig_false":"begin_false");
    }
}
static void callbacks() {
    {
        Persistence instance;
        require(!instance.SetValidator(nullptr),"missing callback null rejected");
        install_file(file_for(encode(valid)));const unsigned reads=LittleFS.read_opens, writes=LittleFS.write_opens;const Bytes stored=*LittleFS.bytes;
        std::memset(&caller,0x6d,sizeof(caller));unsigned char prior[sizeof(Config)];std::memcpy(prior,&caller,sizeof(caller));
        require(instance.LoadConfigChecked(caller)==Result::StorageFailure,"missing callback fail closed");
        require(!instance.LoadConfig(caller)&&LittleFS.read_opens==reads&&std::memcmp(prior,&caller,sizeof(caller))==0,"missing callback read/publish");
        require(LittleFS.write_opens==writes&&*LittleFS.bytes==stored,"missing callback stored/writer mutation");
        ConfigValidationError error;
        require(!instance.ValidateConfig(valid,error),"missing callback semantic rejection");
        const char text[]="Config validator is not installed";
        require(error.length==sizeof(text)&&std::memcmp(error.message,text,sizeof(text))==0,"missing callback error bytes/NUL");
        require(instance.SetValidator(counted_validator)&&instance.SetValidator(counted_validator),"install/same pointer idempotent");
        require(!instance.SetValidator(other_validator)&&!instance.SetValidator(nullptr),"different/null callback rejected");
        static Config invalid;invalid=valid;invalid.rgb_configs_count=31;callback_calls=0;
        require(!instance.ValidateConfig(invalid,error)&&callback_calls==0,"extents before callback");
        invalid=valid;invalid.game_mode_configs[0].menu_button_icon_count=8;
        require(!instance.ValidateConfig(invalid,error)&&callback_calls==0,"new menu extent before callback");
        invalid=valid;invalid.rgb_configs_count=1;invalid.rgb_configs[0].button_colors_count=61;
        require(!instance.ValidateConfig(invalid,error)&&callback_calls==0,"new RGB extent before callback");
        require(instance.ValidateConfig(valid,error)&&callback_calls==1,"original callback retained");
        require(!instance.SetValidator(other_validator)&&instance.ValidateConfig(valid,error)&&callback_calls==2,"different pointer never installed");
        emit("callback/install_once_missing_different_extent_before_callback",Result::StorageFailure);
    }
    recover("callback_local_scope");
}

static void storage_faults() {
    const Bytes good=file_for(encode(valid));Bytes bad=good;
    bad[sizeof(Persistence::ConfigHeader)]^=1;rejected("header/bad_crc",bad,Result::Rejected);
    for(size_t length:{size_t(0),size_t(1),sizeof(Persistence::ConfigHeader)-1}) {
        bad=good;bad.resize(length);rejected("header/physical_short_"+std::to_string(length),bad,length==0?Result::StorageFailure:Result::Rejected);
    }
    bad=good;bad.pop_back();rejected("header/physical_payload_truncation",bad,Result::Rejected);
    bad=good;bad.push_back(0);rejected("header/extra_physical_byte",bad,Result::Rejected);
    for(size_t length:{size_t(0),size_t(1),std::numeric_limits<size_t>::max()}) {
        bad=good;Persistence::ConfigHeader header;std::memcpy(&header,bad.data(),sizeof(header));header.config_size=length;
        std::memcpy(bad.data(),&header,sizeof(header));rejected("header/declared_length_"+std::to_string(length),bad,Result::Rejected);
    }
    for(size_t reported:{sizeof(Persistence::ConfigHeader)-1,good.size()+1}) {
        LittleFS.faults.reported_size=reported;
        rejected("io/initial_reported_size_"+std::to_string(reported),good,Result::Rejected);
    }
    for(unsigned seek:{1U,2U}) {
        LittleFS.faults.fail_seek_call=seek;rejected("io/seek_call_"+std::to_string(seek),good,Result::StorageFailure);
    }
    LittleFS.faults.read_cutoff=sizeof(Persistence::ConfigHeader)-1;
    rejected("io/short_header_bulk_read",good,Result::StorageFailure);
    LittleFS.faults.read_cutoff=sizeof(Persistence::ConfigHeader)+1;
    rejected("io/crc_pass_short_payload_read",good,Result::StorageFailure);
    LittleFS.faults.decoder_block_read_negative=true;
    rejected("io/postCRC_decoder_block_read_negative",good,Result::StorageFailure);
    LittleFS.faults.decoder_read_cutoff=sizeof(Persistence::ConfigHeader)+1;
    rejected("io/postCRC_decoder_short_bulk_read",good,Result::StorageFailure);
    Bytes unknown=encode(valid);append(unknown,message(500,Bytes(257,0x7c)));
    LittleFS.faults.decoder_read_cutoff=sizeof(Persistence::ConfigHeader)+encode(valid).size()+4+33;
    rejected("io/postCRC_unknown_nullskip_short_read",file_for(unknown),Result::StorageFailure);
    for(unsigned call:{2U,3U,4U}) {
        LittleFS.faults.size_override_call=call;
        LittleFS.faults.size_override_value=call==3?sizeof(Persistence::ConfigHeader)-1:good.size()+1;
        rejected("io/size_inconsistency_call_"+std::to_string(call),good,Result::StorageFailure);
    }
    LittleFS.faults.size_override_call=3;LittleFS.faults.size_override_value=good.size()+1;
    rejected("io/postCRC_size_growth_decoder_short_read",good,Result::StorageFailure);
    for(unsigned call:{1U,2U}) {
        LittleFS.faults.position_override_call=call;LittleFS.faults.position_override_value=good.size()-1;
        rejected("io/position_inconsistency_call_"+std::to_string(call),good,Result::StorageFailure);
    }
    LittleFS.read_open_ok=false;rejected("io/open_failure_uncertain_absence",good,Result::StorageFailure);
    install_file(good);const Bytes before=*LittleFS.bytes;const unsigned writes=LittleFS.write_opens;
    Capture output; require(persistence.CheckSavedConfig(),"valid public CRC adapter");
    require(persistence.LoadConfigRaw(output)==1&&output.bytes==encode(valid),"valid raw payload unchanged");
    Capture unvalidated;require(persistence.LoadConfigRaw(unvalidated,false)==1&&unvalidated.bytes==encode(valid),"unvalidated raw payload unchanged");
    require(persistence.LoadConfig(caller)&&encode(caller)==encode(valid),"valid bool Load adapter");
    require(*LittleFS.bytes==before&&LittleFS.write_opens==writes,"public read adapters wrote file");
    emit("adapters/valid_raw_crc_bool_load",Result::Loaded);
}

int main() {
    try {
        require(LittleFS.set_config_calls==1&&LittleFS.begin_calls==1,"global configure then begin once");
        require(!LittleFS.saw_auto_format_true&&persistence.IsAvailable(),"global noautoformat mounted");
        require(persistence.SetValidator(validate_config_semantics),"stable generic validator installed");
        require(persistence.SetValidator(validate_config_semantics)&&!persistence.SetValidator(nullptr)&&!persistence.SetValidator(other_validator),"global validator install once");
        valid=valid_config();
        require(persistence.SaveConfig(valid),"actual successful save");
        require(*LittleFS.bytes==file_for(encode(valid)),"actual saved header CRC/body equal independent encoding");
        accepted("save_then_load/actual_encoder_crc",encode(valid));
        callbacks();unavailable();decoder_payloads();wire_extents();decoded_binding_leaves();semantic_rejections();storage_faults();
        require(LittleFS.format_calls==0&&!LittleFS.saw_auto_format_true,"no format on every path");
        std::cout<<"persistence_matrix decoder_extent_classes=20 decoder_extent_cases="<<decoder_extents
                 <<" valid_recoveries="<<recoveries<<" total="<<cases<<" button_width="<<sizeof(Button)
                 <<" real_crc_nanopb=YES format_calls=0 PASS\n";
        std::cout<<"case=literal_persistence_valid_real_crc_nanopb PASS\n"
                 <<"case=semantic_crc_header_length_rejection_preserves_bytes PASS\n"
                 <<"case=seek_shortio_open_ambiguity_no_rewrite PASS\n"
                 <<"case=post_failure_valid_reload_private_reset PASS\n";
        return 0;
    } catch(const std::exception &error) {std::cerr<<"FAIL: "<<error.what()<<'\n';return 1;}
}
