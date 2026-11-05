#include "core/ConfigWireValidator.hpp"
#include <climits>

namespace config_wire {
namespace {
constexpr uint8_t kRepeated = 1, kCallback = 2, kFixed = 4;
struct Field {
    uint16_t tag, bound;
    uint8_t kind, flags, bits, child, enumeration;
};
struct Message { uint16_t first; uint8_t count; uint32_t required; };
#include "ConfigWireMetadata.inc"
static_assert(sizeof(Workspace::frames) / sizeof(Frame) == 4, "Config depth drift");
inline bool Reject(Workspace &w) { w.failed = true; return false; }
inline void ResetVarint(Workspace &w) { w.varint_low = w.varint_high = 0; w.varint_count = 0; }
inline void ToKey(Workspace &w) { w.phase = Phase::Key; ResetVarint(w); }
bool CloseFrames(Workspace &w) {
    while (w.depth && w.position == w.frames[w.depth - 1].end) {
        if (w.phase != Phase::Key || w.varint_count || w.frames[w.depth - 1].missing) return Reject(w);
        --w.depth;
    }
    return true;
}
bool ScalarValid(const Workspace &w, const Field &f) {
    if (f.bits < 32 && (w.varint_high || w.varint_low >= (uint32_t(1) << f.bits))) return false;
    if (f.bits == 32 && w.varint_high) return false;
    if (f.kind == 8 && (w.varint_high || w.varint_low > 1)) return false;
    if (f.kind == 14) {
        if (w.varint_high || w.varint_low >= 64 || f.enumeration >= sizeof enum_sets / sizeof *enum_sets) return false;
        if (!(enum_sets[f.enumeration] & (UINT64_C(1) << w.varint_low))) return false;
    }
    return true;
}
bool Key(Workspace &w) {
    if (w.varint_high || !w.depth) return Reject(w);
    const uint32_t key = w.varint_low;
    const uint32_t tag = key >> 3, type = key & 7;
    auto &frame = w.frames[w.depth - 1];
    const auto &message = messages[frame.message];
    uint8_t local = 0;
    while (local < message.count && fields[message.first + local].tag < tag) ++local;
    if (!tag || local == message.count || fields[message.first + local].tag != tag) return Reject(w);
    w.field = message.first + local;
    const auto &field = fields[w.field];
    if ((field.flags & kCallback) || tag < frame.previous_tag) return Reject(w);
    if (tag == frame.previous_tag) {
        if (!(field.flags & kRepeated) || field.kind != 11 || ++frame.repetitions > field.bound) return Reject(w);
    } else {
        frame.previous_tag = uint16_t(tag); frame.repetitions = 1;
        if ((field.flags & kRepeated) && field.kind == 11 && !field.bound) return Reject(w);
    }
    frame.missing &= ~(uint32_t(1) << local);
    ResetVarint(w);
    if ((field.flags & kRepeated) && field.kind != 11) {
        if (type != 2) return Reject(w);
        w.phase = Phase::Length;
    } else if (field.kind == 4 || field.kind == 8 || field.kind == 13 || field.kind == 14) {
        if (type != 0) return Reject(w);
        w.phase = Phase::Scalar;
    } else if (field.kind == 2) {
        if (type != 5 || frame.end - w.position < 4) return Reject(w);
        w.phase = Phase::Float; w.payload_end = w.position + 4; w.float_nonzero = 0;
    } else {
        if (type != 2) return Reject(w);
        w.phase = Phase::Length;
    }
    return true;
}
bool Length(Workspace &w) {
    if (w.varint_high || !w.depth) return Reject(w);
    const uint32_t count = w.varint_low;
    const auto &field = fields[w.field];
    const uint32_t parent_end = w.frames[w.depth - 1].end;
    if (count > parent_end - w.position) return Reject(w);
    const uint32_t end = w.position + count;
    ResetVarint(w);
    if (field.kind == 11) {
        if (w.depth == 4) return Reject(w);
        const auto &child = messages[field.child];
        w.frames[w.depth++] = {end, child.required, 0, 0, field.child};
        ToKey(w);
    } else if (field.flags & kRepeated) {
        if (!count) return Reject(w);
        w.payload_end = end; w.packed_count = 0; w.phase = Phase::Packed;
    } else if (field.kind == 9 || field.kind == 12) {
        if (count > field.bound || ((field.flags & kFixed) ? count != field.bound : !count)) return Reject(w);
        w.payload_end = end; w.utf8_left = 0;
        w.phase = field.kind == 9 ? Phase::String : Phase::Bytes;
        if (!count) ToKey(w);
    } else return Reject(w);
    return true;
}
bool VarintByte(Workspace &w, uint8_t byte) {
    if (w.varint_count == 10 || (w.varint_count == 9 && byte > 1)) return Reject(w);
    uint64_t value = uint64_t(w.varint_low) | (uint64_t(w.varint_high) << 32);
    value |= uint64_t(byte & 127) << (7 * w.varint_count++);
    w.varint_low = uint32_t(value); w.varint_high = uint32_t(value >> 32);
    if (byte & 128) {
        if (w.varint_count == 10 || (w.phase == Phase::Packed && w.position == w.payload_end)) return Reject(w);
        return true;
    }
    if (w.varint_count > 1 && byte == 0) return Reject(w);
    if (w.phase == Phase::Key) return Key(w);
    if (w.phase == Phase::Length) return Length(w);
    const auto &field = fields[w.field];
    if (!ScalarValid(w, field)) return Reject(w);
    if (w.phase == Phase::Scalar) {
        if (!w.varint_low && !w.varint_high) return Reject(w); // default omission
        ToKey(w);
    } else {
        if (++w.packed_count > field.bound) return Reject(w);
        ResetVarint(w);
        if (w.position == w.payload_end) ToKey(w);
    }
    return true;
}
bool StringByte(Workspace &w, uint8_t byte) {
    if (!byte) return Reject(w);
    if (!w.utf8_left) {
        if (byte < 0x80) return true;
        if (byte >= 0xc2 && byte <= 0xdf) { w.utf8_left = 1; w.unicode = byte & 31; w.unicode_minimum = 0x80; }
        else if (byte >= 0xe0 && byte <= 0xef) { w.utf8_left = 2; w.unicode = byte & 15; w.unicode_minimum = 0x800; }
        else if (byte >= 0xf0 && byte <= 0xf4) { w.utf8_left = 3; w.unicode = byte & 7; w.unicode_minimum = 0x10000; }
        else return Reject(w);
    } else {
        if ((byte & 0xc0) != 0x80) return Reject(w);
        w.unicode = (w.unicode << 6) | (byte & 63);
        if (!--w.utf8_left && (w.unicode < w.unicode_minimum || w.unicode > 0x10ffff ||
                             (w.unicode >= 0xd800 && w.unicode <= 0xdfff))) return Reject(w);
    }
    return true;
}
} // namespace

bool Begin(Workspace &w, size_t size) {
    w = {};
    if (size > 65536) return Reject(w);
    w.length = uint32_t(size); w.depth = 1; w.phase = Phase::Key;
    w.frames[0] = {uint32_t(size), messages[config_message].required, 0, 0, config_message};
    return true;
}
bool Consume(Workspace &w, const uint8_t *bytes, size_t count) {
    if (w.failed || (!bytes && count) || count > w.length - w.position) return Reject(w);
    while (count--) {
        if (!CloseFrames(w) || !w.depth) return Reject(w);
        if (w.position >= w.frames[w.depth - 1].end) return Reject(w);
        const uint8_t byte = *bytes++; ++w.position;
        if (w.phase == Phase::String) {
            if (!StringByte(w, byte)) return false;
            if (w.position == w.payload_end) { if (w.utf8_left) return Reject(w); ToKey(w); }
        } else if (w.phase == Phase::Bytes) {
            if (w.position == w.payload_end) ToKey(w);
        } else if (w.phase == Phase::Float) {
            w.float_nonzero |= byte;
            if (w.position == w.payload_end) { if (!w.float_nonzero) return Reject(w); ToKey(w); }
        } else if (!VarintByte(w, byte)) return false;
    }
    return !w.failed;
}
bool Finish(Workspace &w) {
    if (w.failed || w.position != w.length || !CloseFrames(w) || w.depth) return Reject(w);
    return true;
}
Result ValidateSpan(Workspace &w, const uint8_t *bytes, size_t size) {
    return Begin(w, size) && Consume(w, bytes, size) && Finish(w) ? Result::Valid : Result::Rejected;
}
__attribute__((noinline)) Result ValidateReader(Workspace &w, Reader read, void *context, size_t size,
                                               uint8_t *chunk, size_t capacity) {
    if (!read || !chunk || !capacity || capacity > 256 || !Begin(w, size)) return Result::Rejected;
    while (w.position < w.length) {
        const size_t count = w.length - w.position < capacity ? w.length - w.position : capacity;
        if (!read(context, w.position, chunk, count)) { w.failed = true; return Result::StorageFailure; }
        if (!Consume(w, chunk, count)) return Result::Rejected;
    }
    return Finish(w) ? Result::Valid : Result::Rejected;
}
} // namespace config_wire
