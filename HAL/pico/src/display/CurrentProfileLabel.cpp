#include "display/CurrentProfileLabel.hpp"

#include "core/ProfileStore.hpp"
#include "core/config_utils.hpp"
#include "modes/Ultimate.hpp"
#include <cstring>

extern Config config;
extern Ultimate ultimate_mode;

const char *current_profile_label(const InputMode *mode, CommunicationBackendId backend) {
    const GameModeConfig *context = mode ? mode->ConfigPointer() : nullptr;
    if (!context) return "";
    const char *fallback = context->name[0] ? context->name : gamemode_name(context->mode_id);
    // Never inspect mutable store/activation state in the Configurator session.
    // Ordinary selections only persist a destination and reboot. No live store
    // writer or activation runs beside the normal dashboard/viewer core.
    if (backend == COMMS_BACKEND_CONFIGURATOR || backend == COMMS_BACKEND_UNSPECIFIED ||
        mode != &ultimate_mode || context->mode_id != MODE_ULTIMATE ||
        config.ultimate_profile_store_format != ProfileStore::kCompactConfigFormat ||
        context->ultimate_profile_engine != 1 || !context->ultimate_profile_id ||
        ultimate_mode.ActiveEngine() != Ultimate::Engine::NativeAbi1 ||
        !profile_store.IsReady() || profile_store.IsReadOnlyRecovery() ||
        context->ultimate_profile_id != profile_store.ActiveId() ||
        ultimate_mode.SelectedProfile() != profile_store.ActiveProfile() ||
        !ultimate_mode.SelectedProfile() ||
        ultimate_mode.SelectedProfile()->schema_version != ultimate_native::kSchema)
        return fallback;

    // At most 64 stable metadata entries; no storage I/O, allocation or cache.
    // A failed activation can retain ActiveId: the execution checks above are
    // essential. Never turn that stale ID into a successfully resolved name.
    if (profile_store.Count() > ProfileStore::kMaxEntries) return fallback;
    for (size_t i = 0; i < profile_store.Count(); ++i) {
        const auto *entry = profile_store.EntryAt(i);
        if (!entry || entry->id != context->ultimate_profile_id) continue;
        const size_t length = strnlen(entry->name, sizeof(entry->name));
        if (entry->payload_version == ultimate_native::kSchema &&
            length > 0 && length < sizeof(entry->name)) return entry->name;
        return fallback;
    }
    return fallback;
}
