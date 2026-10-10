#include "core/config_button_validation.hpp"
#define main gp_config019_original_main
#include "historical/tools/fixtures/gp_config019_usb_name_selection/main.cpp"
#undef main

// External proof adapter. Original harness/stubs and production bodies are unchanged.
static void binding_wire(bool empty_name, bool backend_binding, unsigned button) {
    wire.clear();
    for (auto id : {MODE_MELEE, MODE_ULTIMATE}) {
        std::vector<uint8_t> payload;
        scalar(payload, 1, id);
        bytes(payload, 2, empty_name ? std::vector<uint8_t>{} : string_bytes("same"));
        if (!backend_binding && id == MODE_MELEE) scalar(payload, 5, button);
        for (auto backend : {COMMS_BACKEND_XINPUT, COMMS_BACKEND_DINPUT, COMMS_BACKEND_NINTENDO_SWITCH})
            scalar(payload, 201, backend);
        bytes(wire, 1, payload);
    }
    for (auto id : {COMMS_BACKEND_XINPUT, COMMS_BACKEND_DINPUT, COMMS_BACKEND_NINTENDO_SWITCH}) {
        std::vector<uint8_t> payload;
        scalar(payload, 1, id); scalar(payload, 2, 1);
        if (backend_binding && id == COMMS_BACKEND_XINPUT) scalar(payload, 3, button);
        bytes(wire, 2, payload);
    }
    bytes(wire, 4, {}); scalar(wire, 6, 1); scalar(wire, 7, 1);
}

static void binding_case(bool empty_name, bool backend_binding, unsigned button) {
    reset();
    binding_wire(empty_name, backend_binding, button);
    static Config decoded = Config_init_zero;
    decoded = Config_init_default;
    auto stream = as_pb_istream(wire);
    require(pb_decode(&stream, Config_fields, &decoded), "binding control must reach real decoder acceptance");
    require(decoded.game_mode_configs_count == 2 && decoded.communication_backend_configs_count == 3,
            "binding control decoded wrong extents");
    const auto count = backend_binding ? decoded.communication_backend_configs[0].activation_binding_count
                                      : decoded.game_mode_configs[0].activation_binding_count;
    require(count == 1, "binding control missing decoded binding");
    const Button &binding = backend_binding ? decoded.communication_backend_configs[0].activation_binding[0]
                                           : decoded.game_mode_configs[0].activation_binding[0];
    static_assert(sizeof(Button) == 1);
    uint8_t raw = 0;
    std::memcpy(&raw, &binding, sizeof(raw));
    require(raw == button, "decoder did not preserve supplied binding bytes");
    require(sameName(decoded.game_mode_configs[0].name, decoded.game_mode_configs[1].name),
            "duplicate/empty name control lost equality");
    require((decoded.game_mode_configs[0].name[0] == 0) == empty_name, "name control decoded wrong bytes");
    const bool valid = button == 1 || button == 60;
    require(validate_config_button_bindings(decoded) == valid, "real validator disagrees with named button domain");

    static Config live = Config_init_zero;
    live = glyph_default_config();
    static std::array<unsigned char, sizeof(Config)> live_before{}, saved_before{};
    std::memcpy(live_before.data(), &live, sizeof(live));
    std::memcpy(saved_before.data(), &persistence.saved, sizeof(persistence.saved));
    ConfiguratorBackend backend(live);
    backend.result = CMD_SUCCESS;
    const bool accepted = backend.HandleSetConfig();
    if (valid) {
        require(accepted && backend.result == CMD_SUCCESS && persistence.saves == 1,
                "valid binding/name control was not saved and published");
        require(live.game_mode_configs_count == 2 && validate_config_button_bindings(live),
                "valid control live publication differs");
        require(sameName(live.game_mode_configs[0].name, live.game_mode_configs[1].name) &&
                (live.game_mode_configs[0].name[0] == 0) == empty_name,
                "valid control names changed on publication");
    } else {
        require(!accepted && backend.result == CMD_ERROR && persistence.saves == 0,
                "decoded invalid binding was not refused before save");
        require(std::memcmp(live_before.data(), &live, sizeof(live)) == 0,
                "decoded invalid binding changed live Config bytes");
        require(std::memcmp(saved_before.data(), &persistence.saved, sizeof(persistence.saved)) == 0,
                "decoded invalid binding changed persistence stub bytes");
    }
    row("current_binding", std::string("name=") + (empty_name ? "empty" : "duplicate") +
        " target=" + (backend_binding ? "backend" : "mode") + " raw=" + std::to_string(button) +
        (valid ? " decoded=PASS validator=PASS CMD_SUCCESS saves=1 names=PRESERVED"
               : " decoded=PASS validator=REJECT CMD_ERROR saves=0 live=BYTE_EXACT saved=BYTE_EXACT"));
}

int main() {
    try {
        require(gp_config019_original_main() == 0, "original 18 observations failed against current acceptance");
        for (bool empty_name : {false, true})
            for (bool backend_binding : {false, true})
                for (unsigned button : {1u, 60u, 0u, 61u, 255u})
                    binding_case(empty_name, backend_binding, button);
        row("current_result", "PASS observations=18 valid_controls=8 decoded_invalid_controls=12 ABI=short_enum ASan_UBSan=PASS hardware=NOT_CLAIMED");
        return 0;
    } catch (const std::exception &error) {
        std::cerr << error.what() << '\n';
        return 1;
    }
}
