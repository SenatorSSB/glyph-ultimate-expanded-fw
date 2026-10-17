#pragma once
#include "pico.h"
#define USBCTRL_IRQ 5
#ifdef __cplusplus
extern "C" {
#endif
typedef void(*irq_handler_t)(void);
void irq_set_enabled(uint,bool);
void irq_add_shared_handler(uint,irq_handler_t,uint8_t);
void irq_set_exclusive_handler(uint,irq_handler_t);
void irq_set_pending(uint);
int __real_user_irq_claim_unused(bool);
int __wrap_user_irq_claim_unused(bool);
#define user_irq_claim_unused __wrap_user_irq_claim_unused
#ifdef __cplusplus
}
#endif
