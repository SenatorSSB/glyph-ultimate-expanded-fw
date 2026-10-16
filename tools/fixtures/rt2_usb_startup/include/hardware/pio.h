#pragma once
#include <cstdint>
#include <cstddef>
struct PioHw {};using PIO=PioHw*;extern PioHw pios[2];
#define pio0 (&pios[0])
#define pio1 (&pios[1])
struct pio_program { const uint16_t *instructions;uint8_t length;int8_t origin; };
struct pio_sm_config {};
enum { pio_x=1,pio_pins=0 };
inline uint16_t pio_encode_out(unsigned d,unsigned n){return 0x6000|(d<<5)|n;}
inline uint16_t pio_encode_set(unsigned d,unsigned n){return 0xe000|(d<<5)|n;}
inline uint16_t pio_encode_mov(unsigned d,unsigned s){return 0xa000|(d<<5)|s;}
inline uint16_t pio_encode_delay(unsigned n){return n<<8;}
bool pio_can_add_program(PIO,const pio_program*);
int pio_claim_unused_sm(PIO,bool);
unsigned pio_add_program(PIO,const pio_program*);
inline pio_sm_config pio_get_default_sm_config(){return {};}
void sm_config_set_wrap(pio_sm_config*,unsigned,unsigned);
void sm_config_set_set_pins(pio_sm_config*,unsigned,unsigned);
void sm_config_set_out_pins(pio_sm_config*,unsigned,unsigned);
void sm_config_set_out_shift(pio_sm_config*,bool,bool,unsigned);
void sm_config_set_clkdiv(pio_sm_config*,float);
void pio_gpio_init(PIO,unsigned);
void pio_sm_set_consecutive_pindirs(PIO,int,unsigned,unsigned,bool);
void pio_sm_init(PIO,int,unsigned,const pio_sm_config*);
void pio_sm_set_pins(PIO,int,unsigned);
void pio_sm_set_enabled(PIO,int,bool);
bool pio_sm_is_tx_fifo_empty(PIO,int);
void pio_sm_put(PIO,int,uint32_t);
