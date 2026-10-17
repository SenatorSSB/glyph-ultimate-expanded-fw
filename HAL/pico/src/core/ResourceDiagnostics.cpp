#include "core/ResourceDiagnostics.hpp"
#if GLYPH_RESOURCE_DIAGNOSTICS
#include "core/StackWatermark.hpp"
#include <Arduino.h>
#include "pico/multicore.h"
#include "hardware/sync.h"

// This diagnostic image must retain the pinned default two-scratch-bank stack
// model. It does not claim the SDK 0x800 reservation is a whole-runtime bound.
extern "C" bool core1_separate_stack;
extern "C" char __StackLimit;
extern "C" char end;
namespace {
constexpr uintptr_t kStackBottom[2] = {0x20041000u, 0x20040000u};
constexpr uintptr_t kStackTop[2] = {0x20042000u, 0x20041000u};
// Preserve the current initialization frames and its caller. The ARM frame
// checker independently gates this function below this guarded interval.
constexpr uintptr_t kInitializationGuard = 64;
volatile uint32_t stack_end[2] = {};
volatile uint32_t stack_minimum[2] = {};
volatile uint32_t heap_current = 0;
volatile uint32_t heap_peak = 0;
}

void InitializeResourceDiagnosticsCore() {
    const unsigned core = get_core_num();
    if (core1_separate_stack || core > 1) return;
    uintptr_t sp;
    asm volatile("mov %0, sp" : "=r"(sp));
    if (sp < kStackBottom[core] + kInitializationGuard || sp > kStackTop[core]) return;
    const uintptr_t untouched_end = (sp - kInitializationGuard) & ~uintptr_t{3};
    const uint32_t irq_state = save_and_disable_interrupts();
    glyph_resource::fill_stack_watermark(reinterpret_cast<volatile uint32_t *>(kStackBottom[core]),
        reinterpret_cast<volatile uint32_t *>(untouched_end));
    __atomic_store_n(&stack_minimum[core], untouched_end - kStackBottom[core], __ATOMIC_RELAXED);
    stack_end[core] = untouched_end;
    restore_interrupts(irq_state);
}

void SampleResourceDiagnostics() {
    const unsigned core = get_core_num();
    if (core > 1 || stack_end[core] == 0) return;
    const uint32_t remaining = glyph_resource::scan_stack_watermark(
        reinterpret_cast<volatile const uint32_t *>(kStackBottom[core]),
        reinterpret_cast<volatile const uint32_t *>(stack_end[core]));
    if (remaining < __atomic_load_n(&stack_minimum[core], __ATOMIC_RELAXED))
        __atomic_store_n(&stack_minimum[core], remaining, __ATOMIC_RELAXED);
}

ResourceDiagnosticsSnapshot ReadResourceDiagnostics() {
    SampleResourceDiagnostics();
    ResourceDiagnosticsSnapshot snapshot;
    snapshot.core0_stack_min_free_bytes = __atomic_load_n(&stack_minimum[0], __ATOMIC_RELAXED);
    snapshot.core1_stack_min_free_bytes = __atomic_load_n(&stack_minimum[1], __ATOMIC_RELAXED);
    snapshot.heap_arena_current_bytes = __atomic_load_n(&heap_current, __ATOMIC_ACQUIRE);
    snapshot.heap_arena_peak_bytes = __atomic_load_n(&heap_peak, __ATOMIC_ACQUIRE);
    snapshot.heap_arena_capacity_bytes = reinterpret_cast<uintptr_t>(&__StackLimit) - reinterpret_cast<uintptr_t>(&end);
    snapshot.resource_diagnostics_enabled = true;
    return snapshot;
}

extern "C" void *__real__sbrk(int increment);
extern "C" void *__wrap__sbrk(int increment) {
    void *result = __real__sbrk(increment);
    if (result != reinterpret_cast<void *>(-1)) {
        // Called inside the existing allocator lock and Arduino interrupt
        // wrappers. Query the exact resulting break, including optimistic
        // SDK clamping, without allocation, recursion, or a second mount.
        const uintptr_t current = reinterpret_cast<uintptr_t>(__real__sbrk(0));
        const uintptr_t base = reinterpret_cast<uintptr_t>(&end);
        if (current >= base) {
            const uint32_t bytes = current - base;
            // Publish peak before current: an acquired current can never
            // exceed the subsequently acquired monotonic peak snapshot.
            if (bytes > __atomic_load_n(&heap_peak, __ATOMIC_RELAXED))
                __atomic_store_n(&heap_peak, bytes, __ATOMIC_RELEASE);
            __atomic_store_n(&heap_current, bytes, __ATOMIC_RELEASE);
        }
    }
    return result;
}
#endif
