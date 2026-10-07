#pragma once
#include <cstdint>
struct HostWire {
    unsigned begin_calls = 0;
    void setSDA(int) {}
    void setSCL(int) {}
    void setClock(unsigned long) {}
    void begin() { ++begin_calls; }
};
inline HostWire Wire1;
inline HostWire Wire;
