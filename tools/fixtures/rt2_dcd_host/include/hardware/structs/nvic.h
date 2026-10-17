#pragma once
#include <stdint.h>
typedef struct {uint32_t iser=0,ispr=0;} NvicHw;
extern NvicHw nvic_registers;
#define nvic_hw (&nvic_registers)
