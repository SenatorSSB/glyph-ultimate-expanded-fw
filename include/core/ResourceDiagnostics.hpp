#ifndef _CORE_RESOURCE_DIAGNOSTICS_HPP
#define _CORE_RESOURCE_DIAGNOSTICS_HPP
#include <cstdint>
#ifndef GLYPH_STRICT_HARDENING_CANDIDATE
#define GLYPH_STRICT_HARDENING_CANDIDATE 0
#endif
#ifndef GLYPH_RESOURCE_DIAGNOSTICS
#define GLYPH_RESOURCE_DIAGNOSTICS 0
#endif

#if GLYPH_RESOURCE_DIAGNOSTICS && !GLYPH_STRICT_HARDENING_CANDIDATE
#error "Resource diagnostics requires the conspicuous strict-hardening candidate marker"
#endif
inline constexpr bool kStrictHardeningCandidate = GLYPH_STRICT_HARDENING_CANDIDATE != 0;

struct ResourceDiagnosticsSnapshot {
    uint32_t core0_stack_min_free_bytes = 0;
    uint32_t core1_stack_min_free_bytes = 0;
    uint32_t heap_arena_peak_bytes = 0;
    uint32_t heap_arena_current_bytes = 0;
    uint32_t heap_arena_capacity_bytes = 0;
    bool resource_diagnostics_enabled = false;
};
#if GLYPH_RESOURCE_DIAGNOSTICS
void InitializeResourceDiagnosticsCore();
void SampleResourceDiagnostics();
ResourceDiagnosticsSnapshot ReadResourceDiagnostics();
#else
inline void InitializeResourceDiagnosticsCore() {}
inline void SampleResourceDiagnostics() {}
inline ResourceDiagnosticsSnapshot ReadResourceDiagnostics() { return {}; }
#endif
#endif
