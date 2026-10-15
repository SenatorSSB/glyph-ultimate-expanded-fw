// Checked operations on the existing Arduino-Pico LittleFS mount. No mount,
// format, raw flash, timestamps, or controller activation occurs here.
#ifndef GLYPH_CHECKED_STORAGE_HPP
#define GLYPH_CHECKED_STORAGE_HPP
#include <cstddef>
#include <cstdint>

namespace CheckedStorage {
enum class Kind : uint8_t { Record, Root, Config };
enum class Operation : uint8_t { None, OpenRead, OpenWrite, Read, Write, Seek, Sync, Close, Stat, Remove, Rename, Capacity, Enumerate };
enum class Phase : uint8_t { Before, After };
enum class Fault : uint8_t { None, Fail, LostAcknowledgement };
enum class Outcome : uint8_t { Ok, NotFound, Failed, Uncertain };
struct Result {
    Outcome outcome = Outcome::Failed;
    int error = 0;
    size_t bytes = 0;
    Operation operation = Operation::None;
    explicit operator bool() const { return outcome == Outcome::Ok; }
};
// Hooks are synchronous core0 test controls; null in ordinary production.
using FaultHook = Fault (*)(Kind, Operation, Phase, const char *path);
void SetFaultHook(FaultHook hook);
struct File {
    // No heap-owned handle or unsafe cast to a derived framework object.
    alignas(std::max_align_t) unsigned char native[112]{};
    void *mount = nullptr;
    bool opened = false;
    Kind kind = Kind::Record;
    const char *path = nullptr; // caller keeps path alive until Close
    File() = default;
    File(const File &) = delete;
    File &operator=(const File &) = delete;
};
struct Geometry {
    uint64_t total_bytes = 0, used_bytes = 0, free_bytes = 0;
    uint32_t erase_bytes = 0, program_bytes = 0, read_bytes = 0;
    uint32_t block_count = 0, cache_bytes = 0, name_max = 0;
};
struct Entry { char name[33]{}; uint32_t bytes = 0; bool directory = false; };
using Visitor = bool (*)(void *, const Entry &);
Result Open(File &, const char *path, bool write, Kind);
Result Read(File &, void *bytes, size_t length);
Result Write(File &, const void *bytes, size_t length);
Result Seek(File &, size_t offset);
Result Sync(File &);
Result Close(File &);
Result Stat(const char *path, size_t *size = nullptr, Kind kind = Kind::Record);
Result Remove(const char *path, Kind kind = Kind::Record); // absent is Ok
// Raw errors after invoking a mutating metadata operation are Uncertain.
// A definitely failed Before hook has performed no operation.
Result Rename(const char *from, const char *to, Kind kind = Kind::Record);
Result Capacity(Geometry &);
Result Enumerate(const char *directory, Visitor, void *context);
Result WriteFile(const char *path, const uint8_t *, size_t, Kind);
Result ReadFile(const char *path, uint8_t *, size_t, Kind);
}
#endif
