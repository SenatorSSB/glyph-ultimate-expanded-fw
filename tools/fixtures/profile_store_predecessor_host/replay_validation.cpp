#include "core/config_validation.hpp"
#include "glyph_config_validation.hpp"

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
    return glyph ? 0 : 1;
}
