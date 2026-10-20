#pragma once
#include "core/state.hpp"

// References live for one UpdateOutputs invocation. No mode may retain them.
struct ResolvedInputContext {
    const InputState &original;
    const InputState &remapped;
    const InputState &post;
};
