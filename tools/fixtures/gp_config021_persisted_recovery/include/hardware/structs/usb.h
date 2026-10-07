#pragma once
#include <cstdint>
struct HostUsbHw { uint32_t sie_status=1; };
inline HostUsbHw host_usb_hw;
inline HostUsbHw *usb_hw=&host_usb_hw;
inline constexpr uint32_t USB_SIE_STATUS_CONNECTED_BITS=1;
