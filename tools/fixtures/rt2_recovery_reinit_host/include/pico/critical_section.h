#pragma once
struct critical_section { void *spin_lock; unsigned held; };
static inline void critical_section_init(struct critical_section *s){s->spin_lock=s;s->held=0;}
static inline void critical_section_enter_blocking(struct critical_section *s){++s->held;}
static inline void critical_section_exit(struct critical_section *s){--s->held;}
