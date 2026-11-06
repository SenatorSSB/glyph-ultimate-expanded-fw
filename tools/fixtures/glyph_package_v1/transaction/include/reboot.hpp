#pragma once
#include <stdexcept>
inline void reboot_firmware(){throw std::runtime_error("unexpected reboot firmware");}
inline void reboot_bootloader(){throw std::runtime_error("unexpected reboot bootloader");}
