#pragma once

#include <cstddef>
#include <cstdint>

// ProfileStore's production translation unit defines its default LittleFS
// adapter even when this host test injects its own storage seam.  This narrow
// declaration only supplies that otherwise-unreached construction path.
class File {
  public:
    explicit operator bool() const { return false; }
    size_t write(const uint8_t *, size_t) { return 0; }
    int read(uint8_t *, size_t) { return -1; }
    int available() const { return 0; }
    size_t size() const { return 0; }
    void close() {}
};

class HostLittleFS {
  public:
    File open(const char *, const char *) { return {}; }
    bool exists(const char *) { return false; }
    bool remove(const char *) { return false; }
    bool rename(const char *, const char *) { return false; }
};

inline HostLittleFS LittleFS;
