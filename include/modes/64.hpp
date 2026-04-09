#ifndef _MODES_64_HPP
#define _MODES_64_HPP

#include "core/ControllerMode.hpp"
#include "core/state.hpp"

#include <config.pb.h>

class Smash64 : public ControllerMode {
  public:
    Smash64();
    void SetConfig(GameModeConfig &config);

  protected:
    void UpdateDigitalOutputs(const InputState &inputs, OutputState &outputs);
    void UpdateAnalogOutputs(const InputState &inputs, OutputState &outputs, CommunicationBackendId backend_id);
  private:
    void HandleSocd(InputState &inputs);
};

#endif