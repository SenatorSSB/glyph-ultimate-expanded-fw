#include "glyph_config_validation.hpp"
#include "modes/Ultimate.hpp"
#include "modes/UltimateProfileEvaluator.hpp"
#undef _MODES_ULTIMATE_HPP
#define Ultimate LegacyUltimate
#include "modes/Ultimate.hpp"
#undef Ultimate

#include <pb_decode.h>
#include <algorithm>
#include <cstdio>
#include <cstdlib>
#include <fstream>
#include <iterator>
#include <vector>

namespace {
size_t checks = 0;
void require(bool value, const char *label) {
    if (!value) { std::fprintf(stderr, "FAIL: %s\n", label); std::exit(1); }
}
bool equal(const OutputState &a, const OutputState &b) {
    return a.buttons == b.buttons && std::equal(a.analog_axes, a.analog_axes + 6, b.analog_axes);
}
uint64_t buttons(std::initializer_list<int> tokens) {
    uint64_t result = 0; for (int token : tokens) result |= uint64_t{1} << (token - 1); return result;
}
uint64_t mask_tokens(uint32_t mask, const uint8_t *tokens, size_t count) {
    uint64_t result = 0;
    for (size_t bit = 0; bit < count; ++bit) if (mask & (uint32_t{1} << bit)) result |= uint64_t{1} << (tokens[bit] - 1);
    return result;
}
void compare(Ultimate &actual, LegacyUltimate &oracle, const InputState &input, const char *label) {
    OutputState expected{}, got{};
    // Include untouched click/reserved bits in the complete 32-bit comparison.
    expected.buttons = got.buttons = 0xa0030000;
    actual.UpdateOutputs(input, got, COMMS_BACKEND_XINPUT);
    oracle.UpdateOutputs(input, expected, COMMS_BACKEND_XINPUT);
    if (!equal(expected, got)) {
        std::fprintf(stderr, "%s input=%016llx expected=%08x/%u,%u,%u,%u,%u,%u actual=%08x/%u,%u,%u,%u,%u,%u\n",
            label, static_cast<unsigned long long>(input.buttons), expected.buttons,
            expected.leftStickX,expected.leftStickY,expected.rightStickX,expected.rightStickY,expected.triggerLAnalog,expected.triggerRAnalog,
            got.buttons,got.leftStickX,got.leftStickY,got.rightStickX,got.rightStickY,got.triggerLAnalog,got.triggerRAnalog);
        std::exit(1);
    }
    ++checks;
}
OutputState output(Ultimate &mode, uint64_t pressed) {
    InputState input{}; input.buttons = pressed; OutputState result{};
    mode.UpdateOutputs(input, result, COMMS_BACKEND_XINPUT); return result;
}
UltimateProfileOutputEffect &effect(UltimateProfile &p, int key) {
    for (size_t i = 0; i < p.output_program.effects_count; ++i)
        if (UltimateProfileEvaluator::EffectKey(p.output_program.effects[i]) == key) return p.output_program.effects[i];
    require(false, "fixture effect key exists"); return p.output_program.effects[0];
}
void fixed(UltimateProfileOutputEffect &e, uint8_t x, uint8_t y) {
    e.coordinate_mode = ULTIMATE_COORDINATE_FIXED; e.coordinates_count = 0;
    e.table_id = e.mode_table_id = 0; e.fixed_x = x; e.fixed_y = y;
}
void require_valid(Config &config) {
    ConfigValidationError error{};
    if (!validate_glyph_config(config, error)) { std::fprintf(stderr, "%s\n",error.message); require(false,"profile variation production-valid"); }
}
void variation(Config &config, const UltimateProfile &a, const UltimateProfile &b, uint64_t input,
    const OutputState &expected, const char *label) {
    config.ultimate_profiles[0] = b; require_valid(config);
    Ultimate mode; GameModeConfig mode_config{}; mode_config.mode_id = MODE_ULTIMATE;
    mode.SetConfig(mode_config, &a); const OutputState first = output(mode, input);
    mode.SetConfig(mode_config, &b); const OutputState second = output(mode, input);
    mode.SetConfig(mode_config, &a); const OutputState third = output(mode, input);
    require(equal(second, expected), label);
    require(!equal(first, second), "A/B output difference is observable");
    require(equal(first, third), "A/B/A complete final output isolation");
    checks += 3;
}

void profile_variations(Config &config, const UltimateProfile &a) {
    Ultimate reference; GameModeConfig mc{}; mc.mode_id = MODE_ULTIMATE; reference.SetConfig(mc,&a);
    UltimateProfile b = a;
    uint64_t input = buttons({1,17}); OutputState expected = output(reference,input);
    effect(b,0).digital_clear_mask = 1; effect(b,0).digital_set_mask = 8; effect(b,0).gate_token = 1;
    expected.a = false; expected.y = true;
    variation(config,a,b,input,expected,"digital conditional clear/set controls final carriers");
    b = a; input = buttons({33,32}); expected = output(reference,input);
    effect(b,9).value = 45; effect(b,10).value = 46; expected.triggerLAnalog = 45; expected.triggerRAnalog = 46;
    variation(config,a,b,input,expected,"both trigger values are profile data");
    const uint64_t inputs[] = {0,0,0,buttons({21}),buttons({1,22}),buttons({1,23}),buttons({43,45}),buttons({1,19,45}),buttons({25}),buttons({1,29})};
    const int keys[] = {1,2,3,3,4,5,6,7,8,11};
    for (size_t index = 0; index < 10; ++index) {
        // key 3 with neutral input additionally proves a dormant override does
        // not run merely because it carries different data.
        if (index == 2) continue;
        b = a; input = inputs[index]; expected = output(reference,input);
        const uint8_t x = static_cast<uint8_t>(11+index*2), y = static_cast<uint8_t>(12+index*2);
        fixed(effect(b,keys[index]),x,y);
        if (keys[index] == 2 || keys[index] == 6 || keys[index] == 7) { expected.rightStickX=x; expected.rightStickY=y; }
        else { expected.leftStickX=x; expected.leftStickY=y; }
        if (keys[index] == 8) { expected.rightStickX=x; expected.rightStickY=y; }
        variation(config,a,b,input,expected,"fixed coordinates govern each LS/RS/override/null/center phase");
    }
    b = a; input=buttons({1,29}); expected=output(reference,input);
    effect(b,11).value=0; expected.dpadRight=false; expected.leftStickRight=true;
    expected.leftStickX=a.tables[0].coordinates[5].x; expected.leftStickY=a.tables[0].coordinates[5].y;
    variation(config,a,b,input,expected,"D-pad routing, centering and LS direction suppression are data flags");
    for (uint8_t flag : {uint8_t{1},uint8_t{2},uint8_t{4}}) {
        b=a; expected=output(reference,input); effect(b,11).value=7^flag;
        if(flag==1) expected.dpadRight=false;
        if(flag==2) { expected.leftStickX=a.tables[0].coordinates[5].x; expected.leftStickY=a.tables[0].coordinates[5].y; }
        if(flag==4) expected.leftStickRight=true;
        variation(config,a,b,input,expected,"each D-pad route/center/suppress flag is independently authoritative");
    }
    b=a; input=buttons({1,22,23}); expected=output(reference,buttons({1,22})); effect(b,5).suppress=true;
    // Digital RF7 B remains an independent carrier when its analogue phase is disabled.
    expected.b=true;
    variation(config,a,b,input,expected,"suppressed RF7 exposes earlier RF6 phase in fixed order");
    b=a; input=buttons({1,22}); expected=output(reference,input);
    effect(b,4).table_id=effect(b,4).mode_table_id=2;
    expected.leftStickX=a.tables[2].coordinates[5].x; expected.leftStickY=a.tables[2].coordinates[5].y;
    variation(config,a,b,input,expected,"explicit RF6 table reference is authoritative");
    b=a; input=buttons({44}); expected=output(reference,input);
    auto &right=effect(b,2); right.coordinate_mode=ULTIMATE_COORDINATE_TABLE;
    right.coordinates_count=0; right.table_id=right.mode_table_id=2;
    expected.rightStickX=a.tables[2].coordinates[5].x; expected.rightStickY=a.tables[2].coordinates[5].y;
    variation(config,a,b,input,expected,"RS explicit table coordinates are authoritative");
    b=a; input=buttons({1,43}); expected=output(reference,input);
    effect(b,1).direction_source=ULTIMATE_DIRECTION_SOURCE_C_STICK;
    expected.leftStickX=a.tables[0].coordinates[3].x; expected.leftStickY=a.tables[0].coordinates[3].y;
    variation(config,a,b,input,expected,"LS coordinate direction source is profile data");
    b=a; input=buttons({17}); expected=output(reference,input);
    effect(b,0).digital_clear_mask=1; effect(b,0).digital_set_mask=8;
    effect(b,0).gate_token=1; effect(b,0).gate_inverted=true;
    expected.a=false; expected.y=true;
    variation(config,a,b,input,expected,"inverted routed-token gate is deterministic");
    b=a; input=buttons({33}); expected=output(reference,input);
    effect(b,9).suppress=true; expected.triggerLAnalog=0;
    variation(config,a,b,input,expected,"trigger suppression preserves its independent digital carrier");
    b=a; input=buttons({1,25,43,45}); expected=output(reference,buttons({1,43,45}));
    effect(b,8).suppress=true;
    variation(config,a,b,input,expected,"analogue-null suppression exposes earlier LS/RS phases");
    b=a; input=buttons({1}); expected=output(reference,input);
    // Gate through a persisted role; role 1 is a fixture-defined RF8 mode role.
    effect(b,1).gate_token=65; expected.leftStickX=228; expected.leftStickY=128;
    variation(config,a,b,input,expected,"role-gated base phase is disabled when its role is false");
    b=a; input=buttons({22}); expected=output(reference,buttons({23}));
    for (size_t i=0;i<b.routing_slots_count;++i) {
        if (b.routing_slots[i].slot_id==22) b.routing_slots[i].input_token=23;
        else if (b.routing_slots[i].slot_id==23) b.routing_slots[i].input_token=22;
    }
    variation(config,a,b,input,expected,"single routed snapshot changes digital and analogue RF6/RF7 together");
    config.ultimate_profiles[0]=a;
    config.ultimate_profiles[0].output_program.effects_count=13;
    require(!validate_config_extents(config),"in-memory output-effect extent rejects before nested traversal");
    config.ultimate_profiles[0]=a; effect(config.ultimate_profiles[0],2).coordinates_count=19;
    require(!validate_config_extents(config),"in-memory inline-coordinate extent rejects before use");
    config.ultimate_profiles[0]=a;
}

void persisted_profile_isolation(Config &config, uint8_t expected_schema) {
    require(config.ultimate_profiles_count==2 && config.ultimate_profiles[0].schema_version==expected_schema &&
        config.ultimate_profiles[1].schema_version==expected_schema,"writer fixture decodes two simultaneous complete profiles");
    require(config.game_mode_configs_count==3 && config.game_mode_configs[0].ultimate_profile_config==0 &&
        config.game_mode_configs[1].ultimate_profile_config==1 && config.game_mode_configs[2].ultimate_profile_config==2,
        "writer fixture retains legacy row and explicit A/B profile references");
    Ultimate mode;
    const auto select=[&](size_t row) {
        auto &mc=config.game_mode_configs[row];
        mode.SetConfig(mc,mc.ultimate_profile_config==0?nullptr:&config.ultimate_profiles[mc.ultimate_profile_config-1]);
    };
    const uint64_t cases[]={buttons({17}),buttons({33,32}),buttons({1,23}),buttons({43,45})};
    for(size_t index=0;index<4;++index) {
        select(1); const auto a=output(mode,cases[index]);
        OutputState expected=a;
        if(index==0) { expected.a=false; expected.y=true; }
        if(index==1) { expected.triggerLAnalog=100; expected.triggerRAnalog=180; }
        if(index==2) { expected.leftStickX=166; expected.leftStickY=160; }
        if(index==3) { expected.rightStickX=78; expected.rightStickY=188; }
        select(2); const auto b=output(mode,cases[index]);
        select(1); const auto again=output(mode,cases[index]);
        require(equal(b,expected),"decoded selected B profile executes its distinct bounded effect payload");
        require(!equal(a,b) && equal(a,again),"decoded writer-produced A/B/A final output isolation");
        checks+=3;
    }
    select(0); require(output(mode,buttons({17})).a,"absent-reference legacy row survives two v3 profiles");
}

void carrier_ownership_checks(Config &config, const UltimateProfile &profile, uint8_t expected_schema) {
    if (expected_schema != 4) return;
    GameModeConfig mc{}; mc.mode_id = MODE_ULTIMATE;
    Ultimate mode; mode.SetConfig(mc, &profile);

    // The approved default carrier is LT5 (37): it owns no legacy LT6
    // meaning, while ordinary LT6 remains its source-backed Down+A path.
    const OutputState default_x1 = output(mode, buttons({37}));
    require(!default_x1.a && !default_x1.leftStickDown,
            "default LT5 carrier has no legacy Down+A leakage");
    const OutputState unclaimed_lt6 = output(mode, buttons({38}));
    require(unclaimed_lt6.a && unclaimed_lt6.leftStickDown,
            "LT6 retains legacy Down+A when LT5 is the carrier");

    UltimateProfile alternate = profile;
    alternate.function_bindings[0].activation_condition.all_tokens[0] = 38;
    alternate.function_bindings[0].carrier_token = 38;
    config.ultimate_profiles[0] = alternate; require_valid(config);
    mode.SetConfig(mc, &alternate);
    const OutputState alternate_x1 = output(mode, buttons({38}));
    require(!alternate_x1.a && !alternate_x1.leftStickDown && !alternate_x1.dpadDown,
            "alternate LT6 carrier is absent from digital legacy Down+A output");
    require(UltimateProfileEvaluator::SelectTable(&alternate, buttons({38}), 0) == 2,
            "alternate LT6 carrier activates X1 from original physical snapshot");
    const OutputState alternate_mode_x1 = output(mode, buttons({24,38}));
    require(!alternate_mode_x1.a && !alternate_mode_x1.leftStickDown && !alternate_mode_x1.dpadDown,
            "Mode plus alternate LT6 has no legacy Down+A leakage");
    require(UltimateProfileEvaluator::SelectTable(&alternate, buttons({24,38}), 0) == 4,
            "Mode plus alternate LT6 activates the bounded mode X1 table");

    // Consumption occurs before both the digital and analogue legacy paths,
    // but function selection intentionally retains the original snapshot.
    UltimateProfile rerouted = alternate;
    for (size_t i=0; i<rerouted.routing_slots_count; ++i) {
        if (rerouted.routing_slots[i].slot_id == 37) rerouted.routing_slots[i].input_token = 38;
        else if (rerouted.routing_slots[i].slot_id == 38) rerouted.routing_slots[i].input_token = 37;
    }
    config.ultimate_profiles[0] = rerouted; require_valid(config);
    mode.SetConfig(mc, &rerouted);
    const OutputState original_snapshot = output(mode, buttons({38}));
    require(!original_snapshot.a && !original_snapshot.leftStickDown &&
            UltimateProfileEvaluator::SelectTable(&rerouted, buttons({38}), 0) == 2,
            "carrier activation uses original remap/SOCD snapshot before consumed routing");
    checks += 9;
    config.ultimate_profiles[0] = profile;
}
}

int main(int argc,char **argv) {
    require(argc==3,"usage pipeline CONFIG SCHEMA_VERSION");
    const uint8_t expected_schema=static_cast<uint8_t>(std::atoi(argv[2]));
    std::ifstream stream(argv[1],std::ios::binary);
    std::vector<uint8_t> payload((std::istreambuf_iterator<char>(stream)),{});
    static Config config{};
    pb_istream_t decoder=pb_istream_from_buffer(payload.data(),payload.size());
    require(pb_decode(&decoder,Config_fields,&config),"production Nanopb decode"); require_valid(config);
    const UltimateProfile a=config.ultimate_profiles[0];
    UltimateProfile reordered=a;
    std::reverse(reordered.tables,reordered.tables+reordered.tables_count);
    std::reverse(reordered.roles,reordered.roles+reordered.roles_count);
    std::reverse(reordered.routing_slots,reordered.routing_slots+reordered.routing_slots_count);
    std::reverse(reordered.table_rules,reordered.table_rules+reordered.table_rules_count);
    std::reverse(reordered.output_program.effects,reordered.output_program.effects+reordered.output_program.effects_count);
    config.ultimate_profiles[0]=reordered; require_valid(config); config.ultimate_profiles[0]=a;
    GameModeConfig mc{}; mc.mode_id=MODE_ULTIMATE;
    Ultimate actual, permuted; LegacyUltimate oracle;
    actual.SetConfig(mc,&a); permuted.SetConfig(mc,&reordered); oracle.SetConfig(mc,nullptr);
    const uint8_t selector[]={4,18,19,20,24,25,34,35,36,37,41,42,43,44,45};
    const uint8_t dirs[]={1,2,3,5};
    InputState input{};
    for(uint32_t mask=0;mask<(1u<<15);++mask) for(uint32_t d=0;d<16;++d) {
        input.buttons=mask_tokens(mask,selector,15)|mask_tokens(d,dirs,4);
        compare(actual,oracle,input,"v3 full selector/direction matrix");
        compare(permuted,oracle,input,"reordered complete profile");
    }
    const uint8_t specials[]={21,22,23,29,38,33,32};
    const uint8_t mixed[]={4,17,18,19,20,24,25,26,34,35,36,37,41,42,43,44,45,52,53,54,55};
    uint32_t rng=0x6178c3;
    for(uint32_t special=0;special<128;++special) for(uint32_t sample=0;sample<512;++sample) {
        rng=rng*1664525u+1013904223u;
        input.buttons=mask_tokens(special,specials,7)|mask_tokens(rng,mixed,21)|mask_tokens(sample,dirs,4);
        compare(actual,oracle,input,"special/direction/button overlap matrix");
    }
    // Every Nunchuk state follows every software override, including null,
    // D-pad and simultaneous C-stick. These are host invariants, not hardware PASS.
    for(int state=0;state<8;++state) for(uint32_t mask=0;mask<1024;++mask) {
        input.buttons=mask_tokens(mask,specials,7)|buttons({1,19,25,43,45});
        input.nunchuk_buttons=static_cast<uint8_t>(state); input.nunchuk_x=-37; input.nunchuk_y=91;
        compare(actual,oracle,input,"Nunchuk precedence");
    }
    input={};
    // Full production remap/SOCD state machines, with directional press,
    // simultaneous opposition, release and reactivation sequences.
    for(int type=0;type<=5;++type) {
        GameModeConfig transformed=mc;
        transformed.button_remapping_count=3;
        transformed.button_remapping[0]={BTN_RF11,BTN_RF6};
        transformed.button_remapping[1]={BTN_RF12,BTN_RF6};
        transformed.button_remapping[2]={BTN_RF11,BTN_RF7}; // duplicate physical input cannot create a macro.
        transformed.socd_pairs_count=1;
        transformed.socd_pairs[0].button_dir1=BTN_LF3; transformed.socd_pairs[0].button_dir2=BTN_LF1;
        transformed.socd_pairs[0].socd_type=static_cast<SocdType>(type);
        Ultimate fresh; LegacyUltimate legacy; fresh.SetConfig(transformed,&a); legacy.SetConfig(transformed,nullptr);
        const uint64_t sequence[]={0,buttons({3}),buttons({3,1}),buttons({1}),0,buttons({1}),buttons({1,3}),buttons({3}),0};
        for(int repeat=0;repeat<32;++repeat) for(uint64_t state:sequence) {
            input.buttons=state|buttons({27,28,19,45}); compare(fresh,legacy,input,"remap/SOCD sequence");
        }
    }
    // v1/v2/absent use the exact frozen Stage-B production path. v1/v2
    // table payloads are supplied identically on both sides of the oracle.
    for(int version=0;expected_schema != 4 && version<=2;++version) {
        UltimateProfile legacy_profile=a; legacy_profile.schema_version=static_cast<uint8_t>(version);
        legacy_profile.has_output_program=false; legacy_profile.output_program={};
        legacy_profile.function_bindings_count=0;
        if(version==1) {
            legacy_profile.roles_count=legacy_profile.routing_slots_count=legacy_profile.table_rules_count=0;
            legacy_profile.default_table_id=0;
        }
        if(version!=0) { config.ultimate_profiles[0]=legacy_profile; require_valid(config); }
        const UltimateProfile *selected=version==0?nullptr:&legacy_profile;
        Ultimate fresh; LegacyUltimate legacy; fresh.SetConfig(mc,selected); legacy.SetConfig(mc,selected);
        for(uint32_t sample=0;sample<32768;++sample) {
            rng=rng*1664525u+1013904223u; input.buttons=mask_tokens(sample,selector,15)|mask_tokens(rng,specials,7)|mask_tokens(rng>>7,dirs,4);
            compare(fresh,legacy,input,"v1/v2/absent exact legacy path");
        }
    }
    config.ultimate_profiles[0]=a;
    profile_variations(config,a);
    persisted_profile_isolation(config,expected_schema);
    carrier_ownership_checks(config,a,expected_schema);
    std::printf("PASS production Ultimate final-output comparisons=%zu; frozen legacy oracle; A/B/A effects; storage-order; remap/SOCD; Nunchuk host invariants\n",checks);
    std::printf("sizeof_config=%zu sizeof_profile=%zu\n",sizeof(Config),sizeof(UltimateProfile));
}
