#pragma once
#include <cstddef>
#include <cstdint>

namespace TUCompositeHID {
struct Endpoint {
    void begin() {}
    bool ready();
    bool sendReport(uint8_t id, const void *report, size_t size);
};
inline Endpoint _usb_hid;
inline void addDescriptor(uint8_t *, size_t) {}
}
