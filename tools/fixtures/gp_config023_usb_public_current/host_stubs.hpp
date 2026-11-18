#pragma once

#include <config.pb.h>
#include <core/config_validation.hpp>
#include <pb_decode.h>
#include <cstddef>
#include <cstdint>
#include <vector>
#include <cstring>
#include <new>
#include "core/ModeSelectionTransaction.hpp"
#include "core/BootDiagnostics.hpp"
#include "modes/UltimateNativeProfile.hpp"

struct InputState {};
struct InputSource {};
struct Pinout {};
struct CommunicationBackend {};

using backend_config_selector_t = void (*)(CommunicationBackendConfig &, const InputState &, Config &);
using usb_backend_getter_t = void (*)(CommunicationBackendConfig &, const Config &);
using detect_console_t = CommunicationBackendId (*)(const Pinout &);
using secondary_backend_initializer_t = size_t (*)(CommunicationBackend **&, CommunicationBackend *&, CommunicationBackendId, InputState &, InputSource **, size_t, Config &, const Pinout &);
using primary_backend_initializer_t = void (*)(CommunicationBackend *&, CommunicationBackendId, InputState &, InputSource **, size_t, Config &, const Pinout &);

struct HostWatchdog {
    uint32_t scratch[8]{};
};
inline HostWatchdog host_watchdog{};
inline HostWatchdog *watchdog_hw = &host_watchdog;
inline bool host_watchdog_reboot = false;
inline bool watchdog_caused_reboot() { return host_watchdog_reboot; }

struct File {
    std::vector<uint8_t> bytes;
    size_t offset = 0;
    bool closed = false;
    size_t size() const { return bytes.size(); }
    size_t position() const { return offset; }
    bool seek(size_t value) { if (value > bytes.size()) return false; offset = value; return true; }
    size_t read(uint8_t *out, size_t count) {
        const size_t remaining = bytes.size() - offset;
        const size_t amount = count < remaining ? count : remaining;
        for (size_t i = 0; i < amount; ++i) out[i] = bytes[offset + i];
        offset += amount;
        return amount;
    }
    bool close() { closed = true; return true; }
    explicit operator bool() const { return true; }
};

struct HostLittleFs {
    std::vector<uint8_t> saved_bytes;
    File open(const char *, const char *) { return File{saved_bytes}; }
};
inline HostLittleFs LittleFS;

struct ConfigFileReader {
    File *file = nullptr;
    bool io_failed = false;
};
inline bool read_config_file(pb_istream_t *stream, uint8_t *destination, size_t count) {
    auto *reader = static_cast<ConfigFileReader *>(stream->state);
    const size_t read = reader->file->read(destination, count);
    if (read != count) reader->io_failed = true;
    return read == count;
}
inline constexpr const char *config_filename = "config.bin";
inline constexpr size_t config_offset = 8;

using CheckedStorageFile = File;
namespace CompactConfigRecovery { enum class Source { Current, PriorCompact, Legacy }; }
class Persistence {
public:
    enum class LoadResult { Loaded, Rejected, StorageFailure };
    enum class ConfigSelection { None, Current, Prior, Legacy };
    struct ConfigHeader { uint32_t config_size=0, config_crc=0; };
    unsigned saves=0;
    bool available=true;
    ConfigSemanticValidator _validator=nullptr;
    ConfigSelection _config_selection=ConfigSelection::None;
    uint32_t _config_generation=0;
    bool IsAvailable() const { return available; }
    bool SetValidator(ConfigSemanticValidator);
    bool ValidateConfig(const Config &, ConfigValidationError &) const;
    bool CheckSavedConfig(CheckedStorageFile &, LoadResult *failure=nullptr) const {
        if(failure)*failure=LoadResult::Rejected;
        return true;
    }
    LoadResult LoadConfigChecked(Config &);
    LoadResult CompleteReadConfigCandidate(CheckedStorageFile &);
    const char *SelectReadConfigCandidate();
    LoadResult InitializeReadConfigCandidate(CheckedStorageFile &);
    LoadResult FinishConfigDecode(CheckedStorageFile &,bool);
    LoadResult ReadConfigCandidate();
    LoadResult FinishLoadedConfig(Config &);
    LoadResult LoadConfigDriver(Config &);
    bool SaveConfig(Config &) { ++saves; return true; }
};
inline constexpr const char *prior_compact_filename="prior.bin",*legacy_config_filename="legacy.bin";
inline bool select_config_filename(const char *current,const char *,const char *,const char *&selected,CompactConfigRecovery::Source &source){selected=current;source=CompactConfigRecovery::Source::Current;return true;}
inline Config loaded_candidate;
struct LoadPhaseState { CompactConfigRecovery::Source source; uint32_t crc; };
union SourcePhaseContext { LoadPhaseState load{}; };
inline SourcePhaseContext source_phase;
#define load_phase source_phase.load
struct LoadPhaseReset { ~LoadPhaseReset(){std::memset(&source_phase,0,sizeof(source_phase));} };
struct ReadWorkspace { ConfigFileReader reader;pb_istream_t stream;size_t file_size; };
inline ReadWorkspace read_workspace;
inline void ResetReadWorkspace(){read_workspace={};}
struct ReadWorkspaceReset { ~ReadWorkspaceReset(){ResetReadWorkspace();} };
template<bool Write>struct SynchronousFileScope {
    CheckedStorageFile file;
    explicit SynchronousFileScope(const char *) : file{LittleFS.saved_bytes} {}
    CheckedStorageFile &File(){return file;}
};
inline Persistence persistence;

CommunicationBackendConfig backend_config_from_id(
    CommunicationBackendId backend_id,
    const CommunicationBackendConfig *configs,
    size_t count);
CommunicationBackendConfig backend_config_from_buttons(
    const InputState &, const CommunicationBackendConfig *configs, size_t count);
void set_mode(CommunicationBackend *, GameModeConfig &, Config &);
extern unsigned set_mode_calls;
