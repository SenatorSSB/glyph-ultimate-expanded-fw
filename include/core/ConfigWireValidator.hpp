#pragma once
#include <cstddef>
#include <cstdint>

// Exact frozen Config wire inventory/canonicality only. Source ValidateConfig
// remains a separate required predicate. No nanopb/Config object, allocation,
// persistent write, implicit seek or mutable global workspace is introduced.
namespace config_wire {
enum class Result : uint8_t { Valid, Rejected, StorageFailure };
enum class Phase : uint8_t { Key, Scalar, Length, Packed, String, Bytes, Float };
struct Frame {
    uint32_t end, missing;
    uint16_t previous_tag, repetitions;
    uint8_t message;
};
struct Workspace {
    Frame frames[4];
    uint32_t position, length, payload_end;
    uint32_t varint_low, varint_high;
    uint32_t unicode, unicode_minimum, float_nonzero;
    uint16_t field, packed_count;
    uint8_t depth, varint_count, utf8_left;
    Phase phase;
    bool failed, historical_retained;
};
// Begin/Consume/Finish permit arbitrary chunk boundaries and retain all parser
// state in this caller-owned workspace. Alias it to an approved existing owner;
// do not add a new static instance. Source graph depth is exactly four frames.
bool Begin(Workspace &, size_t body_bytes);
// Exact precompact writer 6b73a7c schema only; never current Config authority.
bool BeginHistoricalRetained(Workspace &, size_t body_bytes);
bool Consume(Workspace &, const uint8_t *bytes, size_t count);
bool Finish(Workspace &);
Result ValidateSpan(Workspace &, const uint8_t *bytes, size_t count);
// Reader must copy exactly count bytes at body-relative offset, returning false
// for ANY seek/read/short-read failure. It is never called by parser functions.
// ValidateReader calls it only between Consume calls, so parser stack frames
// cannot overlap storage I/O. Borrowed chunk capacity must be in 1..256.
using Reader = bool (*)(void *context, size_t offset, uint8_t *into, size_t count);
Result ValidateReader(Workspace &, Reader, void *context, size_t body_bytes,
                      uint8_t *borrowed_chunk, size_t chunk_capacity, bool historical_retained = false);
} // namespace config_wire
