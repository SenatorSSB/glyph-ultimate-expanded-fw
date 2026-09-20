#pragma once
#include "config.pb.h"
inline const char *backend_name(CommunicationBackendId) { return "backend"; }
inline const char *gamemode_name(GameModeId) { return "mode"; }
inline const char *socd_name(SocdType) { return "socd"; }
