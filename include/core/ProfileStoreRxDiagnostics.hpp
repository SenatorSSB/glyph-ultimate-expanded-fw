#pragma once
#include <cstdint>
// Core0-owned candidate observation; no payload copies, flash, or allocations.
// Phase: 1 command recognized, 2 receiving, 4 EOP, 5 decode entered,
// 6 decoded, 7 common admission passed/before ticket, 8 ticket accepted,
// 9 mutation operation branch entered (before storage call), 10 receive timeout, 11 oversize, 12 decode rejected.
// Flags: bit0 EOP, bit1 timeout, bit2 oversize, bit3 decode rejected.
// Raw/fetched/task counters cover ReadPacket only, excluding command ingestion.
struct ProfileStoreRxDiagnostics {
    uint32_t phase = 0, raw = 0, decoded = 0, elapsed = 0;
    uint32_t task_passes = 0, last_progress = 0, fetched = 0, flags = 0;
};
