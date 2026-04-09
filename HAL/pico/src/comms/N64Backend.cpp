#include "comms/N64Backend.hpp"
#include "core/InputSource.hpp"

#include <N64Console.hpp>
#include <hardware/pio.h>

N64Backend::N64Backend(
    InputState &inputs,
    InputSource **input_sources,
    size_t input_source_count,
    uint data_pin,
    PIO pio,
    int sm,
    int offset
)
    : CommunicationBackend(inputs, input_sources, input_source_count),
      _n64(data_pin, pio, sm, offset) {
    _report = default_n64_report;
}

CommunicationBackendId N64Backend::BackendId() {
    return COMMS_BACKEND_N64;
}

void __no_inline_not_in_flash_func(N64Backend::SendReport()) {
    // Update slower inputs before we start waiting for poll.
    ScanInputs(InputScanSpeed::SLOW);
    ScanInputs(InputScanSpeed::MEDIUM);

    // Read inputs
    bool pollTime = true;
    while(pollTime == true) {
        ScanInputs(InputScanSpeed::FAST);
        UpdateOutputs();
        pollTime = _n64.WaitForPoll();
    };

    rp2040.idleOtherCore();

    // Update fast inputs in response to poll.

    // Run gamemode logic.

    // Digital outputs
    _report.a = _outputs.a;
    _report.b = _outputs.b;
    _report.z = _outputs.buttonR;
    _report.l = _outputs.triggerLDigital;
    _report.r = _outputs.triggerRDigital;
    _report.start = _outputs.start;
    _report.dpad_left = _outputs.dpadLeft;
    _report.dpad_right = _outputs.dpadRight;
    _report.dpad_down = _outputs.dpadDown;
    _report.dpad_up = _outputs.dpadUp;

    _report.c_left = _outputs.rightStickLeft;
    _report.c_right = _outputs.rightStickRight;
    _report.c_down = _outputs.rightStickDown;
    _report.c_up = _outputs.rightStickUp;

    // Analog outputs
    _report.stick_x = _outputs.leftStickX - 128;
    _report.stick_y = _outputs.leftStickY - 128;

    // Send outputs to console.
    _n64.SendReport(&_report);
    rp2040.resumeOtherCore();
}

int N64Backend::GetOffset() {
    return _n64.GetOffset();
}
