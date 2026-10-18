#include "glyph_config_validation.hpp"
#include "modes/UltimateProfileEvaluator.hpp"

#include <pb_decode.h>

#include <cstdio>
#include <fstream>
#include <iterator>
#include <vector>

namespace {

bool check(bool condition, const char *name) {
    if (!condition) {
        static bool reported = false;
        if (!reported) std::fprintf(stderr, "FAIL: %s\n", name);
        reported = true;
    }
    return condition;
}

bool pressed(uint64_t buttons, uint8_t token) {
    return (buttons & (uint64_t{1} << (token - 1))) != 0;
}

// Frozen host oracle copied from the current legacy role/table selector. It is
// intentionally independent of the profile evaluator under test.
uint8_t legacy_selected_table(uint64_t buttons) {
    const bool lf4 = pressed(buttons, 4), rf2 = pressed(buttons, 18), rf3 = pressed(buttons, 19);
    const bool rf4 = pressed(buttons, 20), rf8 = pressed(buttons, 24), rf9 = pressed(buttons, 25);
    const bool lt2 = pressed(buttons, 34), lt3 = pressed(buttons, 35), lt4 = pressed(buttons, 36);
    const bool lt5 = pressed(buttons, 37), rt1 = pressed(buttons, 41);
    const bool cstick = pressed(buttons, 42) || pressed(buttons, 43) || pressed(buttons, 44) || pressed(buttons, 45);
    const bool y2_sublayer = lt3 && !lf4 && (rf3 || rf4);
    const bool base_rf3_x = rf3 && !lt3 && !lf4;
    const bool rf9_base_rf3 = rf9 && base_rf3_x;
    const bool rf4_suppressed = rf9_base_rf3 && rf4;
    const bool custom = rt1 && rf4 && !rf4_suppressed;
    const bool rf4_cstick_suppressed = rf4 && cstick && !custom;
    const bool rf4_available = rf4 && !rf4_cstick_suppressed && !rf4_suppressed;
    const bool normal_x = y2_sublayer && rf3;
    const bool flipper = lt3 && !lf4 && rf4_available && !custom;
    const bool tilt1 = rf4_available && (!lt3 || lf4) && !rt1 && !(lf4 && rf2);
    const bool tilt2 = rt1 && !rf4;
    const bool minus41 = rf4_available && rf2 && !lt3 && !lf4 && !custom;
    if (minus41) return 22;
    if (tilt1 && tilt2) return 23;
    const bool normal_effective = normal_x && !flipper;
    const bool rt_rf = normal_effective || flipper || tilt1 || tilt2 || custom;
    const bool y2 = lt3 && !lf4 && !y2_sublayer && !rt_rf;
    int count = 0;
    int modifier = 0;
    const auto add = [&](bool active, int id) { if (active) { ++count; modifier = id; } };
    add(lt5, 1); add(lt4, 2); add(lt2 && !lf4, 3); add(y2, 4); add(normal_effective, 5); add(flipper, 6);
    if (custom) add(true, 9); else if (tilt1) add(true, 7); else if (tilt2) add(true, 8);
    if (count != 1) return rf8 ? 1 : 0;
    if (!rf8) { const uint8_t normal[] = {0, 2, 3, 6, 7, 9, 11, 19, 20, 21}; return normal[modifier]; }
    const uint8_t mode[] = {1, 4, 5, 8, 7, 10, 12, 1, 25, 26};
    return mode[modifier];
}

bool evaluate_v2(const Config &config) {
    if (config.ultimate_profiles_count == 0) return false;
    const UltimateProfile &profile = config.ultimate_profiles[0];
    const uint8_t selector_tokens[] = {4,18,19,20,24,25,34,35,36,37,41,42,43,44,45};
    bool result = true;
    for (uint32_t mask = 0; mask < (1u << 15); ++mask) {
        uint64_t buttons = 0;
        for (size_t bit = 0; bit < 15; ++bit) if (mask & (1u << bit)) buttons |= uint64_t{1} << (selector_tokens[bit] - 1);
        const uint8_t selected = UltimateProfileEvaluator::SelectTable(&profile, buttons, 27);
        const uint8_t expected = legacy_selected_table(buttons);
        result &= check(selected == expected, "v2 profile matches frozen legacy selector");
    }
    Config reordered_config = config;
    UltimateProfile &reordered = reordered_config.ultimate_profiles[0];
    const UltimateProfileRole first_role = reordered.roles[0]; reordered.roles[0] = reordered.roles[20]; reordered.roles[20] = first_role;
    const UltimateProfileTableRule first_rule = reordered.table_rules[0]; reordered.table_rules[0] = reordered.table_rules[18]; reordered.table_rules[18] = first_rule;
    const UltimateProfileTable first_table = reordered.tables[0]; reordered.tables[0] = reordered.tables[27]; reordered.tables[27] = first_table;
    ConfigValidationError error{};
    result &= check(validate_glyph_config(reordered_config, error),
                    "reordered profile storage remains production-valid");
    for (uint32_t mask = 0; mask < (1u << 15); ++mask) {
        uint64_t buttons = 0;
        for (size_t bit = 0; bit < 15; ++bit) if (mask & (1u << bit)) buttons |= uint64_t{1} << (selector_tokens[bit] - 1);
        result &= check(UltimateProfileEvaluator::SelectTable(&reordered, buttons, 27) == legacy_selected_table(buttons),
                        "role and rule storage order do not control precedence");
    }
    return result;
}

bool evaluate_v1(const Config &config) {
    if (config.ultimate_profiles_count == 0) return false;
    const UltimateProfile &profile = config.ultimate_profiles[0];
    const uint64_t input_buttons = 0;
    const UltimateProfileEvaluator::RoutingState routing =
        UltimateProfileEvaluator::EvaluateRouting(profile, input_buttons);
    return check(UltimateProfileEvaluator::SelectTable(&profile, input_buttons, 11) == 11,
                 "v1 selection preserves legacy table choice") &&
        check(!routing.slots[24] && !routing.slots[37] && !routing.slots[41],
              "v1 has no Stage-B routing state");
}

bool evaluate_v3(const Config &config) {
    if (config.ultimate_profiles_count == 0) return false;
    const UltimateProfile &profile = config.ultimate_profiles[0];
    bool result = true;
    // A/B/A routing isolation: the same physical RF6 press is evaluated
    // through profile A, a finite B permutation, then A again.  This is the
    // production evaluator used by Ultimate before every fixed output phase.
    const uint64_t rf6 = uint64_t{1} << (22 - 1);
    result &= check(UltimateProfileEvaluator::RouteLogicalInputs(&profile, rf6) == rf6,
                    "v3 profile A preserves identity routed input");
    UltimateProfile profile_b = profile;
    for (size_t i = 0; i < profile_b.routing_slots_count; ++i) {
        if (profile_b.routing_slots[i].slot_id == 22) profile_b.routing_slots[i].input_token = 23;
        else if (profile_b.routing_slots[i].slot_id == 23) profile_b.routing_slots[i].input_token = 22;
    }
    result &= check(UltimateProfileEvaluator::RouteLogicalInputs(&profile_b, rf6) == (uint64_t{1} << (23 - 1)),
                    "v3 profile B changes only its routed logical input");
    result &= check(UltimateProfileEvaluator::RouteLogicalInputs(&profile, rf6) == rf6,
                    "v3 profile A is unchanged after B");
    UltimateProfile reordered = profile;
    const UltimateProfileRoutingSlot first = reordered.routing_slots[0];
    reordered.routing_slots[0] = reordered.routing_slots[31];
    reordered.routing_slots[31] = first;
    result &= check(UltimateProfileEvaluator::RouteLogicalInputs(&reordered, rf6) == rf6,
                    "v3 routing storage order does not change logical input");
    return result;
}

bool evaluate_v4(const Config &config) {
    if (config.ultimate_profiles_count == 0) return false;
    const UltimateProfile &profile = config.ultimate_profiles[0];
    const uint8_t selector_tokens[] = {4,18,19,20,24,25,34,35,36,37,41,42,43,44,45};
    bool result = true;
    for (uint32_t mask = 0; mask < (1u << 15); ++mask) {
        uint64_t input_buttons = 0;
        for (size_t bit = 0; bit < 15; ++bit)
            if (mask & (1u << bit)) input_buttons |= uint64_t{1} << (selector_tokens[bit] - 1);
        result &= check(UltimateProfileEvaluator::SelectTable(&profile, input_buttons, 27) == legacy_selected_table(input_buttons),
                        "v4 X1 binding matches frozen legacy selector");
    }
    UltimateProfile alternate = profile;
    alternate.function_bindings[0].activation_condition.all_tokens[0] = 38;
    result &= check(UltimateProfileEvaluator::SelectTable(&alternate, uint64_t{1} << (38 - 1), 27) == 2,
                    "v4 binding changes only its physical X1 carrier");
    UltimateProfile rerouted = profile;
    for (size_t i = 0; i < rerouted.routing_slots_count; ++i)
        if (rerouted.routing_slots[i].slot_id == 37) rerouted.routing_slots[i].input_token = 36;
    result &= check(UltimateProfileEvaluator::SelectTable(&rerouted, uint64_t{1} << (37 - 1), 27) == 2,
                    "v4 binding is evaluated before profile routing");
    return result;
}

}  // namespace

int main(int argc, char **argv) {
    if (argc != 4) return 2;
    std::ifstream input(argv[1], std::ios::binary);
    if (!input) return 2;
    const std::vector<unsigned char> bytes{
        std::istreambuf_iterator<char>(input), std::istreambuf_iterator<char>()};
    Config config = Config_init_zero;
    pb_istream_t stream = pb_istream_from_buffer(bytes.data(), bytes.size());
    if (!pb_decode(&stream, Config_fields, &config)) {
        std::fprintf(stderr, "nanopb_decode=%s\n", PB_GET_ERROR(&stream));
        return argv[2][0] == '0' ? 0 : 1;
    }
    ConfigValidationError error{};
    const bool admitted = validate_glyph_config(config, error);
    const bool expected = argv[2][0] == '1';
    if (admitted != expected) {
        std::fprintf(stderr, "production admission=%d expected=%d error=%s\n",
                     admitted, expected, error.message);
        return 1;
    }
    if (!admitted) return 0;
    const bool evaluated = argv[3][0] == '4' ? evaluate_v4(config) :
        (argv[3][0] == '3' ? evaluate_v3(config) :
        (argv[3][0] == '2' ? evaluate_v2(config) : evaluate_v1(config)));
    if (evaluated) {
        std::printf("sizeof_config=%zu\n", sizeof(Config));
    }
    return evaluated ? 0 : 1;
}
