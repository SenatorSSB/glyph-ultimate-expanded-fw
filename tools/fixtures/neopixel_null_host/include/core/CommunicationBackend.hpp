#pragma once
#include <cstddef>
class InputMode;
struct InputState {};
class InputSource {};
class CommunicationBackend {
public:
    CommunicationBackend(InputState &, InputSource **, std::size_t) {}
    virtual ~CommunicationBackend() = default;
    virtual void SetGameMode(InputMode *) {}
    virtual void SendReport() = 0;
};
