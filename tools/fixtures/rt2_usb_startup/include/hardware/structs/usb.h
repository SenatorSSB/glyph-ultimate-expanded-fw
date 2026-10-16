#pragma once
#include <cstdint>
struct UsbHw { uint32_t sie_ctrl=0; };
extern UsbHw usb_registers;
#define usb_hw (&usb_registers)
#define USB_SIE_CTRL_PULLUP_EN_BITS 1u
