#include <cstddef>
#include <cstdint>
#include <iostream>
#include <stdexcept>
#include <string>

#include "config.pb.h"

struct InputState {
    uint64_t buttons = 0;
    bool lt1 = false;
    bool lt2 = false;
    bool mb1 = false;
    bool mb2 = false;
};

class InputMode {
  public:
    virtual ~InputMode() = default;
};
class ControllerMode : public InputMode {};
class KeyboardMode : public InputMode {};

class CommunicationBackend {
  public:
    explicit CommunicationBackend(InputState &inputs) : inputs_(inputs) {}
    InputState &GetInputs() { return inputs_; }
    CommunicationBackendId BackendId() { return COMMS_BACKEND_XINPUT; }
    void SetGameMode(InputMode *mode) { last_mode = mode; ++set_calls; }
    InputMode *last_mode = nullptr;
    size_t set_calls = 0;

  private:
    InputState &inputs_;
};

#define DEFINE_MODE(name, base) \
    class name : public base { \
      public: \
        template <typename... Args> void SetConfig(Args &&...) {} \
    }
DEFINE_MODE(Melee20Button, ControllerMode);
DEFINE_MODE(ProjectM, ControllerMode);
DEFINE_MODE(Ultimate, ControllerMode);
DEFINE_MODE(FgcMode, ControllerMode);
DEFINE_MODE(RivalsOfAether, ControllerMode);
DEFINE_MODE(Rivals2, ControllerMode);
DEFINE_MODE(CustomKeyboardMode, KeyboardMode);
DEFINE_MODE(CustomControllerMode, ControllerMode);
DEFINE_MODE(Smash64, ControllerMode);
DEFINE_MODE(SenscopePrototype, ControllerMode);
#undef DEFINE_MODE

namespace senscope::prototype {
constexpr bool kEnableSenscopePrototypeManualSelection = false;
}

KeyboardMode *current_kb_mode = nullptr;
void set_mode(CommunicationBackend *, ControllerMode *);
void set_mode(CommunicationBackend *, KeyboardMode *);
void set_mode(CommunicationBackend *, GameModeConfig &, Config &);
void set_mode(CommunicationBackend *, GameModeId, Config &);

uint64_t make_button_mask(uint64_t binding, size_t count) {
    return count == 0 ? 0 : binding;
}
bool all_buttons_held(uint64_t buttons, uint64_t mask) {
    return mask != 0 && (buttons & mask) == mask;
}

#include "../../../src/core/mode_selection.cpp"

static void require(bool condition, const char *message) {
    if (!condition) throw std::runtime_error(message);
}

static GameModeConfig *make_configs(GameModeConfig *configs, size_t count) {
    for (size_t i = 0; i < count; ++i) {
        configs[i].mode_id = MODE_MELEE;
        configs[i].activation_binding = uint64_t{1} << (i % 30);
        configs[i].activation_binding_count = 1;
    }
    return configs;
}

static void setup_case(size_t count) {
    for (size_t i = 0; i < 30; ++i) mode_activation_masks[i] = 0xccccccccccccccccULL;
    GameModeConfig configs[30]{};
    make_configs(configs, count > 30 ? 30 : count);
    setup_mode_activation_bindings(configs, count);
    if (count <= 30) {
        for (size_t i = 0; i < count; ++i) require(mode_activation_masks[i] == configs[i].activation_binding, "valid binding changed");
    } else {
        for (size_t i = 0; i < 30; ++i) require(mode_activation_masks[i] == 0xccccccccccccccccULL, "oversize setup partially wrote");
    }
}

static void selection_case(size_t count) {
    InputState inputs;
    inputs.buttons = UINT64_MAX;
    CommunicationBackend backend(inputs);
    CommunicationBackend *backends[] = {&backend};
    Config config;
    config.game_mode_configs_count = count;
    make_configs(config.game_mode_configs, count > 30 ? 30 : count);
    current_mode_index = SIZE_MAX;
    select_mode(backends, 1, config);
    require(count > 0 && count <= 30 ? backend.set_calls == 1 : backend.set_calls == 0, "selection refusal mismatch");
}

static void index_cases() {
    for (size_t index = 0; index < 13; ++index) {
        InputState inputs;
        inputs.buttons = uint64_t{1} << index;
        CommunicationBackend backend(inputs);
        CommunicationBackend *backends[] = {&backend};
        Config config;
        config.game_mode_configs_count = 13;
        make_configs(config.game_mode_configs, 13);
        current_mode_index = SIZE_MAX;
        setup_mode_activation_bindings(config.game_mode_configs, 13);
        select_mode(backends, 1, config);
        require(backend.set_calls == 1, "production index did not select");
        require(current_mode_index == index, "production index/order drift");
    }
}

int main(int argc, char **argv) {
    try {
        require(argc == 2, "one case argument is required");
        const std::string name = argv[1];
        if (name == "count_0") setup_case(0), selection_case(0);
        else if (name == "count_10") setup_case(10), selection_case(10);
        else if (name == "count_11") setup_case(11), selection_case(11);
        else if (name == "count_13") setup_case(13), selection_case(13);
        else if (name == "count_30") setup_case(30), selection_case(30);
        else if (name == "count_31") setup_case(31), selection_case(31);
        else if (name == "indices_0_to_12") index_cases();
        else throw std::runtime_error("unknown case");
        std::cout << "case=" << name << " result=PASS\n";
        return 0;
    } catch (const std::exception &error) {
        std::cerr << error.what() << '\n';
        return 1;
    }
}
