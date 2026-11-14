#include "comms/NintendoSwitchBackend.hpp"
#include "comms/IntegratedDisplay.hpp"
#include "TUCompositeHID.hpp"
#include "hardware/timer.h"
#include <array>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>

static void check(bool condition, const char *message) {
    if (!condition) {
        std::fprintf(stderr, "%s\n", message);
        std::exit(1);
    }
}

static std::string trace;
static uint64_t ready_at;
static bool freeze_control;
static bool withdraw_on_fast;
static bool pressed;
static std::vector<std::array<uint8_t, 8>> reports;

bool TUCompositeHID::Endpoint::ready() {
    // Identify where the unmodified parent is spinning. The driver bounds its lifetime.
    if (freeze_control && clock_us == 2000 && trace == "SM") {
        std::puts("stalled before FAST with 2000 us of simulated waiting");
        std::fflush(stdout);
    }
    return clock_us >= ready_at;
}

bool TUCompositeHID::Endpoint::sendReport(uint8_t id, const void *data, size_t size) {
    check(clock_us >= ready_at && id == 0 && size == 8, "invalid HID submission");
    std::array<uint8_t, 8> bytes;
    std::memcpy(bytes.data(), data, size);
    reports.push_back(bytes);
    trace += 'T';
    return true;
}

struct Source : InputSource {
    InputScanSpeed speed;
    explicit Source(InputScanSpeed value) : speed(value) {}
    InputScanSpeed ScanSpeed() override { return speed; }
    void UpdateInputs(InputState &inputs) override {
        switch (speed) {
            case InputScanSpeed::SLOW: trace += 'S'; break;
            case InputScanSpeed::MEDIUM: trace += 'M'; break;
            case InputScanSpeed::FAST:
                trace += 'F';
                inputs.mb1 = pressed;
                if (withdraw_on_fast) ready_at = UINT64_MAX;
                break;
        }
    }
};

struct Backend : NintendoSwitchBackend {
    using NintendoSwitchBackend::NintendoSwitchBackend;
    void UpdateOutputs() override {
        trace += 'U';
        _outputs = {};
        _outputs.y = _outputs.a = _outputs.buttonL = _outputs.triggerLDigital = pressed;
        _outputs.select = _outputs.leftStickClick = _outputs.home = pressed;
        _outputs.b = _outputs.x = _outputs.buttonR = _outputs.triggerRDigital = !pressed;
        _outputs.start = _outputs.rightStickClick = _outputs.capture = !pressed;
        _outputs.dpadUp = _outputs.dpadRight = pressed;
        _outputs.leftStickX = 144;
        _outputs.leftStickY = 96;
        _outputs.rightStickX = 112;
        _outputs.rightStickY = 160;
    }
};

struct Menu : DisplayMode {
    int frames = 0, presses = 0;
    DisplayModeId GetId() override { return DISPLAY_MODE_VIEWER; }
    void UpdateDisplay(IntegratedDisplay *, Adafruit_GFX &) override { ++frames; }
    void HandleControls(IntegratedDisplay *, const DisplayControls &, Button button) override {
        check(button == BTN_MB1, "unexpected control");
        ++presses;
    }
};

int main(int argc, char **argv) {
    InputState state{};
    Source slow(InputScanSpeed::SLOW), medium(InputScanSpeed::MEDIUM), fast(InputScanSpeed::FAST);
    InputSource *sources[] = {&fast, &medium, &slow};
    Backend backend(state, sources, 3);
    check(backend.BackendId() == COMMS_BACKEND_NINTENDO_SWITCH, "wrong backend ID");
    Adafruit_GFX gfx;
    Menu menu;
    DisplayMode *modes[] = {&menu};
    IntegratedDisplay display(state, gfx, [] {}, [] {},
        {BTN_MB1, BTN_UNSPECIFIED, BTN_UNSPECIFIED, BTN_UNSPECIFIED}, modes, 1);

    freeze_control = argc > 1 && std::string(argv[1]) == "stall";
    if (freeze_control) {
        ready_at = UINT64_MAX;
        backend.SendReport();
        return 1;
    }
    auto turn = [&](bool button, uint64_t delay, bool send, uint64_t elapsed) {
        clock_us += 200000; // Advance past the real display's control cooldown.
        pressed = button;
        ready_at = delay == UINT64_MAX ? UINT64_MAX : clock_us + delay;
        const auto before = clock_us;
        const auto count = reports.size();
        trace.clear();
        backend.SendReport();
        check(trace == (send ? "SMFUT" : "SMFU"), "scan/output/submission sequence");
        check(clock_us - before == elapsed, "unexpected readiness wait");
        check(reports.size() == count + send, "unexpected submission count");
        if (send) {
            const std::array<uint8_t, 8> expected = {
                uint8_t(button ? 0x55 : 0xaa), uint8_t(button ? 0x15 : 0x2a),
                uint8_t(button ? 1 : 8), 148, 167, 108, 87, 0};
            check(reports.back() == expected, "packed report mismatch");
        }
        display.SendReport();
    };
    turn(false, 0, true, 0);
    turn(true, 500, true, 500);
    if (argc > 1 && std::string(argv[1]) == "ready") return 0;
    turn(false, UINT64_MAX, false, 1000);
    turn(true, UINT64_MAX, false, 1000);
    check(menu.presses == 2 && menu.frames == 4, "menu did not receive buttons while unready");
    for (int i = 0; i < 32; ++i) turn(false, UINT64_MAX, false, 1000);
    turn(true, 0, true, 0);
    withdraw_on_fast = true;
    turn(false, 0, false, 0);
    withdraw_on_fast = false;
    turn(false, 0, true, 0);
    std::puts("PASS bounded Switch wait, scan order, shared-menu controls and 8-byte reports");
}
