#include "include/host_stubs.hpp"
#include <array>
#include <iostream>
#include "production_fragments.inc"

static void require(bool condition, const char *message) {
    if (!condition) throw std::runtime_error(message);
}
static void reset() {
    Scratch::events = nullptr;
    watchdog.scratch[0] = 0; watchdog.scratch[1] = 0;
    events.clear(); Scratch::events = &events;
    returning_reboot = false; rebooted = false;
    persistence.saves = 0; selected_mode = nullptr;
}
static void row(const std::string &id, const std::string &observation) {
    std::cout << id << " " << observation << '\n';
}
static void varint(std::vector<uint8_t> &out, uint64_t value) {
    while (value >= 128) { out.push_back((value & 127) | 128); value >>= 7; }
    out.push_back(value);
}
static void scalar(std::vector<uint8_t> &out, unsigned tag, uint64_t value) {
    varint(out, uint64_t{tag} << 3); varint(out, value);
}
static void bytes(std::vector<uint8_t> &out, unsigned tag, const std::vector<uint8_t> &payload) {
    varint(out, (uint64_t{tag} << 3) | 2); varint(out, payload.size());
    out.insert(out.end(), payload.begin(), payload.end());
}
struct WireMode { GameModeId id; std::vector<uint8_t> name; bool keyboard = false; };
static std::vector<uint8_t> string_bytes(const char *name) {
    return {name, name + std::strlen(name)};
}
static void configure_wire(const std::vector<WireMode> &modes) {
    wire.clear();
    for (const auto &mode : modes) {
        std::vector<uint8_t> payload;
        scalar(payload, 1, mode.id); bytes(payload, 2, mode.name);
        if (mode.keyboard) scalar(payload, 7, 1);
        scalar(payload, 201, COMMS_BACKEND_DINPUT);
        if (!mode.keyboard) {
            scalar(payload, 201, COMMS_BACKEND_XINPUT);
            scalar(payload, 201, COMMS_BACKEND_NINTENDO_SWITCH);
        }
        bytes(wire, 1, payload);
    }
    for (auto id : {COMMS_BACKEND_XINPUT, COMMS_BACKEND_DINPUT, COMMS_BACKEND_NINTENDO_SWITCH}) {
        std::vector<uint8_t> payload; scalar(payload, 1, id); scalar(payload, 2, 1);
        bytes(wire, 2, payload);
    }
    bytes(wire, 4, {}); scalar(wire, 6, 1); scalar(wire, 7, 1);
}
static Config admitted(const std::vector<WireMode> &modes) {
    configure_wire(modes);
    static Config live = Config_init_zero, loaded = Config_init_zero;
    ConfiguratorBackend backend(live);
    require(backend.HandleSetConfig() && backend.result == CMD_SUCCESS && persistence.saves == 1,
            "production SET_CONFIG did not admit wire");
    require(persistence.LoadConfig(loaded), "production LoadConfig did not decode wire");
    require(live.game_mode_configs_count == loaded.game_mode_configs_count &&
        live.communication_backend_configs_count == loaded.communication_backend_configs_count &&
        live.default_usb_backend_config == loaded.default_usb_backend_config,
        "SET/LOAD decoded indices mismatch");
    for (size_t i = 0; i < live.game_mode_configs_count; ++i) {
        const auto &a = live.game_mode_configs[i]; const auto &b = loaded.game_mode_configs[i];
        require(a.mode_id == b.mode_id && a.keyboard_mode_config == b.keyboard_mode_config &&
            std::memcmp(a.name, b.name, 18) == 0 &&
            a.applicable_backends_count == b.applicable_backends_count,
            "SET/LOAD decoded name/mode mismatch");
    }
    return live;
}
static std::vector<unsigned> menu_keys(Config &config, size_t current) {
    GameMode mode{&config.game_mode_configs[current]}; CommunicationBackend backend{&mode};
    CommunicationBackend *backends[]{&backend}; DefaultConfigMenu menu(backends);
    menu.BuildUsbPage(config);
    std::vector<unsigned> result;
    for (size_t i = 0; i < menu._usb_backends_page.items_count; ++i) {
        auto &item = menu._usb_backends_page.items[i];
        require(item.action == &DefaultConfigMenu::SetUsbBackend, "menu action is not production selector");
        result.push_back(item.key);
    }
    return result;
}
static bool select(Config &config, size_t current, uint8_t backend, bool through_menu = true) {
    GameMode mode{&config.game_mode_configs[current]}; IntegratedDisplay display{&mode};
    CommunicationBackend comms{&mode}; CommunicationBackend *backends[]{&comms}; DefaultConfigMenu menu(backends);
    if (through_menu) {
        menu.BuildUsbPage(config);
        for (size_t i = 0; i < menu._usb_backends_page.items_count; ++i) {
            auto &item = menu._usb_backends_page.items[i];
            if (item.key == backend) {
                try { item.action(&display, &menu, config, item.key); }
                catch (const RebootStop &) { return true; }
                return false;
            }
        }
        throw std::runtime_error("requested backend is not offered by ordinary menu");
    }
    try { DefaultConfigMenu::SetUsbBackend(&display, &menu, config, backend); }
    catch (const RebootStop &) { return true; }
    return false;
}
static void expected_trace(unsigned backend, unsigned mode) {
    require(events == std::vector<std::string>{"disconnect", "delay=500",
        "scratch1=" + std::to_string(mode), "scratch0=" + std::to_string(backend),
        "delay=30", "reboot"}, "scratch/reboot trace mismatch");
}
static CommunicationBackend primary{nullptr};
static void init_primary(CommunicationBackend *&out, CommunicationBackendId, InputState &,
                         InputSource **, size_t, Config &, const Pinout &) { out = &primary; }
static CommunicationBackendId detect(const Pinout &) { return COMMS_BACKEND_XINPUT; }
static size_t init_secondary(CommunicationBackend **&out, CommunicationBackend *&backend,
                            CommunicationBackendId, InputState &, InputSource **, size_t, Config &, const Pinout &) {
    static CommunicationBackend *storage[1]; storage[0] = backend; out = storage; return 1;
}
static void consume_scratch(Config &config, unsigned backend, unsigned mode) {
    rebooted = true; CommunicationBackend **backends = nullptr; InputState inputs{}; Pinout pinout{};
    require(initialize_backends(backends, inputs, nullptr, 0, config, pinout,
        get_backend_config_default, get_usb_backend_config_default, detect,
        init_secondary, init_primary) == 1, "watchdog initializer failed");
    require(config.default_usb_backend_config == backend &&
        config.communication_backend_configs[backend - 1].default_mode_config == mode &&
        selected_mode == &config.game_mode_configs[mode - 1] && persistence.saves == 1,
        "production watchdog consumer selected a different row");
}
int main() {
    try {
        static_assert(sizeof(GameModeConfig::name) == 18);
        static_assert(sizeof(Button) == 1);
        reset(); static Config defaults = glyph_default_config();
        require(defaults.game_mode_configs_count == 13, "default mode count");
        unsigned empty = 0;
        for (size_t i = 0; i < 13; ++i) {
            empty += defaults.game_mode_configs[i].name[0] == 0;
            for (size_t j = i + 1; j < 13; ++j)
                require(!sameName(defaults.game_mode_configs[i].name, defaults.game_mode_configs[j].name),
                        "default names collide");
        }
        require(empty == 1 && defaults.game_mode_configs[12].mode_id == MODE_KEYBOARD, "default empty name");
        require(menu_keys(defaults, 0) == std::vector<unsigned>{0, 1, 2}, "controller USB options");
        require(menu_keys(defaults, 12) == std::vector<unsigned>{1}, "Keyboard USB options");
        row("defaults", "unique=13 nonempty=12 empty_keyboard=1 controller_menu=0,1,2 keyboard_menu=1");
        unsigned defaults_tested = 0;
        for (size_t i = 0; i < 13; ++i) {
            for (auto backend : menu_keys(defaults, i)) {
                reset(); require(select(defaults, i, backend), "default selector did not reboot");
                expected_trace(backend + 1, i + 1); ++defaults_tested;
            }
        }
        row("default_selection", "cases=" + std::to_string(defaults_tested) + " exact_current_index=PASS");

        reset(); static Config duplicate = admitted({{MODE_MELEE, string_bytes("same")},
            {MODE_ULTIMATE, string_bytes("same")}, {MODE_PROJECT_M, string_bytes("same")},
            {MODE_KEYBOARD, {}, true}});
        row("accept_duplicate", "set=PASS load=PASS names_equal=1");
        for (size_t current = 0; current < 3; ++current) {
            for (unsigned backend = 0; backend < 3; ++backend) {
                reset(); require(select(duplicate, current, backend), "duplicate selector did not reboot");
                expected_trace(backend + 1, 1); consume_scratch(duplicate, backend + 1, 1);
            }
        }
        row("duplicate_selection", "current=0,1,2 backends=0,1,2 selected=0 reboot_calls=1 watchdog_mode=1");
        reset(); returning_reboot = true;
        require(!select(duplicate, 1, 1), "returning reboot unexpectedly terminated");
        require(events.size() == 18 && watchdog.scratch[1].value == 3, "returning reboot continuation");
        row("returning_reboot_double", "reboot_calls=3 final_mode=3 physical_reachability=UNKNOWN");

        reset(); static Config empty_names = admitted({{MODE_MELEE, {}}, {MODE_KEYBOARD, {}, true}});
        row("accept_empty", "set=PASS load=PASS");
        reset(); require(select(empty_names, 1, 1), "Keyboard DInput did not reboot");
        expected_trace(2, 1); consume_scratch(empty_names, 2, 1);
        row("keyboard_empty_collision", "offered_backend=1 current=1 selected=0 selected_mode=controller");

        reset(); static Config kb_first = admitted({{MODE_KEYBOARD, string_bytes("same"), true},
            {MODE_ULTIMATE, string_bytes("same")}});
        for (unsigned backend : {0u, 2u}) {
            reset(); require(select(kb_first, 1, backend), "controller crossbackend did not reboot");
            expected_trace(backend + 1, 1); consume_scratch(kb_first, backend + 1, 1);
        }
        row("controller_keyboard_collision", "current=1 offered_backends=0,2 selected=0 selected_mode=keyboard set_mode_boundary=STUB");
        reset(); require(select(kb_first, 0, 0, false), "injected Keyboard XInput selector");
        row("injected_keyboard_xinput", "ordinary_menu=NOT_OFFERED direct_call=REBOOT");

        // All eighteen positions, including bytes following an embedded NUL, matter.
        std::array<char, 18> left{}, right{}; left.fill('a'); right = left;
        require(sameName(left.data(), right.data()), "18-byte identical injected names");
        for (size_t i = 0; i < 18; ++i) {
            right = left; right[i] = 'b';
            require(!sameName(left.data(), right.data()), "18-byte differing position ignored");
        }
        left.fill(0); right = left; right[17] = 'z';
        require(!sameName(left.data(), right.data()), "post-NUL byte ignored");
        row("same_name_matrix", "equal18=PASS differing_positions=18 post_nul=COMPARED all_nonzero=INJECTED");
        const std::vector<uint8_t> name17(17, 'a'), name16(16, 'a');
        reset(); static Config lengths = admitted({{MODE_MELEE, name17}, {MODE_ULTIMATE, name16}});
        require(lengths.game_mode_configs[0].name[17] == 0 && lengths.game_mode_configs[1].name[16] == 0,
                "accepted decoder termination");
        reset(); require(select(lengths, 1, 0), "length16 selector"); expected_trace(1, 2);
        row("boundary17", "set=PASS load=PASS terminator17=0 length16_different=1 selected=1");
        configure_wire({{MODE_MELEE, std::vector<uint8_t>(18, 'a')}});
        static Config rejected = Config_init_zero; ConfiguratorBackend invalid(rejected);
        reset(); require(!invalid.HandleSetConfig() && persistence.saves == 0 && !persistence.LoadConfig(rejected),
                         "18-byte wire string not rejected");
        row("boundary18", "set=REJECT load=REJECT saves=0");
        reset(); static Config embedded = admitted({{MODE_MELEE, {'a', 0, 'x'}},
            {MODE_ULTIMATE, {'a', 0, 'y'}}});
        require(!sameName(embedded.game_mode_configs[0].name, embedded.game_mode_configs[1].name), "embedded NUL equality");
        reset(); require(select(embedded, 1, 0), "embedded-NUL selector"); expected_trace(1, 2);
        row("embedded_nul", "set=PASS load=PASS displayed_prefix_equal=1 suffix_different=1 selected=1");

        reset(); static Config no_match = defaults; GameMode external{&no_match.game_mode_configs[0]};
        std::memset(no_match.game_mode_configs[0].name, 'x', 18);
        GameModeConfig detached = defaults.game_mode_configs[0]; external.config = &detached;
        IntegratedDisplay display{&external}; DefaultConfigMenu::SetUsbBackend(&display, nullptr, no_match, 0);
        require(events.empty(), "no-match injected state caused reboot");
        row("injected_no_match", "events=0 reachability=UNKNOWN");
        reset(); static Config zero_profiles = Config_init_zero;
        zero_profiles.communication_backend_configs_count = 1;
        watchdog.scratch[0].value = 91; watchdog.scratch[1].value = 92;
        DefaultConfigMenu::SetUsbBackend(&display, nullptr, zero_profiles, 0);
        require(events.empty() && watchdog.scratch[0].value == 91 && watchdog.scratch[1].value == 92,
                "zero-profile injected Config changed scratch");
        row("injected_zero_profiles", "events=0 scratch_sentinels=UNCHANGED reachability=UNKNOWN");
        unsigned rejected_indices = 0;
        for (unsigned i = defaults.communication_backend_configs_count; i < 256; ++i) {
            reset(); require(!select(defaults, 0, i, false) && events.empty(), "out-of-range backend wrote scratch");
            ++rejected_indices;
        }
        row("backend_bounds", "invalid_count_to255=" + std::to_string(rejected_indices) + " events=0");
        reset(); IntegratedDisplay null_display{nullptr};
        watchdog.scratch[0].value = 91; watchdog.scratch[1].value = 92;
        DefaultConfigMenu::SetUsbBackend(&null_display, nullptr, defaults, defaults.communication_backend_configs_count);
        require(events.empty() && watchdog.scratch[0].value == 91 && watchdog.scratch[1].value == 92,
                "bounds guard did not precede null current dereference");
        row("injected_invalid_backend_null_current", "events=0 scratch_sentinels=UNCHANGED");
        row("result", "PASS H1 host_only hardware=NOT_CLAIMED");
        return 0;
    } catch (const std::exception &error) {
        std::cerr << error.what() << '\n'; return 1;
    }
}
