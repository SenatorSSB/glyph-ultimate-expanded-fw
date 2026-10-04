#ifndef _MODES_CUSTOMCONTROLLERMODE_HPP
#define _MODES_CUSTOMCONTROLLERMODE_HPP

#include "core/ControllerMode.hpp"
#include "core/state.hpp"

#include <config.pb.h>
#include <type_traits>

class CustomControllerMode : public ControllerMode {
  private:
    static constexpr size_t kMaxCustomModeModifiers = 20;
    static_assert(
        std::extent<decltype(((CustomModeConfig *)nullptr)->modifiers)>::value ==
            kMaxCustomModeModifiers,
        "custom modifier cache capacity must match generated schema"
    );

  public:
    CustomControllerMode();
    void SetConfig(GameModeConfig &config, const CustomModeConfig &custom_mode_config);

  protected:
    void UpdateDigitalOutputs(const InputState &inputs, OutputState &outputs);
    void UpdateAnalogOutputs(const InputState &inputs, OutputState &outputs, CommunicationBackendId backend_id);
  private:
    const CustomModeConfig *_custom_mode_config = nullptr;
    uint64_t _modifier_button_masks[kMaxCustomModeModifiers]{};
    uint64_t _button_combo_mappings_masks[5];
    uint64_t _buttons_to_ignore = 0;
    uint64_t _filtered_buttons = 0;

    Button GetDirectionButton(const Button *direction_buttons, StickDirectionButton direction);
};

#endif
