#pragma once
#include "pico.h"
extern unsigned host_exception,host_core;
inline uint __get_current_exception(){return host_exception;}
inline uint get_core_num(){return host_core;}

extern unsigned host_chip_version;
inline uint8_t rp2040_chip_version(){return host_chip_version;}
inline uint8_t rp2040_rom_version(){return host_chip_version==1?2:3;}
