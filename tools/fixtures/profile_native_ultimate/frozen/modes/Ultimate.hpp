#ifndef _MODES_ULTIMATE_HPP
#define _MODES_ULTIMATE_HPP

#include "core/ControllerMode.hpp"
#include "core/state.hpp"

class Ultimate : public ControllerMode {
  public:
    Ultimate();
    void SetConfig(GameModeConfig &config, const UltimateProfile *profile);
    const UltimateProfile *SelectedProfile() const { return _profile; }

  private:
    // Config owns both this mode configuration and the selected profile.
    // Config replacement is not a hot-reload operation.
    const UltimateProfile *_profile = nullptr;

    void UpdateDigitalOutputs(const InputState &inputs, OutputState &outputs);
    void UpdateAnalogOutputs(const InputState &inputs, OutputState &outputs, CommunicationBackendId backend_id);
};

#endif
