#include <cstdint>
struct NativeCondition { uint16_t tokens[15]; uint8_t all_count, any_count, none_count, flags; };
struct NativeRole { uint8_t id,condition; };
struct NativeRule { uint8_t priority,table,condition,flags; };
struct NativeDigitalBinding { uint16_t output_mask; uint8_t condition,flags; };
struct NativeEffect { uint8_t phase,target,direction_source,coordinate_mode,condition,table,mode_table,fixed_x,fixed_y,value,flags,reserved; uint16_t digital_set,digital_clear; uint8_t coordinates[18]; };
struct NativeProgramExample { uint8_t header[64],coordinates[28][18]; uint16_t direction_refs[8]; NativeCondition conditions[64]; NativeRole roles[22]; NativeRule rules[19]; NativeDigitalBinding bindings[32]; NativeEffect effects[12]; };
#define P(T) extern "C" char native_##T[sizeof(T)]; char native_##T[sizeof(T)];
P(NativeCondition) P(NativeRole) P(NativeRule) P(NativeDigitalBinding) P(NativeEffect) P(NativeProgramExample)
