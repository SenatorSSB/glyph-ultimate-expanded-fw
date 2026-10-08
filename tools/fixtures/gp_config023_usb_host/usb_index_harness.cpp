#include "host_stubs.hpp"

#include <array>
#include <cstring>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

#include "core/config_validation.hpp"

static void require(bool value, const char *message) {
    if (!value) throw std::runtime_error(message);
}

static unsigned selector_calls = 0;
static unsigned usb_getter_calls = 0;
static unsigned detector_calls = 0;
static unsigned primary_calls = 0;
static unsigned secondary_calls = 0;
unsigned set_mode_calls = 0;
static GameModeId last_mode_id = MODE_UNSPECIFIED;
static CommunicationBackendId selected_detected = COMMS_BACKEND_UNSPECIFIED;
static CommunicationBackendConfig selector_result = CommunicationBackendConfig_init_zero;
static CommunicationBackendConfig usb_result = CommunicationBackendConfig_init_zero;
static CommunicationBackend primary;
static CommunicationBackend *secondary_storage[2]{};
static std::vector<CommunicationBackendId> primary_ids;
enum class BootOutcome { Pending, Normal, StoredConfigRejected, StorageFailure, DefaultsRejected, StartupConfigRejected };
static std::vector<std::string> recovery_events;
static constexpr int SSD1306_WHITE = 1;
struct HostDisplay {
    void clearDisplay() { recovery_events.push_back("clear"); }
    void setFont(void *) { recovery_events.push_back("font"); }
    void setTextSize(int value) { recovery_events.push_back("size=" + std::to_string(value)); }
    void setTextColor(int value) { recovery_events.push_back("color=" + std::to_string(value)); }
    void setCursor(int x, int y) { recovery_events.push_back("cursor=" + std::to_string(x) + "," + std::to_string(y)); }
    void println(const char *text) { recovery_events.push_back(std::string("text=") + text); }
    void display() { recovery_events.push_back("display"); }
};
static HostDisplay display;
static BootOutcome published_outcome = BootOutcome::Pending;

void publish_boot_state(BootOutcome outcome, bool) {
    published_outcome = outcome;
    recovery_events.push_back("publish=" + std::to_string(static_cast<unsigned>(outcome)));
}

CommunicationBackendConfig backend_config_from_id(CommunicationBackendId backend_id,
    const CommunicationBackendConfig *configs, size_t count) {
    for (size_t i = 0; i < count; ++i) if (configs[i].backend_id == backend_id) return configs[i];
    return CommunicationBackendConfig_init_zero;
}
CommunicationBackendConfig backend_config_from_buttons(const InputState &,
    const CommunicationBackendConfig *, size_t) {
    return CommunicationBackendConfig_init_zero;
}
void set_mode(CommunicationBackend *, GameModeConfig &mode, Config &) {
    ++set_mode_calls;
    last_mode_id = mode.mode_id;
}

static void selector(CommunicationBackendConfig &out, const InputState &, Config &) {
    ++selector_calls;
    out = selector_result;
}
static void mutating_selector(CommunicationBackendConfig &out, const InputState &, Config &config) {
    ++selector_calls;
    out = selector_result;
    config.default_usb_backend_config = static_cast<uint8_t>(255);
}
static void usb_getter(CommunicationBackendConfig &out, const Config &) {
    ++usb_getter_calls;
    out = usb_result;
}
static CommunicationBackendId detect(const Pinout &) {
    ++detector_calls;
    return selected_detected;
}
static size_t init_secondaries(CommunicationBackend **&out, CommunicationBackend *&,
    CommunicationBackendId, InputState &, InputSource **, size_t, Config &, const Pinout &) {
    ++secondary_calls;
    secondary_storage[0] = &primary;
    out = secondary_storage;
    return 1;
}
static void init_primary(CommunicationBackend *&out, CommunicationBackendId backend_id,
    InputState &, InputSource **, size_t, Config &, const Pinout &) {
    ++primary_calls;
    primary_ids.push_back(backend_id);
    out = &primary;
}

#include "production_backend_init.inc"
#include "production_backend_selectors.inc"
#include "production_persistence.inc"
#include "production_recovery.inc"

static Config config_with_count(unsigned count, unsigned index) {
    Config config = Config_init_zero;
    config.communication_backend_configs_count = static_cast<pb_size_t>(count);
    config.default_usb_backend_config = static_cast<uint8_t>(index);
    config.game_mode_configs_count = 2;
    config.game_mode_configs[0].mode_id = MODE_MELEE;
    config.game_mode_configs[1].mode_id = MODE_KEYBOARD;
    for (unsigned i = 0; i < sizeof(config.communication_backend_configs) /
            sizeof(config.communication_backend_configs[0]); ++i) {
        config.communication_backend_configs[i].backend_id = COMMS_BACKEND_XINPUT;
        config.communication_backend_configs[i].default_mode_config = 1;
    }
    return config;
}

static void reset_calls() {
    selector_calls = usb_getter_calls = detector_calls = primary_calls = secondary_calls = 0;
    set_mode_calls = persistence.saves = 0;
    last_mode_id = MODE_UNSPECIFIED;
    primary_ids.clear();
    host_watchdog = HostWatchdog{};
    host_watchdog_reboot = false;
    selected_detected = COMMS_BACKEND_UNSPECIFIED;
    selector_result = CommunicationBackendConfig_init_zero;
    usb_result = CommunicationBackendConfig_init_zero;
}

static std::string backend_name(CommunicationBackendId id) {
    switch (id) {
        case COMMS_BACKEND_GAMECUBE: return "GC";
        case COMMS_BACKEND_XINPUT: return "XInput";
        case COMMS_BACKEND_DINPUT: return "DInput";
        case COMMS_BACKEND_NINTENDO_SWITCH: return "Switch";
        case COMMS_BACKEND_CONFIGURATOR: return "Configurator";
        default: return "UNSPECIFIED";
    }
}

static void index_matrix() {
    unsigned actual_extent = sizeof(Config{}.communication_backend_configs) /
        sizeof(Config{}.communication_backend_configs[0]);
    unsigned accepted = 0;
    for (unsigned count = 0; count <= 15; ++count) {
        for (unsigned index = 0; index <= 255; ++index) {
            Config config = config_with_count(count, index);
            ConfigValidationError error{};
            const bool valid = validate_config_semantics(config, error);
            const bool expected = count <= actual_extent && index >= 1 && index <= count;
            require(valid == expected, "0..255 x 0..15 index/count matrix mismatch");
            require(is_valid_usb_default_index(config) == expected,
                    "shared production index predicate mismatch");
            if (expected) ++accepted;
        }
    }
    require(actual_extent == 15 && accepted == 120, "generated communication backend extent/count");
    for (unsigned count = 16; count <= 255; ++count) {
        Config config = config_with_count(count, 1);
        require(!validate_config_extents(config), "out-of-extent count accepted");
        require(!is_valid_usb_default_index(config), "out-of-extent count admitted by index helper");
    }
    std::cout << "index_matrix counts=0..15 indices=0..255 cases=4096 accepted=" << accepted
              << " actual_extent=" << actual_extent << " oversized_counts=16..255 REJECT\n";
}

static void invalid_start_and_post_selector() {
    InputState inputs{}; Pinout pinout{}; CommunicationBackend **backends = nullptr;
    for (const auto invalid : {std::pair<unsigned, unsigned>{1, 0}, {1, 2}, {0, 1}, {16, 1}, {1, 255}}) {
        reset_calls();
        Config config = config_with_count(invalid.first, invalid.second);
        const auto before = config;
        require(initialize_backends(backends, inputs, nullptr, 0, config, pinout,
            selector, usb_getter, detect, init_secondaries, init_primary) == 0,
            "invalid pre-selector state initialized a backend");
        require(selector_calls == 0 && usb_getter_calls == 0 && detector_calls == 0 &&
                primary_calls == 0 && secondary_calls == 0 && persistence.saves == 0,
                "invalid pre-selector state reached downstream callback/save");
        require(std::memcmp(&before, &config, sizeof(Config)) == 0,
                "invalid pre-selector rejection mutated Config");
    }
    reset_calls();
    Config config = config_with_count(1, 1);
    selector_result.backend_id = COMMS_BACKEND_UNSPECIFIED;
    require(initialize_backends(backends, inputs, nullptr, 0, config, pinout,
        mutating_selector, usb_getter, detect, init_secondaries, init_primary) == 0,
        "selector-created invalid index was not rejected");
    require(selector_calls == 1 && usb_getter_calls == 0 && detector_calls == 0 &&
            primary_calls == 0 && secondary_calls == 0 && persistence.saves == 0,
            "post-selector rejection reached downstream callback/save");
    std::cout << "invalid_routes pre_selector=5 no_callbacks_or_save=PASS post_selector=1 selector_only=PASS Config_pre_rejection=BYTE_EXACT\n";
}

static void valid_routes() {
    InputState inputs{}; Pinout pinout{}; CommunicationBackend **backends = nullptr;
    Config config = config_with_count(1, 1);

    reset_calls(); config = config_with_count(1, 1);
    selector_result.backend_id = COMMS_BACKEND_GAMECUBE;
    selector_result.default_mode_config = 1;
    require(initialize_backends(backends, inputs, nullptr, 0, config, pinout,
        selector, usb_getter, detect, init_secondaries, init_primary) == 1,
        "GC route did not initialize");
    require(primary_calls == 1 && detector_calls == 0 && secondary_calls == 1 &&
            set_mode_calls == 1 && last_mode_id == MODE_MELEE && backends[0] == &primary &&
            primary_ids == std::vector<CommunicationBackendId>{COMMS_BACKEND_GAMECUBE},
            "GC route callback/mode trace mismatch");
    std::cout << "route GC primary=1 secondary=1 detect=0 mode=1 PASS\n";

    reset_calls(); config = config_with_count(1, 1);
    selector_result.backend_id = COMMS_BACKEND_UNSPECIFIED;
    usb_result.backend_id = COMMS_BACKEND_XINPUT;
    usb_result.default_mode_config = 1;
    selected_detected = COMMS_BACKEND_XINPUT;
    require(initialize_backends(backends, inputs, nullptr, 0, config, pinout,
        selector, usb_getter, detect, init_secondaries, init_primary) == 1,
        "USB route did not initialize");
    require(primary_calls == 2 && usb_getter_calls == 1 && detector_calls == 1 &&
            secondary_calls == 1 && set_mode_calls == 1 && primary_ids ==
                std::vector<CommunicationBackendId>{COMMS_BACKEND_XINPUT, COMMS_BACKEND_XINPUT},
            "USB route callback/mode trace mismatch");
    std::cout << "route USB_XInput getter=1 detect=1 primary=2 secondary=1 mode=1 PASS\n";

    reset_calls(); config = config_with_count(1, 1);
    selector_result.backend_id = COMMS_BACKEND_DINPUT;
    selector_result.default_mode_config = 2;
    require(initialize_backends(backends, inputs, nullptr, 0, config, pinout,
        selector, usb_getter, detect, init_secondaries, init_primary) == 1,
        "Keyboard/DInput route did not initialize");
    require(primary_calls == 1 && detector_calls == 0 && secondary_calls == 1 &&
            set_mode_calls == 1 && last_mode_id == MODE_KEYBOARD && primary_ids ==
                std::vector<CommunicationBackendId>{COMMS_BACKEND_DINPUT},
            "Keyboard/DInput route callback/mode trace mismatch");
    std::cout << "route Keyboard_DInput primary=1 secondary=1 mode=2 PASS\n";

    reset_calls(); config = config_with_count(1, 1);
    config.communication_backend_configs[0].backend_id = COMMS_BACKEND_DINPUT;
    host_watchdog_reboot = true; host_watchdog.scratch[0] = 1; host_watchdog.scratch[1] = 2;
    selector_result.backend_id = COMMS_BACKEND_UNSPECIFIED;
    usb_result.backend_id = COMMS_BACKEND_DINPUT;
    usb_result.default_mode_config = 1;
    selected_detected = COMMS_BACKEND_DINPUT;
    require(initialize_backends(backends, inputs, nullptr, 0, config, pinout,
        get_backend_config_default, get_usb_backend_config_default, detect,
        init_secondaries, init_primary) == 1,
        "watchdog route did not initialize");
    require(config.communication_backend_configs[0].default_mode_config == 2,
            "watchdog route did not apply requested mode");
    require(persistence.saves == 1, "watchdog route save count");
    require(primary_calls == 2 && detector_calls == 1 && secondary_calls == 1 &&
            set_mode_calls == 1 && last_mode_id == MODE_KEYBOARD,
            "watchdog route callback/mode counts");
    require(primary_ids == std::vector<CommunicationBackendId>{COMMS_BACKEND_DINPUT, COMMS_BACKEND_DINPUT},
            "watchdog route selected wrong backend IDs");
    std::cout << "route watchdog DInput scratch=(1,2) valid_index=1 mode_update=2 save=1 PASS\n";
}

static void failure_containment() {
    // The production semantic validator is pure: invalid index rejects without changing
    // the caller's Config. This does not emulate ConfiguratorBackend persistence.
    Config config = config_with_count(1, 255);
    const Config before = config;
    ConfigValidationError error{};
    require(!validate_config_semantics(config, error), "invalid SET-style Config accepted");
    require(std::memcmp(&before, &config, sizeof(Config)) == 0,
            "invalid Config validation altered caller bytes");
    std::cout << "containment invalid_config=REJECT caller_bytes=BYTE_EXACT validator_persistence=NOT_APPLICABLE\n";
}

static std::vector<uint8_t> wire_config(bool include_usb_index, unsigned usb_index) {
    // Empty repeated backend-config message (Config tag 2), followed by optional tag 7.
    std::vector<uint8_t> wire{0x12, 0x00};
    if (include_usb_index) {
        wire.push_back(0x38);
        do {
            uint8_t byte = static_cast<uint8_t>(usb_index & 0x7f);
            usb_index >>= 7;
            if (usb_index != 0) byte |= 0x80;
            wire.push_back(byte);
        } while (usb_index != 0);
    }
    return wire;
}

static bool decode_and_validate(const std::vector<uint8_t> &wire, bool decoder_expected,
                               unsigned decoded_index_expected) {
    Config candidate = Config_init_default;
    pb_istream_t stream = pb_istream_from_buffer(wire.data(), wire.size());
    const bool decoded = pb_decode(&stream, Config_fields, &candidate);
    require(decoded == decoder_expected, "actual nanopb decoder verdict mismatch");
    if (!decoded) return false;
    require(candidate.default_usb_backend_config == decoded_index_expected &&
            candidate.communication_backend_configs_count == 1,
            "actual nanopb decoded USB index/backend extent mismatch");
    ConfigValidationError error{};
    return validate_config_semantics(candidate, error);
}

static void decoder_and_persisted_refusal() {
    require(persistence.SetValidator(validate_config_semantics), "actual persistence validator install");
    const struct Case { const char *label; bool present; unsigned index; bool decoder_accepts; } cases[] = {
        {"omitted", false, 0, true}, {"zero", true, 0, true},
        {"out_of_range_2", true, 2, true}, {"out_of_range_255", true, 255, true},
        {"varint_256", true, 256, false}, {"valid_1", true, 1, true}
    };
    for (const auto &item : cases) {
        const auto bytes = wire_config(item.present, item.index);
        const bool valid = decode_and_validate(bytes, item.decoder_accepts,
            item.present ? item.index : 0);
        require(valid == (std::string(item.label) == "valid_1"),
                "nanopb-decoded required index semantic verdict");
        if (std::string(item.label) == "valid_1") {
            std::cout << "decoder_case " << item.label << " decode=PASS semantic=PASS\n";
            continue;
        }

        LittleFS.saved_bytes = bytes;
        const auto saved_before = LittleFS.saved_bytes;
        Config caller = config_with_count(1, 1);
        const Config caller_before = caller;
        const unsigned saves_before = persistence.saves;
        require(persistence.LoadConfigChecked(caller) == Persistence::LoadResult::Rejected,
                "production LoadConfigChecked did not refuse invalid stored index");
        require(std::memcmp(&caller_before, &caller, sizeof(Config)) == 0,
                "rejected stored Config changed caller bytes");
        require(LittleFS.saved_bytes == saved_before,
                "rejected stored Config bytes changed");
        require(persistence.saves == saves_before, "rejected stored Config reached SaveConfig");
        std::cout << "decoder_case " << item.label << " decode="
                  << (item.decoder_accepts ? "PASS" : "REJECT")
                  << " semantic=" << (item.decoder_accepts ? "REJECT" : "NOT_REACHED")
                  << " stored=REJECT caller=BYTE_EXACT saved=BYTE_EXACT\n";
    }
}

static void executable_recovery_refusal() {
    recovery_events.clear();
    published_outcome = BootOutcome::Pending;
    watchdog_hw->scratch[0] = 9;
    watchdog_hw->scratch[1] = 7;
    refuse_boot(BootOutcome::StartupConfigRejected, true);
    const std::vector<std::string> expected{
        "clear", "font", "size=1", "color=1", "cursor=0,0",
        "text=Startup Config invalid", "text=Recovery required", "text=Operation refused",
        "display", "publish=5"
    };
    require(recovery_events == expected, "actual recovery display text/order mismatch");
    require(published_outcome == BootOutcome::StartupConfigRejected &&
            watchdog_hw->scratch[0] == 0 && watchdog_hw->scratch[1] == 0,
            "actual refusal outcome/watchdog cleanup mismatch");
    recovery_events.clear();
    refuse_boot(BootOutcome::StartupConfigRejected, false);
    require(recovery_events == std::vector<std::string>{"publish=5"},
            "display-unavailable startup refusal drew UI or failed to publish");
    std::cout << "startup_recovery executable_display=PASS exact_text_and_order=PASS scratch_clear=PASS display_unavailable=PASS\n";
}

int main() {
    try {
        static_assert(sizeof(GameModeConfig::name) > 0);
        index_matrix();
        invalid_start_and_post_selector();
        valid_routes();
        failure_containment();
        decoder_and_persisted_refusal();
        executable_recovery_refusal();
        std::cout << "gp_config023_usb_index_validation: PASS (host-only; no hardware claim)\n";
        return 0;
    } catch (const std::exception &error) {
        std::cerr << error.what() << '\n';
        return 1;
    }
}
