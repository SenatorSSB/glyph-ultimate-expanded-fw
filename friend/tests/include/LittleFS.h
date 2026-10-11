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
    unsigned begin_calls = 0, format_calls = 0, end_calls = 0;
    bool configuration_ok = true, initial_mount_ok = true, format_ok = true, remount_ok = true;
    bool auto_format_seen = false;
    void (*before_config_read)() = nullptr;
    bool setConfig(const LittleFSConfig &c) { auto_format_seen |= c.auto_format; return configuration_ok && !c.auto_format; }
    bool begin() { ++begin_calls; mounted = format_calls ? remount_ok : initial_mount_ok; return mounted; }
    void end() { ++end_calls; mounted = false; }
    bool format() { ++format_calls; if (!format_ok) return false; files.clear(); return true; }
    void reset() {
        files.clear(); config_fault = {}; marker_fault = {};
        fail_config_write_open = fail_config_read_open = fail_marker_write_open = fail_marker_read_after_write = false;
        config_writes = marker_writes = 0; before_config_read = nullptr;
        begin_calls = format_calls = end_calls = 0;
        configuration_ok = initial_mount_ok = format_ok = remount_ok = true; auto_format_seen = false;
    }
    bool remove(const char *path) { return files.erase(path) != 0; }
    bool exists(const char *path) { return files.count(path) != 0; }
    File open(const char *path, const char *mode) {
        // Enforce the exact target's path-component limit, missed by v1 tests.
        std::string name(path); size_t start = 0;
        for (size_t i=0;i<=name.size();++i) if(i==name.size() || name[i]=='/') {
            if(i-start>=32) return {}; start=i+1;
        }
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
