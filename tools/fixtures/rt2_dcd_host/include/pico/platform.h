#pragma once
#include "pico.h"
extern unsigned host_exception,host_core;
inline uint __get_current_exception(){return host_exception;}
inline uint get_core_num(){return host_core;}
