#pragma once
#include <cstdint>
struct HostTinyUsbDevice {
    unsigned set_id_calls = 0;
    void setManufacturerDescriptor(const char*) {}
    void setProductDescriptor(const char*) {}
    void setSerialDescriptor(const char*) {}
    void setID(uint16_t, uint16_t) { ++set_id_calls; }
};
inline HostTinyUsbDevice TinyUSBDevice;

class Adafruit_USBD_Interface { public: virtual ~Adafruit_USBD_Interface() = default; virtual uint16_t getInterfaceDescriptor(uint8_t,uint8_t*,uint16_t) { return 0; } };

inline HostTinyUsbDevice &USBDevice=TinyUSBDevice;
