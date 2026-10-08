#include "host_stubs.hpp"

#if defined(EXPECT_SHORT_ENUM)
static_assert(sizeof(GameModeId) == 1);
static_assert(sizeof(CommunicationBackendId) == 1);
#else
static_assert(sizeof(GameModeId) == sizeof(int));
static_assert(sizeof(CommunicationBackendId) == sizeof(int));
#endif

#include <cstdio>
#include <cstring>

WatchdogState watchdog_storage{};
WatchdogState *watchdog_hw = &watchdog_storage;
std::vector<std::string> effects;
size_t current_mode_index = SIZE_MAX;
KeyboardMode *current_kb_mode = nullptr;
StubMode melee_mode, projectm_mode, ultimate_mode, fgc_mode;
StubMode rivals_mode, rivals2_mode, custom_mode, s64_mode;
KeyboardMode keyboard_mode;
bool terminate_reboot = false;

void tud_disconnect() { effects.emplace_back("disconnect"); }
void delay(uint32_t milliseconds) {
    effects.emplace_back("delay:" + std::to_string(milliseconds));
}
void reboot_firmware() {
    effects.emplace_back("reboot");
    if (terminate_reboot) throw 7;
}

#include "production_methods.inc"

namespace {
int failures = 0;

#define CHECK(condition) do { \
    if (!(condition)) { \
        std::fprintf(stderr, "FAIL line %d: %s\n", __LINE__, #condition); \
        ++failures; \
    } \
} while (false)

bool same_config(const Config &left, const Config &right) {
    if (left.game_mode_configs_count != right.game_mode_configs_count ||
        left.communication_backend_configs_count != right.communication_backend_configs_count ||
        left.keyboard_modes_count != right.keyboard_modes_count ||
        left.custom_modes_count != right.custom_modes_count ||
        left.melee_options != right.melee_options ||
        left.project_m_options != right.project_m_options) {
        return false;
    }
    for (size_t i = 0; i < 30; ++i) {
        const GameModeConfig &a = left.game_mode_configs[i];
        const GameModeConfig &b = right.game_mode_configs[i];
        if (std::memcmp(a.name, b.name, sizeof(a.name)) != 0 ||
            a.keyboard_mode_config != b.keyboard_mode_config || a.mode_id != b.mode_id ||
            a.custom_mode_config != b.custom_mode_config) return false;
    }
    for (size_t i = 0; i < 15; ++i) {
        if (left.communication_backend_configs[i].backend_id !=
            right.communication_backend_configs[i].backend_id) return false;
    }
    for (size_t i = 0; i < 10; ++i) {
        if (left.keyboard_modes[i] != right.keyboard_modes[i] ||
            left.custom_modes[i] != right.custom_modes[i]) return false;
    }
    return true;
}

void reset_effects() {
    effects.clear();
    watchdog_hw->scratch[0].value = 91;
    watchdog_hw->scratch[1].value = 92;
    terminate_reboot = false;
}

void set_name(GameModeConfig &row, const char *name) {
    std::memset(row.name, 0, sizeof(row.name));
    std::strncpy(row.name, name, sizeof(row.name) - 1);
}

void prepare_config(Config &config, size_t profiles = 4, size_t backends = 3) {
    config = Config{};
    config.game_mode_configs_count = profiles;
    config.communication_backend_configs_count = backends;
    config.keyboard_modes_count = 1;
    config.custom_modes_count = 1;
    const GameModeId controller_modes[] = {
        MODE_ULTIMATE, MODE_FGC, MODE_RIVALS_OF_AETHER, MODE_RIVALS2,
    };
    for (size_t i = 0; i < 4; ++i) {
        std::snprintf(config.game_mode_configs[i].name,
                      sizeof(config.game_mode_configs[i].name), "profile-%zu", i);
        config.game_mode_configs[i].mode_id = controller_modes[i];
    }
}

void select_via_actual_mode_setup(GameModeConfig &row, Config &config,
                                  CommunicationBackend &backend, InputMode *&active) {
    current_mode_index = SIZE_MAX;
    set_mode(&backend, row, config);
    active = backend.CurrentGameMode();
    CHECK(active != nullptr);
    CHECK(active != nullptr && active->GetConfig() == &row);
    CHECK(current_mode_index == SIZE_MAX);
}

void expect_refusal(Config &config, const Config &before,
                    IntegratedDisplay &display, uint8_t backend_index = 0) {
    ConfigMenu menu;
    reset_effects();
    DefaultConfigMenu::SetUsbBackend(&display, &menu, config, backend_index);
    CHECK(effects.empty());
    CHECK(watchdog_hw->scratch[0].value == 91);
    CHECK(watchdog_hw->scratch[1].value == 92);
    CHECK(same_config(config, before));
}

void expect_match(Config &config, size_t selected_row, uint8_t backend_index,
                  CommunicationBackendId backend_id = COMMS_BACKEND_XINPUT,
                  bool terminating_reboot = false) {
    CommunicationBackend backend(backend_id);
    InputMode *active = nullptr;
    select_via_actual_mode_setup(config.game_mode_configs[selected_row], config, backend, active);
    IntegratedDisplay display(&backend);
    ConfigMenu menu;
    const Config before = config;
    reset_effects();
    terminate_reboot = terminating_reboot;
    bool reboot_terminated = false;
    try {
        DefaultConfigMenu::SetUsbBackend(&display, &menu, config, backend_index);
    } catch (int signal) {
        CHECK(signal == 7);
        reboot_terminated = true;
    }
    CHECK(reboot_terminated == terminating_reboot);
    const std::vector<std::string> expected{
        "disconnect", "delay:500",
        "scratch:1=" + std::to_string(selected_row + 1),
        "scratch:0=" + std::to_string(static_cast<unsigned>(backend_index) + 1),
        "delay:30", "reboot"};
    CHECK(effects == expected);
    CHECK(watchdog_hw->scratch[1].value == selected_row + 1);
    CHECK(watchdog_hw->scratch[0].value == static_cast<unsigned>(backend_index) + 1);
    CHECK(same_config(config, before));
    CHECK(active != nullptr && active->GetConfig() == &config.game_mode_configs[selected_row]);
}

void test_unique_rows_duplicates_and_reordering() {
    Config config{};
    prepare_config(config);
    for (size_t i = 0; i < config.game_mode_configs_count; ++i) {
        expect_match(config, i, static_cast<uint8_t>(i % config.communication_backend_configs_count));
    }

    // Every row is independently selectable when names and mode IDs collide.
    for (size_t i = 0; i < config.game_mode_configs_count; ++i) {
        for (auto &row : config.game_mode_configs) set_name(row, "duplicate");
        for (auto &row : config.game_mode_configs) row.mode_id = MODE_ULTIMATE;
        expect_match(config, i, 1);
    }

    // Every row remains addressable when all configured names are empty.
    for (auto &row : config.game_mode_configs) set_name(row, "");
    for (size_t i = 0; i < config.game_mode_configs_count; ++i) expect_match(config, i, 2);

    // Reordered rows follow the live pointer, not the prior menu order or mode ID.
    const GameModeConfig reordered[4] = {
        config.game_mode_configs[2], config.game_mode_configs[0],
        config.game_mode_configs[3], config.game_mode_configs[1]};
    std::memcpy(config.game_mode_configs, reordered, sizeof(reordered));
    for (size_t i = 0; i < config.game_mode_configs_count; ++i) expect_match(config, i, 0);
}

void test_controller_keyboard_empty_orderings_and_raw_name_bytes() {
    Config config{};
    prepare_config(config, 2, 2);
    // Both controller/Keyboard row orderings are accepted, including empty names.
    for (int keyboard_first = 0; keyboard_first < 2; ++keyboard_first) {
        for (auto &row : config.game_mode_configs) set_name(row, "");
        config.game_mode_configs[0].mode_id = keyboard_first ? MODE_KEYBOARD : MODE_ULTIMATE;
        config.game_mode_configs[1].mode_id = keyboard_first ? MODE_ULTIMATE : MODE_KEYBOARD;
        config.game_mode_configs[0].keyboard_mode_config = 1;
        config.game_mode_configs[1].keyboard_mode_config = 1;
        expect_match(config, 0, 0, COMMS_BACKEND_DINPUT);
        expect_match(config, 1, 1, COMMS_BACKEND_DINPUT);
    }

    // Seventeen-byte names and nonzero bytes after an embedded NUL do not define identity.
    for (auto &row : config.game_mode_configs) {
        std::memset(row.name, 'A', 17);
        row.name[17] = '\0';
    }
    config.game_mode_configs[0].name[16] = '\0';
    config.game_mode_configs[0].name[17] = 'X';
    config.game_mode_configs[1].name[16] = '\0';
    config.game_mode_configs[1].name[17] = 'Y';
    expect_match(config, 0, 0, COMMS_BACKEND_DINPUT);
    expect_match(config, 1, 1, COMMS_BACKEND_DINPUT);
}

void test_refusals_and_reboot_return_modes() {
    Config config{};
    prepare_config(config, 3, 2);
    CommunicationBackend backend;
    InputMode *active = nullptr;
    select_via_actual_mode_setup(config.game_mode_configs[0], config, backend, active);
    IntegratedDisplay display(&backend);
    ConfigMenu menu;
    const Config baseline = config;

    expect_refusal(config, baseline, display, 2);
    reset_effects();
    DefaultConfigMenu::SetUsbBackend(nullptr, &menu, config, 0);
    CHECK(effects.empty());

    CommunicationBackend no_mode_backend;
    IntegratedDisplay no_mode_display(&no_mode_backend);
    expect_refusal(config, baseline, no_mode_display);

    InputMode no_config_mode;
    CommunicationBackend no_config_backend;
    no_config_backend.SetGameMode(&no_config_mode);
    IntegratedDisplay no_config_display(&no_config_backend);
    expect_refusal(config, baseline, no_config_display);

    InputMode detached_mode;
    GameModeConfig detached_row{};
    detached_mode.SetConfig(detached_row);
    CommunicationBackend detached_backend;
    detached_backend.SetGameMode(&detached_mode);
    IntegratedDisplay detached_display(&detached_backend);
    expect_refusal(config, baseline, detached_display);

    reset_effects();
    config.game_mode_configs_count = 0;
    const Config zero_profiles = config;
    DefaultConfigMenu::SetUsbBackend(&display, &menu, config, 0);
    CHECK(effects.empty() && same_config(config, zero_profiles));
    config = baseline;

    reset_effects();
    config.communication_backend_configs_count = 0;
    const Config zero_backends = config;
    DefaultConfigMenu::SetUsbBackend(&display, &menu, config, 0);
    CHECK(effects.empty() && same_config(config, zero_backends));
    config = baseline;

    reset_effects();
    config.game_mode_configs_count = 31;
    const Config excessive_profiles = config;
    DefaultConfigMenu::SetUsbBackend(&display, &menu, config, 0);
    CHECK(effects.empty() && same_config(config, excessive_profiles));
    config = baseline;

    reset_effects();
    config.communication_backend_configs_count = 16;
    const Config excessive_backends = config;
    DefaultConfigMenu::SetUsbBackend(&display, &menu, config, 0);
    CHECK(effects.empty() && same_config(config, excessive_backends));
    config = baseline;

    expect_match(config, 2, 1, COMMS_BACKEND_DINPUT, false);
    expect_match(config, 2, 1, COMMS_BACKEND_DINPUT, true);
}
}  // namespace

int main() {
    test_unique_rows_duplicates_and_reordering();
    test_controller_keyboard_empty_orderings_and_raw_name_bytes();
    test_refusals_and_reboot_return_modes();
    if (failures != 0) return 1;
    std::puts("C024 selector identity host proof: PASS; actual mode setup, row identity, no-effects refusals and reboot actions verified");
    return 0;
}
