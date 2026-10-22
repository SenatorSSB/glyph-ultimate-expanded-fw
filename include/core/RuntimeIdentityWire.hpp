#pragma once

#include <cstddef>
#include <cstdint>
#include <cstring>

namespace runtime_identity {
constexpr size_t kRequestBytes = 16;
constexpr size_t kResponseBytes = 72;
constexpr uint32_t kPartialTimeoutMs = 250;
constexpr uint8_t kMagic[4] = {0xa5, 'G', 'R', 'I'};
enum class Status : uint8_t {
    Persisted, NoPrimary, Configurator, Recovery, NoMode, NonUltimate,
    SourceFallback, EmbeddedLegacy, StoreUnavailable, ObjectMismatch,
    ContextUnavailable, DigestFailure, SnapshotUnavailable
};
struct Snapshot {
    Status status = Status::NoPrimary;
    uint8_t backend = 0;
    uint16_t row = 0;
    uint32_t requested = 0;
    uint32_t incarnation = 0, id = 0, revision = 0, schema = 0;
    uint8_t digest[32] = {};
};
inline uint64_t ReadLE(const uint8_t *p, size_t n) {
    uint64_t value = 0;
    for (size_t i = 0; i < n; ++i) value |= uint64_t(p[i]) << (8*i);
    return value;
}
inline void WriteLE(uint8_t *p, uint64_t value, size_t n) {
    for (size_t i = 0; i < n; ++i) p[i] = uint8_t(value >> (8*i));
}
inline bool DecodeRequest(const uint8_t *bytes, size_t length, uint64_t &token) {
    if (length != kRequestBytes || std::memcmp(bytes, kMagic, 4) ||
        bytes[4] != 1 || bytes[5] != 1 || ReadLE(bytes+6, 2) != kRequestBytes) return false;
    token = ReadLE(bytes+8, 8);
    return token != 0;
}
inline void EncodeResponse(uint64_t token, const Snapshot &s, uint8_t bytes[kResponseBytes]) {
    std::memset(bytes, 0, kResponseBytes);
    std::memcpy(bytes, kMagic, 4);
    bytes[4] = 1; bytes[5] = 2;
    WriteLE(bytes+6, kResponseBytes, 2); WriteLE(bytes+8, token, 8);
    bytes[16] = static_cast<uint8_t>(s.status); bytes[17] = s.backend;
    WriteLE(bytes+18, s.row, 2); WriteLE(bytes+20, s.requested, 4);
    if (s.status != Status::Persisted) return;
    WriteLE(bytes+24, s.incarnation, 4); WriteLE(bytes+28, s.id, 4);
    WriteLE(bytes+32, s.revision, 4); WriteLE(bytes+36, s.schema, 4);
    std::memcpy(bytes+40, s.digest, 32);
}

// Identity-only RX. No length-controlled allocation, waits or dispatch table.
class RequestParser {
  public:
    bool HasPartialFrame() const { return _used != 0; }
    void Expire(uint32_t now) {
        if (_used && uint32_t(now - _started) >= kPartialTimeoutMs) _used = 0;
    }
    bool Consume(uint8_t byte, uint32_t now, uint64_t &token) {
        Expire(now);
        if (_used < 4 && byte != kMagic[_used]) {
            _used = byte == kMagic[0] ? 1 : 0;
            _started = now;
            return false;
        }
        if (!_used) _started = now;
        _bytes[_used++] = byte;
        if (_used < kRequestBytes) return false;
        _used = 0;
        return DecodeRequest(_bytes, sizeof(_bytes), token);
    }
  private:
    uint8_t _bytes[kRequestBytes] = {};
    uint8_t _used = 0;
    uint32_t _started = 0;
};
} // namespace runtime_identity
