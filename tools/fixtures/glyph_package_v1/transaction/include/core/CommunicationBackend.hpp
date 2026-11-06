#pragma once
#include "core/InputSource.hpp"
#include <cstddef>
class CommunicationBackend { public: CommunicationBackend(InputState&,InputSource**,size_t){} virtual ~CommunicationBackend()=default; virtual void SendReport()=0; };
