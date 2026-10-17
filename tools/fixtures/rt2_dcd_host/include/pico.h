#pragma once
#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include <assert.h>
typedef unsigned uint;
#define __unused __attribute__((unused))
#define PICO_SDK_VERSION_MAJOR 1
#define PICO_SDK_VERSION_MINOR 5
#define PICO_SHARED_IRQ_HANDLER_HIGHEST_ORDER_PRIORITY 0xff
#define PICO_SHARED_IRQ_HANDLER_LOWEST_ORDER_PRIORITY 0x00
#define PICO_RP2040_USB_FAST_IRQ 0
#define _u(x) x##u
#ifdef __cplusplus
extern "C" {
#endif
void panic(const char*,...);
#ifdef __cplusplus
}
#endif
#define hard_assert assert

#define FORCE_VBUS_DETECT 1
#define remove_volatile_cast(type, value) ((type)(value))
