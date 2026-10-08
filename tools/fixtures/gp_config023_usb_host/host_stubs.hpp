#pragma once

#include <config.pb.h>
#include <cstddef>
#include <cstdint>
#include <vector>

struct InputState {};
struct InputSource {};
struct Pinout {};
struct CommunicationBackend {};

using backend_config_selector_t = void (*)(CommunicationBackendConfig &, const InputState &, Config &);
using usb_backend_getter_t = void (*)(CommunicationBackendConfig &, const Config &);
using detect_console_t = CommunicationBackendId (*)(const Pinout &);
using secondary_backend_initializer_t = size_t (*)(CommunicationBackend **&, CommunicationBackend *&, CommunicationBackendId, InputState &, InputSource **, size_t, Config &, const Pinout &);
using primary_backend_initializer_t = void (*)(CommunicationBackend *&, CommunicationBackendId, InputState &, InputSource **, size_t, Config &, const Pinout &);

struct HostWatchdog {
    uint32_t scratch[8]{};
};
inline HostWatchdog host_watchdog{};
inline HostWatchdog *watchdog_hw = &host_watchdog;
inline bool host_watchdog_reboot = false;
inline bool watchdog_caused_reboot() { return host_watchdog_reboot; }

struct HostPersistence {
    unsigned saves = 0;
    void SaveConfig(const Config &) { ++saves; }
};
inline HostPersistence persistence;

CommunicationBackendConfig backend_config_from_id(
    CommunicationBackendId backend_id,
    const CommunicationBackendConfig *configs,
    size_t count);
CommunicationBackendConfig backend_config_from_buttons(
    const InputState &, const CommunicationBackendConfig *configs, size_t count);
void set_mode(CommunicationBackend *, GameModeConfig &, Config &);
extern unsigned set_mode_calls;
