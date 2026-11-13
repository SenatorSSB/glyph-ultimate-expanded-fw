#pragma once
#include "core/state.hpp"
#include <config.pb.h>
struct absolute_time_t { long _private_us_since_boot; };
class CommunicationBackend {
public:
 OutputState outputs{};
 CommunicationBackendId id=COMMS_BACKEND_GAMECUBE;
 OutputState &GetOutputs() { return outputs; }
 CommunicationBackendId BackendId() { return id; }
};
