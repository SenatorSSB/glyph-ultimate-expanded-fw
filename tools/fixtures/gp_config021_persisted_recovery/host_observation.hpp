#pragma once
#include <cstddef>
#include <cstdint>
struct HostObservation {
    unsigned backend_initializations = 0;
    unsigned backend_constructions = 0;
    unsigned mode_binding_setups = 0;
    unsigned menu_constructions = 0;
    unsigned rgb_constructions = 0;
    unsigned configurator_constructions = 0;
    unsigned ordinary_reports = 0;
    unsigned display_begins = 0;
    unsigned display_draws = 0;
    unsigned display_transfers = 0;
    unsigned bootloader_requests = 0;
    unsigned sync_initializations = 0;
    unsigned sync_acquires = 0;
    unsigned sync_releases = 0;
};
inline HostObservation host_observation;

inline bool host_trace_enabled = false;

// Exact compiled template constructor offsets, established by the host runner.
inline uintptr_t host_rgb_ctor_offsets[2]{};
