#include "core/PackageStorageFormat.hpp"
#include "core/ProfileStoreName.hpp"
#include "core/Sha256.hpp"
#include <climits>
#include <cstdio>
#include <cstring>
#include <new>

namespace package_storage {
namespace {
uint32_t CrcStep(uint32_t crc, uint8_t byte) {
    crc ^= byte;
    for (unsigned j = 0; j < 8; ++j)
        crc = (crc >> 1) ^ (0xedb88320u & (0u - (crc & 1)));
    return crc;
}
uint32_t CrcFeed(uint32_t crc, const uint8_t *bytes, size_t length) {
    while (length--) crc = CrcStep(crc, *bytes++);
    return crc;
}
bool Zero(const uint8_t *p, size_t n) {
    while (n--) if (*p++) return false;
    return true;
}
bool Equal(const uint8_t *a, const uint8_t *b, size_t n) {
    return std::memcmp(a, b, n) == 0;
}
bool Add(uint64_t a, uint64_t b, uint64_t &out) {
    if (b > UINT64_MAX - a) return false;
    out = a + b; return true;
}
bool Multiply(uint64_t a, uint64_t b, uint64_t &out) {
    if (b && a > UINT64_MAX / b) return false;
    out = a * b; return true;
}
bool Round(uint64_t n, uint64_t unit, uint64_t &out) {
    uint64_t sum;
    return unit && Add(n, unit - 1, sum) && Multiply(sum / unit, unit, out);
}
bool ReceiptValid(const uint8_t *p) {
    if (!Get64(p + 24)) return true;
    const auto status = Get32(p + 64);
    return (status == 0 || status == 12) && Get32(p + 68) <= Get32(p + 16) &&
           Get32(p + 76) <= Get32(p + 8);
}
const uint8_t *Entry(const RootView &r, size_t i) { return r.prefix + 320 + i * 56; }
}
uint16_t Get16(const uint8_t *p) { return uint16_t(p[0]) | uint16_t(p[1]) << 8; }
uint32_t Get32(const uint8_t *p) {
    uint32_t value = 0;
    for (unsigned i = 0; i < 4; ++i) value |= uint32_t(p[i]) << (8 * i);
    return value;
}
uint64_t Get64(const uint8_t *p) {
    uint64_t value = 0;
    for (unsigned i = 0; i < 8; ++i) value |= uint64_t(p[i]) << (8 * i);
    return value;
}
void Put16(uint8_t *p, uint16_t value) { p[0] = value; p[1] = value >> 8; }
void Put32(uint8_t *p, uint32_t value) { for (unsigned i = 0; i < 4; ++i) p[i] = value >> (8 * i); }
void Put64(uint8_t *p, uint64_t value) { for (unsigned i = 0; i < 8; ++i) p[i] = value >> (8 * i); }
uint32_t Crc32(const uint8_t *p, size_t n) { return ~CrcFeed(~0u, p, n); }
uint32_t RootCrc(const RootView &r) {
    return ~CrcFeed(CrcFeed(~0u, r.prefix, kRootPrefixBytes), r.intent, kIntentBytes);
}
void HashRoot(const RootView &r, uint8_t out[32]) {
    Sha256 sha;
    sha.Update(r.prefix, kRootPrefixBytes); sha.Update(r.intent, kIntentBytes);
    sha.Update(r.trailer, 4); sha.Final(out);
}
void EmptyIntent(uint8_t *p) {
    std::memset(p, 0, kIntentBytes);
    std::memcpy(p, "PKI1", 4); Put16(p + 4, 1); Put16(p + 6, kIntentBytes);
}
bool IntentValid(const uint8_t *p) {
    if (!p || !Equal(p, reinterpret_cast<const uint8_t *>("PKI1"), 4) ||
        Get16(p + 4) != 1 || Get16(p + 6) != kIntentBytes || !Zero(p + 400, 112)) return false;
    if (!Get32(p + 8)) return Zero(p + 8, kIntentBytes - 8);
    const auto phase = Get32(p + 12), terminal = Get32(p + 16), flags = Get32(p + 20);
    if (Get32(p + 8) != 15 || phase < 1 || phase > 5 || terminal > 4 || flags > 1 ||
        bool(flags) != bool(Get32(p + 100))) return false;
    const auto baseline_id = Get32(p + 396), generation = Get32(p + 76), sequence = Get32(p + 368);
    if (Get64(p + 24) <= Get64(p + 388) || !Get32(p + 64) || baseline_id == UINT32_MAX ||
        Get32(p + 68) != baseline_id + 1 || Get32(p + 72) != 1 ||
        !generation || generation == UINT32_MAX || Get32(p + 80) != generation + 1 ||
        sequence == UINT32_MAX || Get32(p + 84) != sequence + 1) return false;
    const auto rows = Get32(p + 372), rgbs = Get32(p + 380);
    if (rows >= 30 || Get32(p + 96) != rows || Get32(p + 376) != rows + 1 ||
        rgbs > 30 || rgbs + flags > 30 || Get32(p + 384) != rgbs + flags ||
        Get32(p + 100) != (flags ? rgbs + 1 : 0)) return false;
    const auto record = Get32(p + 360), config = Get32(p + 364);
    return record > kRecordHeaderBytes && record <= kRecordMaxBytes && config &&
        config <= kConfigBodyMaxBytes && ((phase == 5) == (terminal == 3));
}
bool SourcePrefixValid(const uint8_t *p) {
    if (!p || Get32(p) != 0x32534450u || Get16(p + 6) > 64 || !Get32(p + 12) ||
        Get32(p + 20) > 2 || Get32(p + 84) > 2 || Get32(p + 64) > 12 || !ReceiptValid(p)) return false;
    if (Get32(p + 20) && ((Get32(p + 80) != 2 && Get32(p + 80) != 3) || !Get32(p + 84))) return false;
    for (size_t i = 0; i < Get32(p + 84); ++i)
        if (!Get32(p + 120 + i * 4) || Get32(p + 120 + i * 4) > Get32(p + 16) ||
            !Get32(p + 128 + i * 4)) return false;
    for (size_t i = 0; i < Get16(p + 6); ++i) {
        const auto *e = p + 320 + i * 56;
        if (!Get32(e) || !Get32(e + 4) || Get32(e + 8) >= Get32(e + 4) ||
            Get32(e) > Get32(p + 16) || !ProfileStoreNameValid(reinterpret_cast<const char *>(e + 20), 33)) return false;
        for (size_t j = 0; j < i; ++j) if (Get32(p + 320 + j * 56) == Get32(e)) return false;
    }
    return true;
}
bool RootValid(const RootView &r) {
    if (!r.prefix || !r.intent || !r.trailer || !SourcePrefixValid(r.prefix) ||
        Get16(r.prefix + 4) != 3 || Get32(r.prefix + 296) != 1 ||
        !Zero(r.prefix + 304, 16) || RootCrc(r) != Get32(r.trailer) || !IntentValid(r.intent)) return false;
    uint32_t rows = 0, rgbs = 0;
    bool intended_entry = false;
    const auto count = Get16(r.prefix + 6);
    for (size_t i = 0; i < count; ++i) {
        const auto *e = Entry(r, i);
        if (e[53] > 1) return false;
        if (!e[53]) { if (e[54] || e[55]) return false; continue; }
        if (Get32(e + 12) != 5 || Get32(e + 8) || !e[54] || e[54] > 30 || e[55] > 30) return false;
        const uint32_t row = 1u << (e[54] - 1);
        const uint32_t rgb = e[55] ? 1u << (e[55] - 1) : 0;
        if ((rows & row) || (rgbs & rgb)) return false;
        rows |= row; rgbs |= rgb;
        intended_entry |= Get32(e) == Get32(r.intent + 68) && Get32(e + 4) == Get32(r.intent + 72) &&
            uint32_t(e[54] - 1) == Get32(r.intent + 96) && e[55] == Get32(r.intent + 100);
    }
    if (!Zero(r.prefix + 320 + count * 56, kRootPrefixBytes - 320 - count * 56)) return false;
    if (!Get32(r.intent + 8)) return true;
    if (!intended_entry || Get32(r.prefix + 12) != Get32(r.intent + 64) ||
        Get32(r.prefix + 300) != Get32(r.intent + 84) || !Equal(r.prefix + 264, r.intent + 296, 32) ||
        Get32(r.prefix + 8) < Get32(r.intent + 80)) return false;
    if (Get32(r.prefix + 8) == Get32(r.intent + 80))
        return Get32(r.prefix + 16) == Get32(r.intent + 68) && Get64(r.prefix + 24) == Get64(r.intent + 24) &&
            Equal(r.prefix + 32, r.intent + 32, 32) && !Get32(r.prefix + 64) &&
            Get32(r.prefix + 68) == Get32(r.intent + 68) && Get32(r.prefix + 72) == 1 &&
            Get32(r.prefix + 76) == Get32(r.intent + 80);
    return Get32(r.intent + 12) == 5 && Get32(r.intent + 16) == 3 &&
        Get64(r.prefix + 24) > Get64(r.intent + 24) && !Zero(r.prefix + 32, 32) &&
        (Get32(r.prefix + 64) == 0 || Get32(r.prefix + 64) == 12) && Get32(r.prefix + 68) &&
        Get32(r.prefix + 68) <= Get32(r.prefix + 16) && Get32(r.prefix + 76) == Get32(r.prefix + 8);
}
bool ControlValid(const uint8_t *h, const RootView &r) {
    if (!h || Get32(h) != 0x32435350u || Get32(h + 4) < 1 || Get32(h + 4) > 3 ||
        Get32(h + 8) != kRootBytes || !RootValid(r)) return false;
    uint32_t crc = CrcFeed(~0u, r.prefix, kRootPrefixBytes);
    crc = CrcFeed(crc, r.intent, kIntentBytes); crc = CrcFeed(crc, r.trailer, 4);
    return Get32(h + 12) == (Crc32(h, 12) ^ ~crc);
}
bool ControlPhaseValid(const uint8_t *h, const uint8_t *p) {
    const auto outer = Get32(h + 4), phase = Get32(p + 12), terminal = Get32(p + 16);
    return (outer == 1 && phase == 1 && terminal == 0) ||
        (outer == 2 && phase >= 2 && phase <= 4 && terminal == 0) ||
        (outer == 3 && phase == 5 && terminal == 3);
}
void FinishRoot(uint8_t *p, const uint8_t *intent, uint8_t *trailer) {
    Put32(trailer, RootCrc({p, intent, trailer}));
}
void FinishControl(uint8_t *h, const RootView &r, uint32_t phase) {
    Put32(h, 0x32435350u); Put32(h + 4, phase); Put32(h + 8, kRootBytes);
    uint32_t crc = CrcFeed(~0u, r.prefix, kRootPrefixBytes);
    crc = CrcFeed(crc, r.intent, kIntentBytes); crc = CrcFeed(crc, r.trailer, 4);
    Put32(h + 12, Crc32(h, 12) ^ ~crc);
}
bool SameRoot(const RootView &a, const RootView &b) {
    return Equal(a.prefix, b.prefix, kRootPrefixBytes) && Equal(a.intent, b.intent, kIntentBytes) && Equal(a.trailer, b.trailer, 4);
}
bool SameImmutableIntent(const uint8_t *a, const uint8_t *b) {
    // Only phase/terminal (12..19) are mutable checkpoints.
    return Equal(a, b, 12) && Equal(a + 20, b + 20, kIntentBytes - 20);
}
bool RootPairValid(const RootView &a, const RootView &b, unsigned &selected) {
    if (!RootValid(a) || !RootValid(b) || Get32(a.prefix + 12) != Get32(b.prefix + 12)) return false;
    selected = Get32(b.prefix + 8) > Get32(a.prefix + 8) ? 1 : 0;
    const auto &current = selected ? b : a; const auto &prior = selected ? a : b;
    const auto g = Get32(current.prefix + 8), pg = Get32(prior.prefix + 8);
    if (g - pg > 1 || Get32(current.prefix + 16) < Get32(prior.prefix + 16) ||
        Get64(current.prefix + 24) < Get64(prior.prefix + 24) || Get32(current.prefix + 300) < Get32(prior.prefix + 300)) return false;
    if (g == pg) return SameRoot(a, b);
    if ((Get32(a.prefix + 8) & 1u) != 0 || (Get32(b.prefix + 8) & 1u) != 1) return false;
    for (size_t i = 0; i < Get16(prior.prefix + 6); ++i) {
        const auto *e = Entry(prior, i); if (!e[53]) continue;
        bool found = false;
        for (size_t j = 0; j < Get16(current.prefix + 6); ++j)
            if (Equal(e, Entry(current, j), 56)) { found = true; break; }
        if (!found) return false;
    }
    return true;
}
bool RecordValid(const uint8_t *p, size_t n) {
    if (!p || n <= kRecordHeaderBytes || n > kRecordMaxBytes || Get32(p) != 0x31525055u ||
        Get16(p + 4) != 2 || Get16(p + 6) != 2 || !Get32(p + 8) || !Get32(p + 12) ||
        Get32(p + 16) != 1 || Get32(p + 20) != n - kRecordHeaderBytes || !Get64(p + 32) ||
        Get32(p + 72) >= 30 || Get32(p + 76) > 30 || Get32(p + 116) != 1 ||
        !Get32(p + 120) || !Get32(p + 124) || Crc32(p, 24) != Get32(p + 24) ||
        Crc32(p + kRecordHeaderBytes, n - kRecordHeaderBytes) != Get32(p + 28)) return false;
    uint32_t crc = ~0u;
    for (size_t i = 0; i < kRecordHeaderBytes; ++i) crc = CrcStep(crc, i >= 112 && i < 116 ? 0 : p[i]);
    return ~crc == Get32(p + 112);
}
bool RecordMatchesIntent(const uint8_t *p, size_t n, const uint8_t *intent) {
    if (!IntentValid(intent) || !Get32(intent + 8) || !RecordValid(p, n) || n != Get32(intent + 360) ||
        Get32(p + 8) != Get32(intent + 64) || Get32(p + 12) != Get32(intent + 68) ||
        Get64(p + 32) != Get64(intent + 24) || !Equal(p + 40, intent + 32, 32) ||
        Get32(p + 72) != Get32(intent + 96) || Get32(p + 76) != Get32(intent + 100) ||
        !Equal(p + 80, intent + 104, 32) || Get32(p + 120) != Get32(intent + 80) ||
        Get32(p + 124) != Get32(intent + 84)) return false;
    Sha256 hash;
    uint8_t digest[32]; hash.Update(p, n); hash.Final(digest);
    if (!Equal(digest, intent + 168, 32)) return false;
    hash.~Sha256(); ::new (&hash) Sha256; hash.Update(p, kRecordHeaderBytes); hash.Final(digest);
    return Equal(digest, intent + 328, 32);
}
bool MakeRecordHeader(uint8_t *p, const uint8_t *body, size_t n, const RecordIdentity &v) {
    if (!p || !body || !n || n > 3341 || !v.incarnation || !v.id || !v.token || v.row >= 30 ||
        v.rgb > 30 || !v.generation || !v.sequence || !v.digest || !v.baseline_config_sha) return false;
    std::memset(p, 0, kRecordHeaderBytes);
    Put32(p, 0x31525055u); Put16(p + 4, 2); Put16(p + 6, 2);
    Put32(p + 8, v.incarnation); Put32(p + 12, v.id); Put32(p + 16, 1); Put32(p + 20, n);
    Put32(p + 24, Crc32(p, 24)); Put32(p + 28, Crc32(body, n)); Put64(p + 32, v.token);
    std::memcpy(p + 40, v.digest, 32); Put32(p + 72, v.row); Put32(p + 76, v.rgb);
    std::memcpy(p + 80, v.baseline_config_sha, 32); Put32(p + 116, 1);
    Put32(p + 120, v.generation); Put32(p + 124, v.sequence); Put32(p + 112, Crc32(p, kRecordHeaderBytes));
    return true;
}
bool RecordPath(char *out, size_t capacity, uint32_t id, uint32_t rev, bool temporary) {
    if (!out || capacity < 30 || !id || !rev) return false;
    const int n = std::snprintf(out, capacity, "/ultpkg-%08x-%08x.%s", unsigned(id), unsigned(rev), temporary ? "tmp" : "bin");
    return n == 29 && size_t(n) < capacity;
}
bool FileCharge(uint64_t bytes, uint64_t &charged) {
    uint64_t aligned, numerator, blocks;
    // Pinned geometry: 4096 - 4*(1+floor(log2(128))) == 4064.
    return Round(bytes, 256, aligned) && Add(aligned, 4063, numerator) &&
        Multiply(numerator / 4064, 4096, blocks) && Round(blocks, 4096, charged);
}
bool AdmissionNeed(const AdmissionArithmetic &v, uint64_t &needed) {
    needed = 0;
    if (v.rows >= 30 || v.rgbs > 30 || (v.with_rgb && v.rgbs == 30) || v.count >= 64 ||
        v.high_id == UINT32_MAX || !v.generation || v.generation == UINT32_MAX || v.sequence == UINT32_MAX ||
        v.token <= v.high_token || !v.config_bytes || v.config_bytes > kConfigBodyMaxBytes ||
        v.record_bytes <= kRecordHeaderBytes || v.record_bytes > kRecordMaxBytes || v.namespace_files > 256 ||
        v.total != 524288 || v.used % 4096 || v.free % 4096) return false;
    uint64_t sum, record, root, config, config_file, names, metadata, staging;
    if (!Add(v.used, v.free, sum) || sum != v.total || !FileCharge(v.record_bytes, record) ||
        !FileCharge(kControlBytes, root) || !Add(v.config_bytes, 8, config_file) || !FileCharge(config_file, config) ||
        !Add(v.namespace_files, 16, names) || !Multiply(names, 128, names) || !Round(names, 4096, names) ||
        !Multiply(names, 2, metadata) || !Add(metadata, 8 * 4096, metadata) ||
        !Multiply(record, 2, staging) || !Multiply(root, 5, root) || !Add(staging, root, staging) ||
        !Multiply(config, 2, config) || !Add(staging, config, staging) || !Add(staging, 4 * 4096, staging) ||
        !Add(staging, metadata, needed) || !Add(needed, 16384, needed) || !Add(v.protected_bytes, needed, sum)) return false;
    return v.free >= needed && v.total >= sum;
}
bool ExactGeometry(const CheckedStorage::Geometry &g) {
    uint64_t sum;
    return g.total_bytes == 524288 && g.erase_bytes == 4096 && g.program_bytes == 256 && g.read_bytes == 256 &&
        g.block_count == 128 && g.cache_bytes == 256 && g.name_max == 31 &&
        !(g.used_bytes % 4096) && !(g.free_bytes % 4096) && Add(g.used_bytes, g.free_bytes, sum) && sum == g.total_bytes;
}
}
