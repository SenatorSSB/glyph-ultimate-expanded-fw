#include "glyph_config_validation.hpp"
#include <pb_decode.h>

#include <cstdio>
#include <fstream>
#include <iterator>
#include <vector>

// Read exact Python-encoded wire bytes; do not reconstruct Config in this harness.
int main(int argc, char **argv) {
    if (argc != 3) return 2;
    std::ifstream input(argv[1], std::ios::binary);
    if (!input) return 2;
    const std::vector<unsigned char> bytes{
        std::istreambuf_iterator<char>(input), std::istreambuf_iterator<char>()};
    Config config = Config_init_zero;
    pb_istream_t stream = pb_istream_from_buffer(bytes.data(), bytes.size());
    if (!pb_decode(&stream, Config_fields, &config)) {
        if (argv[2][0] == '2') {
            std::printf("nanopb_decode=REJECT expectation=PASS error=%s\n", PB_GET_ERROR(&stream));
            return 0;
        }
        std::fprintf(stderr, "Nanopb decode rejected: %s\n", PB_GET_ERROR(&stream));
        return 1;
    }
    if (argv[2][0] == '2') return 1;
    ConfigValidationError error{};
    const bool admitted = validate_glyph_config(config, error);
    const bool expected = argv[2][0] == '1';
    if (admitted != expected) {
        std::fprintf(stderr, "production admission=%d expected=%d error=%s\n",
                     admitted, expected, error.message);
        return 1;
    }
    std::printf("nanopb_decode=PASS production_admission=%s expectation=PASS\n",
                admitted ? "ACCEPT" : "REJECT");
    return 0;
}
