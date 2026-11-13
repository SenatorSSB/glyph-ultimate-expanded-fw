#include "core/ProfileSelection.hpp"
#include <atomic>

namespace profile_selection {
namespace {
// Loads/stores only: no ARMv6-M atomic RMW helper or second mailbox owner.
std::atomic<uint32_t> pending_id{0};
CommunicationBackendId requested_backend = COMMS_BACKEND_UNSPECIFIED;
}
bool Request(uint32_t id, CommunicationBackendId route) {
    if (!id || pending_id.load(std::memory_order_acquire)) return false;
    requested_backend = route;
    pending_id.store(id, std::memory_order_release);
    return true;
}
bool Request(uint32_t id) { return Request(id, COMMS_BACKEND_UNSPECIFIED); }
uint32_t Pending() { return pending_id.load(std::memory_order_acquire); }
CommunicationBackendId RequestedBackend() { return requested_backend; }
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
    return !package_ownership::Managed(mode) && mode.mode_id == MODE_ULTIMATE && mode.ultimate_profile_engine == 1;
}
const ProfileStore::Entry *FindEntry(const ProfileStore &store, uint32_t id) {
    for (size_t i = 0; i < store.Count() && i < ProfileStore::kMaxEntries; ++i) {
        const auto *entry = store.EntryAt(i);
        if (entry && entry->id == id) return entry;
    }
    return nullptr;
}
#if defined(GLYPH_PACKAGE_V1) && GLYPH_PACKAGE_V1
bool BoundPair(const Config &config, const ProfileStore::Entry &entry, size_t row, CommunicationBackendId backend) {
    if (config.ultimate_profile_store_format != ProfileStore::kCompactConfigFormat ||
        row >= config.game_mode_configs_count || config.game_mode_configs_count > 30 ||
        !entry.id || entry.payload_version != ultimate_native::kSchema) return false;
    const auto &mode = config.game_mode_configs[row];
    if (mode.mode_id != MODE_ULTIMATE || mode.ultimate_profile_engine != 1 ||
        mode.ultimate_profile_id != entry.id || mode.ultimate_profile_config ||
        mode.keyboard_mode_config || mode.custom_mode_config || !Eligible(mode, backend)) return false;
    if (!entry.managed_format) return !mode.managed_format;
    return entry.managed_format == 1 && mode.managed_format == 1 &&
        entry.owned_row1 == row + 1 && entry.owned_rgb1 == mode.rgb_config;
}
#endif
size_t BuildTargets(const Config &config, const ProfileStore &store,
    CommunicationBackendId backend, Target *targets, size_t capacity) {
    if (backend == COMMS_BACKEND_CONFIGURATOR || backend == COMMS_BACKEND_UNSPECIFIED) return 0;
    if (!targets || config.game_mode_configs_count > 30 || store.Count() > ProfileStore::kMaxEntries) return 0;
    size_t count = 0;
#if defined(GLYPH_PACKAGE_V1) && GLYPH_PACKAGE_V1
    // Ordinary non-Ultimate modes precede the logical native profile list.
    // A raw record without a bound Config row is available to G6 only.
    for (size_t i = 0; i < config.game_mode_configs_count; ++i) {
        const auto &mode = config.game_mode_configs[i];
        if (count == capacity) return count;
        if (package_ownership::Managed(mode) || !Eligible(mode, backend) ||
            (mode.mode_id == MODE_ULTIMATE && config.ultimate_profile_store_format == ProfileStore::kCompactConfigFormat))
            continue;
        targets[count++] = {0, static_cast<uint8_t>(i)};
    }
    if (!store.IsReady()) return count;
    const size_t first_native = count;
    for (size_t i = 0; i < store.Count() && count < capacity; ++i) {
        const auto *entry = store.EntryAt(i);
        if (!entry) continue;
        size_t row = config.game_mode_configs_count;
        bool ambiguous = false;
        for (size_t j = 0; j < config.game_mode_configs_count; ++j) {
            if (!BoundPair(config, *entry, j, backend)) continue;
            if (row != config.game_mode_configs_count) { ambiguous = true; break; }
            row = j;
        }
        if (ambiguous || row == config.game_mode_configs_count) continue;
        size_t at = count;
        while (at > first_native) {
            const auto *previous = FindEntry(store, targets[at - 1].profile_id);
            if (previous->rank <= entry->rank) break;
            targets[at] = targets[at - 1];
            --at;
        }
        targets[at] = {entry->id, static_cast<uint8_t>(row)};
        ++count;
    }
    return count;
#else
    bool native = false;
    for (size_t i = 0; i < config.game_mode_configs_count; ++i) {
        const auto &mode = config.game_mode_configs[i];
        if (package_ownership::Managed(mode) || !Eligible(mode, backend)) continue;
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
        if (!entry || package_ownership::Managed(*entry) || !entry->id || entry->payload_version != ultimate_native::kSchema) continue;
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
#endif
}
} // namespace profile_selection
