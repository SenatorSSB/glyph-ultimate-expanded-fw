#pragma once
#include <stdbool.h>
#include <stdint.h>
struct semaphore { unsigned count; };
static inline void sem_init(struct semaphore *s,unsigned initial,unsigned maximum) { (void)maximum; s->count=initial; }
static inline void sem_release(struct semaphore *s) { ++s->count; }
static inline bool sem_acquire_timeout_ms(struct semaphore *s,uint32_t ms) { (void)ms; if(!s->count)return false; --s->count;return true; }
static inline void sem_reset(struct semaphore *s,unsigned n) { s->count=n; }
