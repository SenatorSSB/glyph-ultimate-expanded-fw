#pragma once
#include <cstdint>
// Core0-only, opt-in candidate observer. No flash writes or allocations.
namespace ProfileStoreReadTrace {
using Callback = bool (*)(void *, uint32_t, uint32_t);
struct State { Callback callback = nullptr; void *context = nullptr; bool failed = false; };
inline State &Get() { static State state; return state; }
inline bool Failed() { return Get().failed; }
inline bool Mark(uint32_t stage, uint32_t value = 0) {
    auto &s = Get();
    if (s.failed) return false;
    if (s.callback && !s.callback(s.context, stage, value)) s.failed = true;
    return !s.failed;
}
class Scope {
  public:
    Scope(Callback callback, void *context) { Get() = {callback, context, false}; }
    ~Scope() { Get() = {}; }
    Scope(const Scope &) = delete;
    Scope &operator=(const Scope &) = delete;
};
}
