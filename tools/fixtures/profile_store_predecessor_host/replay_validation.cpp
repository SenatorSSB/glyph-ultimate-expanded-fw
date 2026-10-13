#include "core/config_validation.hpp"
#include "glyph_config_validation.hpp"
#include "config_rgb_target_domain.hpp"

#include <pb_decode.h>

#include <cstdio>
#include <fstream>
#include <iterator>
#include <vector>

int main(int argc, char **argv) {
    if (argc != 2) return 2;
    std::ifstream file(argv[1], std::ios::binary);
    std::vector<uint8_t> bytes((std::istreambuf_iterator<char>(file)), {});
    Config config = Config_init_default;
    pb_istream_t input = pb_istream_from_buffer(bytes.data(), bytes.size());
    const bool decoded = pb_decode(&input, Config_fields, &config) && input.bytes_left == 0;
    std::printf("decode=%s bytes_left=%zu\n", decoded ? "PASS" : "FAIL", input.bytes_left);
    if (!decoded) return 1;
    std::printf("legacy_profiles=%zu modes=%zu rgb=%zu format=%lu\n",
                config.ultimate_profiles_count, config.game_mode_configs_count, config.rgb_configs_count,
                static_cast<unsigned long>(config.ultimate_profile_store_format));
    std::printf("extents=%s\n", validate_config_extents(config) ? "PASS" : "FAIL");
    ConfigValidationError error{};
    const bool semantic = validate_config_semantics(config, error);
    std::printf("semantic=%s error=%.*s\n", semantic ? "PASS" : "FAIL",
                static_cast<int>(error.length), error.message);
    error = {};
    const bool glyph = validate_glyph_config(config, error);
    std::printf("glyph=%s error=%.*s\n", glyph ? "PASS" : "FAIL",
                static_cast<int>(error.length), error.message);
    Config compact_negative = config;
    compact_negative.ultimate_profile_store_format = 1;
    compact_negative.ultimate_profile_store_incarnation = 1;
    error = {};
    const bool compact_rejected = !validate_glyph_config(compact_negative, error);
    std::printf("compact_unspecified_negative=%s\n", compact_rejected ? "PASS" : "FAIL");
    Config colored_unspecified = config;
    colored_unspecified.rgb_configs[0].button_colors[0].button = BTN_UNSPECIFIED;
    colored_unspecified.rgb_configs[0].button_colors[0].color = 1;
    error = {};
    const bool colored_rejected = !validate_glyph_config(colored_unspecified, error);
    std::printf("legacy_colored_unspecified_negative=%s\n", colored_rejected ? "PASS" : "FAIL");
    // The source-faithful base comparison intentionally uses its historical
    // strict domain header, which predates this normalization helper.
#ifndef BASE_COMPARISON
    Config normalized = config;
    normalize_legacy_glyph_rgb_noops(normalized);
    bool noops_removed = true;
    for (size_t i = 0; i < normalized.rgb_configs_count; ++i) {
        for (size_t j = 0; j < normalized.rgb_configs[i].button_colors_count; ++j) {
            const ButtonToColorMapping &mapping = normalized.rgb_configs[i].button_colors[j];
            if (mapping.button == BTN_UNSPECIFIED && mapping.color == 0) noops_removed = false;
        }
    }
    std::printf("legacy_noop_normalization=%s\n", noops_removed ? "PASS" : "FAIL");
    Config colored_normalized = colored_unspecified;
    normalize_legacy_glyph_rgb_noops(colored_normalized);
    const bool colored_preserved = colored_normalized.rgb_configs[0].button_colors_count != 0 &&
        colored_normalized.rgb_configs[0].button_colors[0].button == BTN_UNSPECIFIED &&
        colored_normalized.rgb_configs[0].button_colors[0].color == 1;
    std::printf("legacy_colored_unspecified_normalization_negative=%s\n",
                colored_preserved ? "PASS" : "FAIL");
    return glyph && compact_rejected && colored_rejected && noops_removed && colored_preserved ? 0 : 1;
#else
    return glyph && compact_rejected && colored_rejected ? 0 : 1;
#endif
}
