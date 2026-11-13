#ifndef _COMMS_CONSOLE_DETECTION_HPP
#define _COMMS_CONSOLE_DETECTION_HPP

#include "core/pinout.hpp"

#include <config.pb.h>

CommunicationBackendId detect_console(const Pinout &pinout);

CommunicationBackendId detect_console_at_boot(const Pinout &pinout);

#endif