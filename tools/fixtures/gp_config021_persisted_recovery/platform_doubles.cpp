// Physical bus methods only. Every repository backend/app object is linked from
// its literal source. These seams provide no USB descriptor or bus-wire proof.
#include <Adafruit_USBD_XInput.hpp>
#include <GamecubeConsole.hpp>
#include <N64Console.hpp>
#include <NesConsole.hpp>
#include <SnesConsole.hpp>
#include <dlfcn.h>
#include <cstring>
#include "host_observation.hpp"

GamecubeConsole::GamecubeConsole(uint, PIO, int, int) {}
GamecubeConsole::~GamecubeConsole() {}
bool GamecubeConsole::Detect() { return false; }
bool GamecubeConsole::WaitForPoll() { return false; }
bool GamecubeConsole::WaitForPollStart() { return false; }
PollStatus GamecubeConsole::WaitForPollEnd() { return PollStatus::RUMBLE_OFF; }
void GamecubeConsole::SendReport(gc_report_t*) { ++host_observation.ordinary_reports; }
int GamecubeConsole::GetOffset() { return 0; }
N64Console::N64Console(uint, PIO, int, int) {}
N64Console::~N64Console() {}
bool N64Console::Detect() { return false; }
bool N64Console::WaitForPoll() { return false; }
void N64Console::SendReport(n64_report_t*) { ++host_observation.ordinary_reports; }
int N64Console::GetOffset() { return 0; }
NesConsole::NesConsole(uint,uint,uint,PIO,int,int) {}
NesConsole::~NesConsole() {}
bool NesConsole::Detect() { return false; }
void NesConsole::SendReport(nes_report_t&) { ++host_observation.ordinary_reports; }
int NesConsole::GetOffset() { return 0; }
SnesConsole::SnesConsole(uint,uint,uint,PIO,int,int) {}
SnesConsole::~SnesConsole() {}
bool SnesConsole::Detect() { return false; }
void SnesConsole::SendReport(snes_report_t&) { ++host_observation.ordinary_reports; }
int SnesConsole::GetOffset() { return 0; }
Adafruit_USBD_XInput::Adafruit_USBD_XInput(uint8_t interval):_interval_ms(interval) {}
bool Adafruit_USBD_XInput::begin() { return true; }
bool Adafruit_USBD_XInput::ready() { return true; }
bool Adafruit_USBD_XInput::sendReport(xinput_report_t*) {
    ++host_observation.ordinary_reports; return true;
}
uint16_t Adafruit_USBD_XInput::getInterfaceDescriptor(uint8_t,uint8_t*,uint16_t) { return 0; }

// Compiler instrumentation observes actual application function entries. It
// never replaces a constructor/body. Local template constructors use exact
// runner-established image-relative symbol addresses; positive normal controls
// must prove each counter is actually wired.
static __attribute__((no_instrument_function))
bool host_contains(const char *text,const char *part) {
    for (size_t i=0;text[i];++i) {
        size_t j=0;while (part[j] && text[i+j] && part[j]==text[i+j]) ++j;
        if (!part[j]) return true;
    }
    return false;
}
extern "C" __attribute__((no_instrument_function))
void __cyg_profile_func_enter(void *function, void*) {
    if (!host_trace_enabled) return;
    Dl_info info{};
    if (!dladdr(function,&info) || !info.dli_fbase) return;
    uintptr_t offset=reinterpret_cast<uintptr_t>(function)-reinterpret_cast<uintptr_t>(info.dli_fbase);
    if(offset==host_rgb_ctor_offsets[0] || offset==host_rgb_ctor_offsets[1]) ++host_observation.rgb_constructions;
    // dladdr may return the nearest exported symbol for a local function.
    if (!info.dli_sname || info.dli_saddr!=function) return;
    const char *name=info.dli_sname;
    if ((host_contains(name,"CommunicationBackendC1E") || host_contains(name,"CommunicationBackendC2E"))) ++host_observation.backend_constructions;
    if ((host_contains(name,"AboutMenuC1E") || host_contains(name,"AboutMenuC2E") || host_contains(name,"RemapMenuC1E") || host_contains(name,"RemapMenuC2E") || host_contains(name,"RgbBrightnessMenuC1E") || host_contains(name,"RgbBrightnessMenuC2E"))) ++host_observation.menu_constructions;
    if ((host_contains(name,"ConfiguratorBackendC1E") || host_contains(name,"ConfiguratorBackendC2E"))) ++host_observation.configurator_constructions;
    if (host_contains(name,"initialize_backends")) ++host_observation.backend_initializations;
    if (host_contains(name,"setup_mode_activation_bindings")) ++host_observation.mode_binding_setups;
}
extern "C" __attribute__((no_instrument_function))
void __cyg_profile_func_exit(void*,void*) {}

// Selected NES physical transport flags start false in actual NesConsole.cpp.
// These flags are an I/O seam; no NES timing or handshake proof is claimed.
bool LED_OK=false;
bool SCREEN_OK=false;
