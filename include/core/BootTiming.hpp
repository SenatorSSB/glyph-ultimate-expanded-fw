#pragma once
#include <cstdint>

namespace boot_timing {
// Milliseconds from entry to Arduino setup. A pending milestone reads UINT32_MAX.
struct Times {
    uint32_t store_ms = UINT32_MAX, backend_ms = UINT32_MAX;
    uint32_t first_mode_ready_ms = UINT32_MAX, first_dashboard_ms = UINT32_MAX;
};
Times Snapshot();
}
