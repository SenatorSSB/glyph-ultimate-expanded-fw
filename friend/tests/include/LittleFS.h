#pragma once
#include <Arduino.h>
#include <map>
#include <string>

struct LittleFSConfig { explicit LittleFSConfig(bool value = true) : auto_format(value) {} bool auto_format; };
struct HostFault { bool fail_write = false; size_t read_limit = SIZE_MAX, write_limit = SIZE_MAX; };
class File : public Stream {
public:
    std::shared_ptr<std::vector<uint8_t>> bytes;
    HostFault *fault = nullptr;
    size_t pos = 0;
    File() = default;
    File(std::shared_ptr<std::vector<uint8_t>> data, HostFault *f) : bytes(data), fault(f) {}
    explicit operator bool() const { return bool(bytes); }
    size_t size() const { return bytes ? bytes->size() : 0; }
    size_t position() const { return pos; }
    int available() override { return size() > pos ? int(size() - pos) : 0; }
    int read() override { return bytes && pos < size() && pos < fault->read_limit ? (*bytes)[pos++] : -1; }
    int read(uint8_t *out, size_t count) { return int(readBytes(out, count)); }
    int peek() override { return bytes && pos < size() ? (*bytes)[pos] : -1; }
    void flush() override {}
    bool seek(size_t next) { if (!bytes || next > size()) return false; pos = next; return true; }
    size_t write(uint8_t byte) override { return write(&byte, 1); }
    size_t write(const uint8_t *data, size_t count) override {
        if (!bytes || fault->fail_write) return 0;
        count = std::min(count, fault->write_limit);
        if (pos + count > size()) bytes->resize(pos + count);
        std::memcpy(bytes->data() + pos, data, count); pos += count; return count;
    }
    void close() {}
};
struct LittleFSHost {
    std::map<std::string, std::shared_ptr<std::vector<uint8_t>>> files;
    HostFault config_fault, marker_fault;
    bool mounted = false, fail_config_write_open = false, fail_config_read_open = false;
    bool fail_marker_write_open = false, fail_marker_read_after_write = false;
    unsigned config_writes = 0, marker_writes = 0;
    void (*before_config_read)() = nullptr;
    bool setConfig(const LittleFSConfig &c) { return !c.auto_format; }
    bool begin() { mounted = true; return true; }
    void end() { mounted = false; }
    void reset() {
        files.clear(); config_fault = {}; marker_fault = {};
        fail_config_write_open = fail_config_read_open = fail_marker_write_open = fail_marker_read_after_write = false;
        config_writes = marker_writes = 0; before_config_read = nullptr;
    }
    bool remove(const char *path) { return files.erase(path) != 0; }
    bool exists(const char *path) { return files.count(path) != 0; }
    File open(const char *path, const char *mode) {
        bool config = std::string(path) == "config.bin";
        if (!mounted) return {};
        if (mode[0] == 'w') {
            if (config ? fail_config_write_open : fail_marker_write_open) return {};
            if (config) ++config_writes; else ++marker_writes;
            files[path] = std::make_shared<std::vector<uint8_t>>();
        } else {
            if (config && before_config_read) { auto hook = before_config_read; before_config_read = nullptr; hook(); }
            if (config ? fail_config_read_open : (fail_marker_read_after_write && marker_writes)) return {};
            if (!files.count(path)) return {};
        }
        return File(files[path], config ? &config_fault : &marker_fault);
    }
};
inline LittleFSHost &littlefs_host_instance() { static LittleFSHost value; return value; }
#define LittleFS (littlefs_host_instance())
