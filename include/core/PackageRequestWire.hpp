#pragma once
#include <cstddef>
#include <cstdint>
#include <cstring>
#include <package.pb.h>
#include <pb_decode.h>
#include <pb_encode.h>
#include "core/Sha256.hpp"

// No storage, transport, global workspace or allocation. These objects must live
// in the B1-R2 request/initialization owner unions, never in new static storage.
// A successful wire decode is not admission: source Config/native/context
// validation and materialization remain mandatory before persistent mutation.
namespace glyph_package {
struct BorrowedSpan {
    const uint8_t *bytes = nullptr;
    size_t size = 0;
    uint32_t maximum = 0;
    bool seen = false;
};
struct EnvelopePhase {
    PackageEnvelope request;
    BorrowedSpan package, native;
    void Release() {
        request.package_body = {};
        package = {}; native = {};
    }
};
static_assert(sizeof(EnvelopePhase) <= sizeof(ProfileStoreRequest), "package request exceeds owner");
static_assert(sizeof(PackageBody) <= 3908, "package body exceeds initialization owner");
static_assert(sizeof(PackageResponse) <= sizeof(ProfileStoreResponse), "package response exceeds owner");
inline bool LifecycleOperation(PackageOperation operation) {
    return operation >= PackageOperation_UPDATE_PACKAGE && operation <= PackageOperation_DELETE_PACKAGE;
}
namespace wire {
enum class Message : uint8_t { Envelope, Body, Mode, Socd, Remap, Rgb, Color };
enum class Kind : uint8_t { Scalar, String, Bytes, Packed, Child };
struct Rule { Kind kind; uint32_t maximum; uint8_t count; Message child; };
inline bool RuleFor(Message message, unsigned tag, Rule &r) {
    r = {Kind::Scalar, UINT32_MAX, 1, Message::Envelope};
    switch (message) {
    case Message::Envelope:
        switch (tag) {
        case 1: case 3: case 4: case 13: case 21: return true;
        case 27: case 28: case 30: return true;
        case 29: r = {Kind::String, 17, 1, {}}; return true;
        case 2: return true; // only full-width uint64 field in requests
        case 24: r = {Kind::Child, 4491, 1, Message::Body}; return true;
        case 25: case 26: r = {Kind::Bytes, 32, 1, {}}; return true;
        default: return false;
        }
    case Message::Body:
        switch (tag) {
        case 1: r.maximum = 1; return true;
        case 2: r = {Kind::String, 32, 1, {}}; return true;
        case 3: return true;
        case 4: r = {Kind::Child, 493, 1, Message::Mode}; return true;
        case 5: r = {Kind::Bytes, 3336, 1, {}}; return true;
        case 6: r = {Kind::Child, 611, 1, Message::Rgb}; return true;
        default: return false;
        }
    case Message::Mode:
        switch (tag) {
        case 1: r = {Kind::String, 17, 1, {}}; return true;
        case 2: r = {Kind::Child, 6, 10, Message::Socd}; return true;
        case 3: r = {Kind::Child, 4, 60, Message::Remap}; return true;
        case 4: r = {Kind::Packed, 60, 4, {}}; return true;
        case 5: r.maximum = 4; return true;
        case 6: r = {Kind::Packed, 10, 15, {}}; return true;
        case 7: r = {Kind::Packed, 45, 7, {}}; return true;
        default: return false;
        }
    case Message::Socd:
        if (tag < 1 || tag > 3) return false;
        r.maximum = tag == 3 ? 5 : 60; return true;
    case Message::Remap:
        if (tag < 1 || tag > 2) return false;
        r.maximum = 60; return true;
    case Message::Rgb:
        switch (tag) {
        case 1: r = {Kind::Child, 8, 60, Message::Color}; return true;
        case 2: return true;
        case 3: r.maximum = 5; return true;
        case 4: r.maximum = 255; return true;
        default: return false;
        }
    case Message::Color:
        if (tag < 1 || tag > 2) return false;
        if (tag == 1) r.maximum = 60;
        return true;
    }
    return false;
}
inline bool Varint(const uint8_t *b, size_t size, size_t &i, uint64_t &v) {
    v = 0;
    for (unsigned shift = 0; shift < 70; shift += 7) {
        if (i == size) return false;
        const uint8_t byte = b[i++];
        if (shift == 63 && byte > 1) return false;
        v |= uint64_t(byte & 127) << shift;
        if (!(byte & 128)) return shift == 0 || byte != 0;
    }
    return false;
}
inline bool Text(const uint8_t *b, size_t size) {
    for (size_t i = 0; i < size;) {
        const uint8_t c = b[i++];
        if (c == 0) return false;
        if (c < 0x80) continue;
        unsigned n; uint32_t v, minimum;
        if (c >= 0xc2 && c <= 0xdf) { n = 1; v = c & 31; minimum = 0x80; }
        else if (c >= 0xe0 && c <= 0xef) { n = 2; v = c & 15; minimum = 0x800; }
        else if (c >= 0xf0 && c <= 0xf4) { n = 3; v = c & 7; minimum = 0x10000; }
        else return false;
        if (n > size - i) return false;
        while (n--) { const uint8_t d = b[i++]; if ((d & 0xc0) != 0x80) return false; v = (v << 6) | (d & 63); }
        if (v < minimum || v > 0x10ffff || (v >= 0xd800 && v <= 0xdfff)) return false;
    }
    return true;
}
inline bool PhysicalRgb(uint64_t v) {
    return (v >= 1 && v <= 8) || (v >= 17 && v <= 38) ||
           (v >= 41 && v <= 45) || v == 49;
}
// Closed grammar, at most Envelope -> Body -> Mode/Rgb -> leaf (depth 3).
// It runs before nanopb and therefore before any callback or admission helper.
inline bool Scan(const uint8_t *b, size_t size, Message message, unsigned depth = 0) {
    if ((!b && size) || depth > 3) return false;
    size_t i = 0; unsigned previous = 0, count = 0; uint32_t seen = 0;
    while (i < size) {
        uint64_t key, v;
        if (!Varint(b, size, i, key) || key > UINT32_MAX) return false;
        const unsigned tag = unsigned(key >> 3), type = unsigned(key & 7);
        Rule r;
        if (!RuleFor(message, tag, r) || tag < previous) return false;
        const bool repeated_child = r.kind == Kind::Child && r.count > 1;
        count = tag == previous ? count + 1 : 1;
        if (tag == previous && !repeated_child) return false;
        if (repeated_child && count > r.count) return false;
        previous = tag;
        if (tag < 32) seen |= uint32_t(1) << tag;
        if (r.kind == Kind::Scalar) {
            if (type != 0 || !Varint(b, size, i, v) || (!v && !(message == Message::Envelope && tag == 30))) return false;
            if (!(message == Message::Envelope && tag == 2) && v > r.maximum) return false;
            if (message == Message::Envelope && tag == 3 && v != 1 && (v < 15 || v > 20)) return false;
            if (message == Message::Color && tag == 1 && !PhysicalRgb(v)) return false;
            continue;
        }
        if (type != 2 || !Varint(b, size, i, v) || v > size - i) return false;
        const size_t n = size_t(v); const uint8_t *part = b + i; i += n;
        if (r.kind == Kind::Packed) {
            if (!n) return false;
            size_t j = 0; unsigned elements = 0;
            while (j < n) {
                if (!Varint(part, n, j, v) || v > r.maximum || ++elements > r.count) return false;
                if (message == Message::Mode && tag == 4 && !v) return false;
            }
        } else {
            if (n > r.maximum) return false;
            if (r.kind == Kind::Child) { if (!Scan(part, n, r.child, depth + 1)) return false; }
            else if (!n) return false; // proto3 bytes/string defaults must be omitted
            else if (r.kind == Kind::String && !Text(part, n)) return false;
            if (message == Message::Envelope && (tag == 25 || tag == 26) && n != 32) return false;
            if (message == Message::Body && tag == 5 && n < 608) return false;
        }
    }
    if (message == Message::Body && (seen & 0x32) != 0x32) return false; // version,row,native
    if (message == Message::Socd && (seen & 6) != 6) return false;
    if (message == Message::Remap && !(seen & 2)) return false;
    if (message == Message::Color && !(seen & 2)) return false;
    return true;
}
inline bool FindSpan(const uint8_t *b, size_t size, unsigned wanted, BorrowedSpan &span) {
    size_t i = 0;
    while (i < size) {
        uint64_t key, n;
        if (!Varint(b, size, i, key)) return false;
        if ((key & 7) == 0) { if (!Varint(b, size, i, n)) return false; }
        else if ((key & 7) == 2) {
            if (!Varint(b, size, i, n) || n > size - i) return false;
            if ((key >> 3) == wanted) { span.bytes = b + i; span.size = size_t(n); }
            i += size_t(n);
        } else return false;
    }
    return true;
}
inline bool DecodeSpan(pb_istream_t *s, const pb_field_t *, void **arg) {
    auto &span = *static_cast<BorrowedSpan *>(*arg);
    if (span.seen || !span.bytes || span.size > span.maximum || s->bytes_left != span.size) return false;
    span.seen = true; uint8_t chunk[32]; size_t pos = 0;
    while (s->bytes_left) {
        const size_t n = s->bytes_left < sizeof chunk ? s->bytes_left : sizeof chunk;
        if (!pb_read(s, chunk, n) || std::memcmp(chunk, span.bytes + pos, n)) return false;
        pos += n;
    }
    return true;
}
inline bool EncodeSpan(pb_ostream_t *s, const pb_field_t *f, void *const *arg) {
    const auto &span = *static_cast<const BorrowedSpan *>(*arg);
    return span.seen && span.bytes && span.size <= span.maximum &&
           pb_encode_tag_for_field(s, f) && pb_encode_string(s, span.bytes, span.size);
}
struct Compare { const uint8_t *bytes; size_t size; size_t position; };
inline bool RoundTrip(const uint8_t *bytes, size_t size, const pb_msgdesc_t *fields, const void *message) {
    Compare expected{bytes, size, 0}; pb_ostream_t out{};
    out.state = &expected; out.max_size = size;
    out.callback = [](pb_ostream_t *s, const pb_byte_t *b, size_t n) -> bool {
        auto &e = *static_cast<Compare *>(s->state);
        if (e.position > e.size || n > e.size - e.position ||
            std::memcmp(e.bytes + e.position, b, n) != 0) return false;
        e.position += n;
        return true;
    };
    return pb_encode(&out, fields, message) && out.bytes_written == size && expected.position == size;
}
} // namespace wire

// Routing is deliberately separate from package admission. Preserve the legacy
// parser's legal unknown/fixed fields and nonminimal scalar acceptance here,
// while ensuring ANY version3 occurrence can never fall through as version1/2.
// Package admission itself always runs the strict complete canonical scanner.
enum class ProtocolRoute : uint8_t { Legacy, Package, Malformed };
inline ProtocolRoute RouteProtocol(const uint8_t *b, size_t size) {
    if ((!b && size) || !size) return ProtocolRoute::Malformed;
    size_t i = 0; bool package = false;
    auto raw_varint = [&](uint64_t &v) -> bool {
        v = 0;
        for (unsigned shift = 0; shift < 70; shift += 7) {
            if (i == size) return false;
            const uint8_t byte = b[i++];
            if (shift == 63 && byte > 1) return false;
            v |= uint64_t(byte & 127) << shift;
            if (!(byte & 128)) return true;
        }
        return false;
    };
    while (i < size) {
        uint64_t key, value;
        if (!raw_varint(key) || key > UINT32_MAX || !(key >> 3)) return ProtocolRoute::Malformed;
        const unsigned tag = unsigned(key >> 3), type = unsigned(key & 7);
        if (type == 0) {
            if (!raw_varint(value)) return ProtocolRoute::Malformed;
            if (tag == 1 && (value == 3 || value == 4)) package = true;
        } else {
            if (tag == 1) return ProtocolRoute::Malformed;
            if (type == 2) { if (!raw_varint(value)) return ProtocolRoute::Malformed; }
            else if (type == 1) value = 8;
            else if (type == 5) value = 4;
            else return ProtocolRoute::Malformed;
            if (value > size - i) return ProtocolRoute::Malformed;
            i += size_t(value);
        }
    }
    return package ? ProtocolRoute::Package : ProtocolRoute::Legacy;
}

inline bool DecodeCanonicalRequest(const uint8_t *bytes, size_t size, EnvelopePhase &phase) {
    phase.Release(); phase.request = PackageEnvelope_init_zero;
    if (!size || size > 4580 || !wire::Scan(bytes, size, wire::Message::Envelope)) return false;
    phase.package.maximum = 4491; phase.native.maximum = 3336;
    if (!wire::FindSpan(bytes, size, 24, phase.package)) return false;
    if (phase.package.bytes) {
        if (!wire::FindSpan(phase.package.bytes, phase.package.size, 5, phase.native)) return false;
        phase.request.package_body.funcs.decode = wire::DecodeSpan;
        phase.request.package_body.arg = &phase.package;
    }
    auto input = pb_istream_from_buffer(bytes, size);
    if (!pb_decode(&input, PackageEnvelope_fields, &phase.request) || input.bytes_left) { phase.Release(); return false; }
    auto &r = phase.request;
    if ((r.protocol_version != 3 && r.protocol_version != 4) || !r.request_token ||
        (r.operation != PackageOperation_PACKAGE_STATUS && !r.expected_store_incarnation)) { phase.Release(); return false; }
    const bool target = r.target_id && r.expected_revision;
    const bool extras = r.target_id || r.expected_revision || r.replacement_name[0] || r.has_replacement_rank;
    if ((r.protocol_version == 3 && (extras || size > 4564)) ||
        (!LifecycleOperation(r.operation) && extras)) { phase.Release(); return false; }
    bool valid = false;
    if (r.operation == PackageOperation_PACKAGE_STATUS) valid = size <= 15 && !r.expected_store_generation &&
        !r.expected_config_generation && !r.expected_store_incarnation && !phase.package.bytes &&
        !r.has_expected_digest && !r.has_expected_config_sha256;
    else if (r.operation == PackageOperation_CREATE_PACKAGE) valid = r.protocol_version == 3 && r.expected_store_generation &&
        phase.package.seen && !r.has_expected_digest && r.has_expected_config_sha256;
    else if (r.operation == PackageOperation_QUERY_PACKAGE) valid = size <= 57 && !r.expected_store_generation &&
        !r.expected_config_generation && !phase.package.bytes && r.has_expected_digest && !r.has_expected_config_sha256;
    else if (LifecycleOperation(r.operation)) {
        valid = r.protocol_version == 4 && target && r.expected_store_generation &&
            !r.has_expected_digest && r.has_expected_config_sha256 &&
            phase.package.seen == (r.operation == PackageOperation_UPDATE_PACKAGE) &&
            bool(r.replacement_name[0]) == (r.operation == PackageOperation_RENAME_PACKAGE) &&
            r.has_replacement_rank == (r.operation == PackageOperation_REORDER_PACKAGE);
    }
    if (!valid) { phase.Release(); return false; }
    if (phase.package.seen) phase.request.package_body.funcs.encode = wire::EncodeSpan;
    if (!wire::RoundTrip(bytes, size, PackageEnvelope_fields, &phase.request)) { phase.Release(); return false; }
    return true;
}
// Error correlation inspects only the bounded closed outer grammar. Nested
// package bytes and SHA extents are payload validation, never trusted data.
// This does not admit a request or expose a decode callback.
inline bool TrustedOuterHeader(const uint8_t *bytes,size_t size,EnvelopePhase &phase) {
    phase.Release(); phase.request=PackageEnvelope_init_zero;
    if(!bytes||!size||size>4580)return false;
    size_t at=0; unsigned previous=0;
    while(at<size) {
        uint64_t key,value;
        if(!wire::Varint(bytes,size,at,key)||key>UINT32_MAX)return false;
        const unsigned tag=unsigned(key>>3),type=unsigned(key&7);
        wire::Rule rule;
        if(tag<=previous||!wire::RuleFor(wire::Message::Envelope,tag,rule))return false;
        if(phase.request.protocol_version==3 && tag>26)return false;
        previous=tag;
        if(rule.kind==wire::Kind::Scalar) {
            if(type||!wire::Varint(bytes,size,at,value)||(!value&&tag!=30)||
               (tag!=2&&value>UINT32_MAX))return false;
            switch(tag) {
            case 1:phase.request.protocol_version=uint32_t(value);break;
            case 2:phase.request.request_token=value;break;
            case 3:if((value!=1&&(value<15||value>20)) || (phase.request.protocol_version==3 && value>16))return false;
                phase.request.operation=static_cast<PackageOperation>(value);break;
            case 21:phase.request.expected_store_incarnation=uint32_t(value);break;
            default:break;
            }
        } else {
            if(type!=2||!wire::Varint(bytes,size,at,value)||value>size-at)return false;
            at+=size_t(value);
        }
    }
    if(phase.request.protocol_version==3 && size>4564)return false;
    return (phase.request.protocol_version==3||phase.request.protocol_version==4)&&phase.request.request_token&&
        (phase.request.operation==PackageOperation_PACKAGE_STATUS||
         ((phase.request.operation==PackageOperation_CREATE_PACKAGE||phase.request.operation==PackageOperation_QUERY_PACKAGE||LifecycleOperation(phase.request.operation))&&
          phase.request.expected_store_incarnation));
}
// Caller supplies the existing initialization owner; not a local/max-size body.
inline bool DecodeCanonicalBody(EnvelopePhase &phase, PackageBody &body) {
    body = PackageBody_init_zero;
    if ((phase.request.operation != PackageOperation_CREATE_PACKAGE && phase.request.operation != PackageOperation_UPDATE_PACKAGE) || !phase.package.seen || !phase.native.bytes) return false;
    phase.native.seen = false;
    body.native_body.funcs.decode = wire::DecodeSpan; body.native_body.arg = &phase.native;
    auto input = pb_istream_from_buffer(phase.package.bytes, phase.package.size);
    if (!pb_decode(&input, PackageBody_fields, &body) || input.bytes_left || !phase.native.seen) { body.native_body = {}; return false; }
    body.native_body.funcs.encode = wire::EncodeSpan;
    if (!wire::RoundTrip(phase.package.bytes, phase.package.size, PackageBody_fields, &body)) { body.native_body = {}; return false; }
    return body.version == 1 && body.has_row;
}
// Requires the exact immutable bytes accepted by DecodeCanonicalRequest. No
// re-encoding buffer: deleting the canonical token2 field is byte-identical to
// encoding that same envelope with request_token=0. No input is modified.
inline bool CreateDigest(const uint8_t *bytes, size_t size, const EnvelopePhase &phase, uint8_t out[32]) {
    if (phase.request.operation != PackageOperation_CREATE_PACKAGE || !phase.package.seen) return false;
    size_t i = 0, token_begin = 0, token_end = 0;
    while (i < size) {
        const size_t begin = i; uint64_t key, n;
        if (!wire::Varint(bytes, size, i, key)) return false;
        if ((key & 7) == 0) { if (!wire::Varint(bytes, size, i, n)) return false; }
        else if ((key & 7) == 2) { if (!wire::Varint(bytes, size, i, n) || n > size - i) return false; i += size_t(n); }
        else return false;
        if (key == 16) { token_begin = begin; token_end = i; }
    }
    if (!token_end) return false;
    Sha256 hash; static constexpr char domain[] = "Glyph.Package.Create.v1";
    hash.Update(domain, sizeof domain); hash.Update(bytes, token_begin);
    hash.Update(bytes + token_end, size - token_end); hash.Final(out);
    return true;
}
} // namespace glyph_package
