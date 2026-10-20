#ifndef _MODES_ULTIMATE_HPP
#define _MODES_ULTIMATE_HPP

#include "core/ControllerMode.hpp"
#include "core/state.hpp"
#include "modes/UltimateNativeProfile.hpp"

class Ultimate : public ControllerMode {
  public:
    Ultimate();
    void SetConfig(GameModeConfig &config, const UltimateProfile *profile, const ultimate_native::PreparedView *native = nullptr);
    enum class Engine : uint8_t { Legacy, NativeAbi1, NativeUnavailable };
    Engine ActiveEngine() const { return _engine; }
    uint32_t NativeGeneration() const { return _native_generation; }
    const ultimate_native::PreparedView *NativeView() const { return _native; }
    const UltimateProfile *SelectedProfile() const { return _profile; }

  private:
    // Config owns both this mode configuration and the selected profile.
    // Config replacement is not a hot-reload operation.
    const UltimateProfile *_profile = nullptr;

    const ultimate_native::PreparedView *_native = nullptr;
    Engine _engine = Engine::Legacy;
    uint32_t _native_generation = 0;
    void UpdatePreprocessedOutputs(const ResolvedInputContext &, OutputState &, CommunicationBackendId) override;
    void UpdateDigitalOutputs(const InputState &inputs, OutputState &outputs) override;
    void UpdateAnalogOutputs(const InputState &inputs, OutputState &outputs, CommunicationBackendId backend_id) override;
};

#endif
