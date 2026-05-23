#ifndef _MODES_SENSCOPEPROTOTYPE_HPP
#define _MODES_SENSCOPEPROTOTYPE_HPP

#include "core/ControllerMode.hpp"

// G11b experimental shell only.
// This mode is intentionally not wired into mode selection and has no runtime effect
// unless a future batch explicitly instantiates and activates it.
// No game semantics are implemented here.
class SenscopePrototype : public ControllerMode {
  public:
    SenscopePrototype();

  private:
    void UpdateDigitalOutputs(const InputState &inputs, OutputState &outputs) override;
    void UpdateAnalogOutputs(
        const InputState &inputs,
        OutputState &outputs,
        CommunicationBackendId backend_id
    ) override;

    static bool RunPrototypeStaticSmokeCheck();
};

#endif
