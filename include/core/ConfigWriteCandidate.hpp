#pragma once
#include <config.pb.h>

// One unpublished whole-Config candidate shared by synchronous core0 writers.
// Never use it as a live runtime profile or retain it across a writer call.
inline Config &ConfigWriteCandidate() {
    static Config candidate;
    return candidate;
}
