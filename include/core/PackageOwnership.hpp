#pragma once
#include "core/ProfileStore.hpp"

// Layout/ownership checks are denials only. Positive persistent-write authority
// still requires the complete same-mount classifier and admitted writer scope.
namespace package_ownership {
inline bool Managed(const GameModeConfig &row) {
#if defined(GLYPH_PACKAGE_V1) && GLYPH_PACKAGE_V1
    return row.managed_format != 0;
#else
    (void)row; return false;
#endif
}
inline bool Managed(const ProfileStore::Entry &entry) {
#if defined(GLYPH_PACKAGE_V1) && GLYPH_PACKAGE_V1
    return entry.managed_format != 0;
#else
    (void)entry; return false;
#endif
}
inline bool ManagedId(const ProfileStore &store, uint32_t id) {
#if defined(GLYPH_PACKAGE_V1) && GLYPH_PACKAGE_V1
    for (size_t i = 0; i < store.Count(); ++i) {
        const auto *entry = store.EntryAt(i);
        if (entry && entry->id == id) return Managed(*entry);
    }
#else
    (void)store; (void)id;
#endif
    return false;
}
inline bool SupportedLayout(const Config &config) {
    return config.ultimate_profile_root_format == 2
#if defined(GLYPH_PACKAGE_V1) && GLYPH_PACKAGE_V1
        || (config.ultimate_profile_root_format == 3 && config.managed_format == 1)
#endif
        ;
}
}
