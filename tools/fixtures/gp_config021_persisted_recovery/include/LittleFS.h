#pragma once
#include <Arduino.h>
#include <limits>
#include <cstdlib>
struct LittleFSConfig {
    explicit LittleFSConfig(bool autoformat = true) : auto_format(autoformat) {}
    bool auto_format;
};
struct HostFileFaults {
    bool fail_seek = false;
    unsigned seek_calls = 0, fail_seek_call = 0;
    size_t decoder_read_cutoff = std::numeric_limits<size_t>::max();
    bool decoder_block_read_negative = false;
    unsigned size_calls = 0, size_override_call = 0;
    size_t size_override_value = 0;
    unsigned position_calls = 0, position_override_call = 0;
    size_t position_override_value = 0;
    void (*seek_observer)(unsigned) = nullptr;
    void (*write_observer)() = nullptr;
    bool fail_write = false;
    size_t read_cutoff = std::numeric_limits<size_t>::max();
    size_t reported_size = std::numeric_limits<size_t>::max();
};
class File : public Stream {
public:
    std::shared_ptr<std::vector<uint8_t>> bytes;
    HostFileFaults *faults = nullptr;
    size_t pos = 0;
    File() = default;
    File(std::shared_ptr<std::vector<uint8_t>> data, HostFileFaults *f) : bytes(data), faults(f) {}
    explicit operator bool() const { return static_cast<bool>(bytes); }
    size_t size() const {
        if (faults && ++faults->size_calls == faults->size_override_call) return faults->size_override_value;
        if (!bytes) return 0;
        return faults && faults->reported_size != std::numeric_limits<size_t>::max()
            ? faults->reported_size : bytes->size();
    }
    int available() override {
        if (!bytes || pos >= bytes->size()) return 0;
        return static_cast<int>(bytes->size() - pos);
    }
    int read() override {
        if (!bytes || pos >= bytes->size() || (faults && pos >= faults->read_cutoff)) return -1;
        if (faults && faults->seek_calls >= 2 && pos >= faults->decoder_read_cutoff) return -1;
        return (*bytes)[pos++];
    }
    int read(uint8_t *destination, size_t length) {
        if (faults && faults->seek_calls >= 2 && faults->decoder_block_read_negative) return -1;
        return static_cast<int>(readBytes(destination, length));
    }
    int peek() override {
        if (!bytes || pos >= bytes->size() || (faults && pos >= faults->read_cutoff)) return -1;
        return (*bytes)[pos];
    }
    void flush() override {}
    bool seek(size_t next) {
        if (faults && ++faults->seek_calls == faults->fail_seek_call) return false;
        if (!bytes || next > bytes->size() || (faults && faults->fail_seek)) return false;
        pos = next;
        if (faults && faults->seek_observer) faults->seek_observer(faults->seek_calls);
        return true;
    }
    size_t position() const {
        if (faults && ++faults->position_calls == faults->position_override_call) return faults->position_override_value;
        return pos;
    }
    size_t write(uint8_t byte) override { return write(&byte, 1); }
    size_t write(const uint8_t *data, size_t length) override {
        if (faults && faults->write_observer) faults->write_observer();
        if (!bytes || (faults && faults->fail_write)) return 0;
        if (pos + length > bytes->size()) bytes->resize(pos + length);
        std::memcpy(bytes->data() + pos, data, length);
        pos += length;
        return length;
    }
    void close() {}
};
struct LittleFSHost {
    std::shared_ptr<std::vector<uint8_t>> bytes;
    HostFileFaults faults;
    bool set_config_ok = true;
    bool begin_ok = true;
    bool read_open_ok = true;
    bool write_open_ok = true;
    bool mounted = false;
    bool saw_auto_format_true = false;
    unsigned set_config_calls = 0, begin_calls = 0, end_calls = 0;
    unsigned read_opens = 0, write_opens = 0, exists_calls = 0, format_calls = 0;
    LittleFSHost() : bytes(std::make_shared<std::vector<uint8_t>>()) {
        set_config_ok = std::getenv("GLYPH_HOST_CONFIG_FAIL") == nullptr;
        begin_ok = std::getenv("GLYPH_HOST_MOUNT_FAIL") == nullptr;
    }
    bool setConfig(const LittleFSConfig &config) {
        ++set_config_calls;
        saw_auto_format_true |= config.auto_format;
        return set_config_ok;
    }
    bool begin() { ++begin_calls; mounted = begin_ok; return mounted; }
    void end() { ++end_calls; mounted = false; }
    bool exists(const char *) { ++exists_calls; return mounted && bytes && !bytes->empty(); }
    bool format() { ++format_calls; return true; }
    File open(const char *, const char *mode) {
        faults.seek_calls = faults.size_calls = faults.position_calls = 0;
        if (!mounted) return {};
        if (mode[0] == 'w') {
            ++write_opens;
            if (!write_open_ok) return {};
            bytes->clear();
            return File(bytes, &faults);
        }
        ++read_opens;
        if (!read_open_ok || !bytes || bytes->empty()) return {};
        return File(bytes, &faults);
    }
};
inline LittleFSHost &littlefs_host_instance() {
    static LittleFSHost value;
    return value;
}
#define LittleFS (littlefs_host_instance())
