#include "core/config_utils.hpp"

#include <pb_decode.h>

#include <cstdio>
#include <cstdlib>
#include <fstream>
#include <iterator>
#include <vector>

namespace {
void require(bool value, const char *label) {
    if (!value) {
        std::fprintf(stderr, "FAIL: %s\n", label);
        std::exit(1);
    }
}
}

int main(int argc, char **argv) {
    require(argc == 2, "usage gamecube-default CONFIG");
    std::ifstream stream(argv[1], std::ios::binary);
    std::vector<uint8_t> payload((std::istreambuf_iterator<char>(stream)), {});
    Config config{};
    pb_istream_t decoder = pb_istream_from_buffer(payload.data(), payload.size());
    require(pb_decode(&decoder, Config_fields, &config), "production Nanopb decode");

    const CommunicationBackendConfig gamecube = backend_config_from_id(
        COMMS_BACKEND_GAMECUBE,
        config.communication_backend_configs,
        config.communication_backend_configs_count);
    require(gamecube.backend_id == COMMS_BACKEND_GAMECUBE,
            "GameCube backend lookup retains GameCube identity");
    require(gamecube.default_mode_config == 1,
            "GameCube lookup installs legacy Ultimate first-row default");
    const GameModeConfig *mode = gamecube.default_mode_config == 0 ? nullptr :
        &config.game_mode_configs[gamecube.default_mode_config - 1];
    require(mode != nullptr && mode->mode_id == MODE_ULTIMATE &&
                mode->ultimate_profile_config == 0,
            "GameCube default resolves a nonnull legacy Ultimate mode");

    CommunicationBackendConfig without_gamecube[32]{};
    size_t count = 0;
    for (size_t index = 0; index < config.communication_backend_configs_count; ++index) {
        if (config.communication_backend_configs[index].backend_id != COMMS_BACKEND_GAMECUBE) {
            require(count < 32, "host fixture backend capacity");
            without_gamecube[count++] = config.communication_backend_configs[index];
        }
    }
    const CommunicationBackendConfig missing = backend_config_from_id(
        COMMS_BACKEND_GAMECUBE, without_gamecube, count);
    require(missing.default_mode_config == 0,
            "missing GameCube row retains the zero-mode fallback path");
    std::puts("gamecube_default_lookup=mode_1 legacy_ultimate_ref=0 missing_gamecube_zero_mode_path=observed");
    return 0;
}
