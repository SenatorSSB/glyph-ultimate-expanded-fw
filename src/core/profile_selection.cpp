#include "core/ProfileSelection.hpp"
#include <atomic>

namespace profile_selection {
namespace {
// Loads/stores only: no ARMv6-M atomic RMW helper or second mailbox owner.
std::atomic<uint32_t> pending_id{0};
}
bool Request(uint32_t id) {
    if (!id || pending_id.load(std::memory_order_acquire)) return false;
    pending_id.store(id, std::memory_order_release);
    return true;
}
uint32_t Pending() { return pending_id.load(std::memory_order_acquire); }
void Complete() { pending_id.store(0, std::memory_order_release); }

bool IsUsb(CommunicationBackendId backend) {
    return backend == COMMS_BACKEND_XINPUT || backend == COMMS_BACKEND_DINPUT ||
        backend == COMMS_BACKEND_NINTENDO_SWITCH;
}
bool Eligible(const GameModeConfig &mode, CommunicationBackendId backend) {
    if ((mode.mode_id == MODE_KEYBOARD || mode.keyboard_mode_config != 0) && !IsUsb(backend)) return false;
    if (mode.applicable_backends_count > sizeof(mode.applicable_backends) / sizeof(mode.applicable_backends[0])) return false;
    if (!mode.applicable_backends_count) return true;
    // Preserve Glyph's USB Keyboard visibility; ordinary selection explicitly
    // forces DInput, the sole backend that can execute Keyboard mode.
    if (mode.keyboard_mode_config != 0 && IsUsb(backend)) return true;
    for (size_t i = 0; i < mode.applicable_backends_count; ++i)
        if (mode.applicable_backends[i] == backend) return true;
    return false;
}
bool NativeTemplate(const GameModeConfig &mode) {
    return mode.mode_id == MODE_ULTIMATE && mode.ultimate_profile_engine == 1;
}
const ProfileStore::Entry *FindEntry(const ProfileStore &store, uint32_t id) {
    for (size_t i = 0; i < store.Count() && i < ProfileStore::kMaxEntries; ++i) {
        const auto *entry = store.EntryAt(i);
        if (entry && entry->id == id) return entry;
    }
    return nullptr;
}
size_t BuildTargets(const Config &config, const ProfileStore &store,
    CommunicationBackendId backend, Target *targets, size_t capacity) {
    if (backend == COMMS_BACKEND_CONFIGURATOR || backend == COMMS_BACKEND_UNSPECIFIED) return 0;
    if (!targets || config.game_mode_configs_count > 30 || store.Count() > ProfileStore::kMaxEntries) return 0;
    size_t count = 0;
    bool native = false;
    for (size_t i = 0; i < config.game_mode_configs_count; ++i) {
        const auto &mode = config.game_mode_configs[i];
        if (!Eligible(mode, backend)) continue;
        if (config.ultimate_profile_store_format == ProfileStore::kCompactConfigFormat && mode.mode_id == MODE_ULTIMATE) {
            // Compact-mode character choices come from native store records.
            // Keep every Config context internally; only an eligible native
            // template can admit those choices to the selector.
            native = native || NativeTemplate(mode);
            continue;
        }
        if (count == capacity) return count;
        targets[count++] = {0, static_cast<uint8_t>(i)};
    }
    if (!native || !store.IsReady()) return count;
    const size_t first_native = count;
    for (size_t i = 0; i < store.Count(); ++i) {
        const auto *entry = store.EntryAt(i);
        if (!entry || !entry->id || entry->payload_version != ultimate_native::kSchema) continue;
        bool duplicate = false;
        for (size_t j = first_native; j < count; ++j) duplicate |= targets[j].profile_id == entry->id;
        if (duplicate) continue;
        if (count == capacity) return count;
        size_t at = count;
        // Stable insertion: display rank first, directory order for equal rank.
        while (at > first_native) {
            const auto *previous = FindEntry(store, targets[at - 1].profile_id);
            if (!previous || previous->rank <= entry->rank) break;
            targets[at] = targets[at - 1];
            --at;
        }
        targets[at] = {entry->id, 0};
        ++count;
    }
    return count;
}
} // namespace profile_selection
