#ifndef _MODES_ULTIMATE_HPP
#define _MODES_ULTIMATE_HPP

#include "core/ControllerMode.hpp"
#include "core/socd.hpp"
#include "core/state.hpp"

class Ultimate : public ControllerMode {
  public:
    Ultimate();

  private:
    void HandleSocd(InputState &inputs);
    void UpdateDigitalOutputs(const InputState &inputs, OutputState &outputs);
    void UpdateAnalogOutputs(const InputState &inputs, OutputState &outputs, CommunicationBackendId backend_id);

    socd::SocdState _friend_ultimate_socd_states[10] = {};
};

#endif
