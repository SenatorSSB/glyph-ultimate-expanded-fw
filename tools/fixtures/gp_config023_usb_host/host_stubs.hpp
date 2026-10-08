#pragma once

#include <config.pb.h>
#include <core/config_validation.hpp>
#include <pb_decode.h>
#include <cstddef>
#include <cstdint>
#include <vector>

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
    void close() { closed = true; }
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
inline constexpr size_t config_offset = 0;

class Persistence {
public:
    enum class LoadResult { Loaded, Rejected, StorageFailure };
    unsigned saves = 0;
    bool available = true;
    ConfigSemanticValidator _validator = nullptr;
    bool IsAvailable() const { return available; }
    bool SetValidator(ConfigSemanticValidator callback);
    bool ValidateConfig(const Config &config, ConfigValidationError &error) const;
    bool CheckSavedConfig(File &, LoadResult *failure = nullptr) const {
        if (failure != nullptr) *failure = LoadResult::Rejected;
        return true;
    }
    LoadResult LoadConfigChecked(Config &config);
    bool SaveConfig(Config &) { ++saves; return true; }
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
