#ifndef _MODES_RIVALS2_HPP
#define _MODES_RIVALS2_HPP

#include "core/ControllerMode.hpp"
#include "core/state.hpp"

#include <config.pb.h>

class Rivals2 : public ControllerMode {
  public:
    Rivals2();

  protected:
    void UpdateDigitalOutputs(const InputState &inputs, OutputState &outputs);
    void UpdateAnalogOutputs(const InputState &inputs, OutputState &outputs, CommunicationBackendId backend_id);};

#endif
