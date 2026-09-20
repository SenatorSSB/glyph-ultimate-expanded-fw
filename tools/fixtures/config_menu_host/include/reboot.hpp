#pragma once
struct WatchdogStub { unsigned int scratch[2] = {}; };
inline WatchdogStub watchdog_storage;
inline WatchdogStub *watchdog_hw = &watchdog_storage;
inline void reboot_firmware() {}
inline void reboot_bootloader() {}
inline void tud_disconnect() {}
inline void delay(unsigned long) {}
