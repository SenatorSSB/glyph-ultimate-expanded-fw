#pragma once
#include <stdbool.h>
#include <stdint.h>
#ifdef __cplusplus
extern "C" {
#endif
typedef struct mutex { bool held; } mutex_t;
void mutex_init(mutex_t *);
bool mutex_try_enter(mutex_t *, uint32_t *);
bool mutex_enter_timeout_ms(mutex_t *, uint32_t);
void mutex_exit(mutex_t *);
#ifdef __cplusplus
}
#endif
