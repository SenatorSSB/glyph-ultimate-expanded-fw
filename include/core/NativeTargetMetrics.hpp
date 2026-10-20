#pragma once
#include <cstddef>
#include <cstdint>

#ifndef GLYPH_NATIVE_TARGET_METRICS
#define GLYPH_NATIVE_TARGET_METRICS 0
#endif

namespace native_metrics {
constexpr size_t kRequestBytes = 16, kResponseBytes = 160;
constexpr uint8_t kMagic[4] = {0xd7, 'G', 'N', 'M'};
struct Statistic { uint32_t count, minimum, maximum, sum_low, sum_high; };
#if GLYPH_NATIVE_TARGET_METRICS
uint32_t Now();
void Calibrate();
void RecordFrame(uint32_t begin, uint32_t end, uint32_t before, uint32_t after);
void RecordActivation(uint32_t begin, uint32_t end, uint32_t generation, bool accepted, bool recovered);
void RecordObserver(uint32_t begin);
void ServiceCore(unsigned core);
// One parser, one fixed frame; prefix bytes do not own the identity stream.
void ExpireRequest(uint32_t now);
bool ConsumeRequest(uint8_t byte, uint32_t now, bool &candidate);
void DiscardRequest();
bool CanRespond(uint32_t now);
const uint8_t *Snapshot(uint32_t now, uint32_t actual_generation);
void ResponseAdmitted(uint32_t now);
#else
inline uint32_t Now() { return 0; }
inline void Calibrate() {}
inline void RecordFrame(uint32_t, uint32_t, uint32_t, uint32_t) {}
inline void RecordActivation(uint32_t, uint32_t, uint32_t, bool, bool) {}
inline void RecordObserver(uint32_t) {}
inline void ServiceCore(unsigned) {}
#endif
}
