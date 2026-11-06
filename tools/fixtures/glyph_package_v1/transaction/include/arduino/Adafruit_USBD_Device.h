#pragma once
#include <cstdint>
struct TinyUSBDeviceStub { void setID(uint16_t,uint16_t) {} };
inline TinyUSBDeviceStub TinyUSBDevice;
