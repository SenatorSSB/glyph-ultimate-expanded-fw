#ifndef _CORE_STACK_WATERMARK_HPP
#define _CORE_STACK_WATERMARK_HPP
#include <cstdint>
#include <cstddef>
namespace glyph_resource {
constexpr uint32_t kStackWatermark = 0x9d6a35c7u;
// Call only for a proven unused interval beneath the current stack pointer.
// All operations inline; no allocator, lock, print, callback, or recursive call.
__attribute__((always_inline)) inline void fill_stack_watermark(
    volatile uint32_t *begin, volatile uint32_t *end) {
    while (begin < end) *begin++ = kStackWatermark;
}
__attribute__((always_inline)) inline uint32_t scan_stack_watermark(
    volatile const uint32_t *begin, volatile const uint32_t *end) {
    volatile const uint32_t *cursor = begin;
    while (cursor < end && *cursor == kStackWatermark) ++cursor;
    return static_cast<uint32_t>(cursor - begin) * sizeof(uint32_t);
}
}
#endif
