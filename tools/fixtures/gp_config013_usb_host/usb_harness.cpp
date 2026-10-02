#include <config.pb.h>
#include <pb_common.h>
#include <pb_decode.h>

#include <array>
#include <cstdint>
#include <iostream>
#include <string>
#include <vector>

struct InputState { uint64_t buttons = 0; };
struct InputSource {};
struct Pinout { int unused = 0; };
class CommunicationBackend {};

using backend_config_selector_t = void (*)(CommunicationBackendConfig &, const InputState &, Config &);
using usb_backend_getter_t = void (*)(CommunicationBackendConfig &, const Config &);
using primary_backend_initializer_t = void (*)(CommunicationBackend *&, CommunicationBackendId,
    InputState &, InputSource **, size_t, Config &, const Pinout &);
using secondary_backend_initializer_t = size_t (*)(CommunicationBackend **&, CommunicationBackend *&,
    CommunicationBackendId, InputState &, InputSource **, size_t, Config &, const Pinout &);
using detect_console_t = CommunicationBackendId (*)(const Pinout &);

CommunicationBackendConfig backend_config_from_buttons(const InputState &, const CommunicationBackendConfig *, size_t);
CommunicationBackendConfig backend_config_from_id(CommunicationBackendId, const CommunicationBackendConfig *, size_t);
uint64_t make_button_mask(const Button *, size_t);
bool all_buttons_held(const uint64_t &, uint64_t);
bool rebooted = false;
struct Watchdog { uint32_t scratch[2]{}; } watchdog_storage;
Watchdog *watchdog_hw = &watchdog_storage;
bool watchdog_caused_reboot() { return rebooted; }
struct PersistenceStub { unsigned saves = 0; void SaveConfig(Config &) { ++saves; } } persistence;
std::vector<CommunicationBackendId> primary_calls;
std::vector<unsigned> modes_set;
CommunicationBackend primary_storage;
CommunicationBackend *primary_pointer = nullptr;

void init_primary_mock(CommunicationBackend *&primary, CommunicationBackendId id,
                       InputState &, InputSource **, size_t, Config &, const Pinout &) {
    primary_calls.push_back(id);
    primary = &primary_storage;
}
size_t init_secondary_mock(CommunicationBackend **&backends, CommunicationBackend *&primary,
                           CommunicationBackendId, InputState &, InputSource **, size_t,
                           Config &, const Pinout &) {
    backends = new CommunicationBackend *[1]{primary};
    return 1;
}
CommunicationBackendId detected = COMMS_BACKEND_UNSPECIFIED;
CommunicationBackendId detect_mock(const Pinout &) { return detected; }
void set_mode(CommunicationBackend *, GameModeConfig &mode, Config &) { modes_set.push_back(mode.mode_id); }

#include "production_fragments.inc"

namespace {
void varint(std::vector<uint8_t> &out, uint64_t value) {
    while (value >= 0x80) { out.push_back(static_cast<uint8_t>((value & 0x7f) | 0x80)); value >>= 7; }
    out.push_back(static_cast<uint8_t>(value));
}
void field(std::vector<uint8_t> &out, uint32_t tag, uint64_t value) {
    varint(out, (uint64_t{tag} << 3)); varint(out, value);
}
void bytes(std::vector<uint8_t> &out, uint32_t tag, const std::vector<uint8_t> &value) {
    varint(out, (uint64_t{tag} << 3) | 2); varint(out, value.size());
    out.insert(out.end(), value.begin(), value.end());
}
std::vector<uint8_t> backend(uint32_t id, uint32_t mode) {
    std::vector<uint8_t> value; field(value, 1, id); field(value, 2, mode); return value;
}
bool decode(const std::vector<uint8_t> &wire, Config &config) {
    pb_istream_t stream = pb_istream_from_buffer(wire.data(), wire.size());
    return pb_decode(&stream, Config_fields, &config);
}
bool decode_case(const std::string &name, std::vector<uint8_t> wire, uint8_t seed = 0) {
    Config config = Config_init_zero; config.default_usb_backend_config = seed;
    bool ok = decode(wire, config);
    std::cout << "decode=" << name << " result=" << (ok ? "accept" : "reject")
              << " usb=" << static_cast<unsigned>(config.default_usb_backend_config)
              << " backends=" << config.communication_backend_configs_count << '\n';
    return ok;
}
void reset_runtime() {
    primary_calls.clear(); modes_set.clear(); primary_pointer = nullptr;
    persistence.saves = 0; rebooted = false; watchdog_hw->scratch[0] = watchdog_hw->scratch[1] = 0;
}
Config sample_config() {
    Config c = Config_init_zero;
    c.communication_backend_configs_count = 4;
    c.communication_backend_configs[0].backend_id = COMMS_BACKEND_XINPUT;
    c.communication_backend_configs[0].default_mode_config = 1;
    c.communication_backend_configs[0].activation_binding_count = 1;
    c.communication_backend_configs[0].activation_binding[0] = BTN_LF1;
    c.communication_backend_configs[1].backend_id = COMMS_BACKEND_DINPUT;
    c.communication_backend_configs[1].default_mode_config = 1;
    c.communication_backend_configs[1].activation_binding_count = 1;
    c.communication_backend_configs[1].activation_binding[0] = BTN_RF3;
    c.communication_backend_configs[2].backend_id = COMMS_BACKEND_NINTENDO_SWITCH;
    c.communication_backend_configs[2].default_mode_config = 3;
    c.communication_backend_configs[2].activation_binding_count = 1;
    c.communication_backend_configs[2].activation_binding[0] = BTN_RF2;
    c.communication_backend_configs[3].backend_id = COMMS_BACKEND_GAMECUBE;
    c.communication_backend_configs[3].default_mode_config = 1;
    c.game_mode_configs_count = 11;
    c.game_mode_configs[0].mode_id = MODE_MELEE;
    c.game_mode_configs[1].mode_id = MODE_PROJECT_M;
    c.game_mode_configs[2].mode_id = MODE_ULTIMATE;
    c.game_mode_configs[10].mode_id = MODE_KEYBOARD;
    c.game_mode_configs[10].keyboard_mode_config = 1;
    c.keyboard_modes_count = 1;
    c.default_usb_backend_config = 1;
    return c;
}
bool route_case(const std::string &name, uint64_t buttons, CommunicationBackendId detected_id,
                bool watchdog, uint32_t scratch0 = 0, uint32_t scratch1 = 0) {
    reset_runtime();
    Config c = sample_config(); InputState inputs{buttons}; Pinout pinout{};
    if (name == "button_hold_keyboard_dinput")
        c.communication_backend_configs[1].default_mode_config = 11;
    CommunicationBackend **backends = nullptr; InputSource **sources = nullptr;
    detected = detected_id; rebooted = watchdog;
    watchdog_hw->scratch[0] = scratch0; watchdog_hw->scratch[1] = scratch1;
    size_t count = initialize_backends(backends, inputs, sources, 0, c, pinout,
        get_backend_config_default, get_usb_backend_config_default, detect_mock,
        init_secondary_mock, init_primary_mock);
    std::cout << "route=" << name << " count=" << count << " primary=";
    for (size_t i = 0; i < primary_calls.size(); ++i) std::cout << (i ? "," : "") << primary_calls[i];
    std::cout << " mode=" << (modes_set.empty() ? 0 : modes_set.back())
              << " detected=" << detected_id << " saves=" << persistence.saves << '\n';
    delete[] backends;
    return count == 1;
}
}

int main() {
    unsigned valid = 0, invalid = 0;
    for (unsigned count = 0; count <= 15; ++count) {
        Config c = Config_init_zero; c.communication_backend_configs_count = count;
        for (unsigned i = 0; i < count; ++i) {
            c.communication_backend_configs[i].backend_id = static_cast<CommunicationBackendId>((i % 7) + 1);
            c.communication_backend_configs[i].default_mode_config = static_cast<uint8_t>(i + 1);
        }
        for (unsigned index = 0; index <= 255; ++index) {
            CommunicationBackendConfig out = CommunicationBackendConfig_init_zero;
            out.backend_id = COMMS_BACKEND_SNES; out.default_mode_config = 77;
            c.default_usb_backend_config = static_cast<uint8_t>(index);
            get_usb_backend_config_default(out, c);
            const bool in_range = index > 0 && index <= count;
            const auto expected = in_range ? c.communication_backend_configs[index - 1].backend_id : COMMS_BACKEND_SNES;
            const auto expected_mode = in_range ? c.communication_backend_configs[index - 1].default_mode_config : 77;
            if (out.backend_id != expected || out.default_mode_config != expected_mode) return 10;
            in_range ? ++valid : ++invalid;
        }
    }
    std::cout << "getter_matrix indices=0..255 counts=0..15 valid=" << valid << " invalid=" << invalid << "\n";

    std::vector<uint8_t> omitted;
    bytes(omitted, 2, backend(COMMS_BACKEND_XINPUT, 1));
    decode_case("omitted_tag7", omitted);
    std::vector<uint8_t> repeated; field(repeated, 7, 2); field(repeated, 7, 1);
    decode_case("repeated_tag7", repeated);
    std::vector<uint8_t> overflow; field(overflow, 7, 256);
    decode_case("uint8_overflow_256", overflow);
    std::vector<uint8_t> malformed = omitted; field(malformed, 7, 2); malformed.push_back(0x38); malformed.push_back(0x80);
    decode_case("partial_malformed_trailing", malformed, 9);
    std::vector<uint8_t> bad_wire_type; varint(bad_wire_type, (7u << 3) | 2); bad_wire_type.push_back(1); bad_wire_type.push_back(0);
    decode_case("malformed_tag7_wire_type", bad_wire_type);
    std::vector<uint8_t> overlong; varint(overlong, 7u << 3); overlong.insert(overlong.end(), 10, 0x80);
    decode_case("malformed_overlong_varint", overlong);
    std::vector<uint8_t> count16;
    for (unsigned i = 0; i < 16; ++i) bytes(count16, 2, backend(COMMS_BACKEND_XINPUT, 1));
    decode_case("backend_count_16", count16);

    route_case("usb_detect_xinput", 0, COMMS_BACKEND_XINPUT, false);
    route_case("usb_detect_dinput", 0, COMMS_BACKEND_DINPUT, false);
    route_case("usb_detect_switch", 0, COMMS_BACKEND_NINTENDO_SWITCH, false);
    route_case("configurator_detect", 0, COMMS_BACKEND_CONFIGURATOR, false);
    route_case("gc_preliminary_usb", 0, COMMS_BACKEND_GAMECUBE, false);
    route_case("button_hold_dinput", uint64_t{1} << (BTN_RF3 - 1), COMMS_BACKEND_XINPUT, false);
    route_case("button_hold_switch", uint64_t{1} << (BTN_RF2 - 1), COMMS_BACKEND_XINPUT, false);
    route_case("button_hold_keyboard_dinput", uint64_t{1} << (BTN_RF3 - 1), COMMS_BACKEND_XINPUT, false);
    route_case("watchdog_override", uint64_t{1} << (BTN_RF3 - 1), COMMS_BACKEND_XINPUT, true, 0, 2);
    route_case("undetected_console", 0, COMMS_BACKEND_UNSPECIFIED, false);
}
