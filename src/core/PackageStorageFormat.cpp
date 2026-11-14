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
    if (!p || !Equal(p, reinterpret_cast<const uint8_t *>("PKI1"), 4) || Get16(p + 6) != kIntentBytes)
        return false;
    const uint32_t format = Get16(p + 4), op = Get32(p + 8);
    if (!op) return format == 1 && Zero(p + 8, kIntentBytes - 8);
    const bool create = op == 15, erase = op == 20;
    if (create ? (format != 1 || !Zero(p + 400, 112)) :
                 (!LifecycleOperation(op) || format != 2 || (!Zero(p + 476, 36) || Zero(p + 444, 32)))) return false;
    const auto phase = Get32(p + 12), terminal = Get32(p + 16), flags = Get32(p + 20);
    const auto id = Get32(p + 68), revision = Get32(p + 72), generation = Get32(p + 76);
    const auto sequence = Get32(p + 368), baseline_id = Get32(p + 396);
    if (phase < 1 || phase > 5 || terminal > 4 || ((phase == 5) != (terminal == 3)) ||
        flags > 1 || flags != bool(Get32(p + 100)) || Get64(p + 24) <= Get64(p + 388) ||
        !Get32(p + 64) || !id || !generation || generation == UINT32_MAX ||
        Get32(p + 80) != generation + 1 || sequence == UINT32_MAX || Get32(p + 84) != sequence + 1)
        return false;
    const auto rows = Get32(p + 372), rgbs = Get32(p + 380), row = Get32(p + 96), rgb = Get32(p + 100);
    const auto final_rows = Get32(p + 376), final_rgbs = Get32(p + 384);
    const auto record = Get32(p + 360), config = Get32(p + 364);
    if (rgbs > 30 || rows > 30 || final_rgbs > 30 || final_rows > 30 || !config ||
        config > kConfigBodyMaxBytes || (!erase && (record <= kRecordHeaderBytes || record > kRecordMaxBytes)))
        return false;
    if (create) return baseline_id != UINT32_MAX && id == baseline_id + 1 && revision == 1 &&
        row == rows && final_rows == rows + 1 && final_rgbs == rgbs + flags && rgb == (flags ? rgbs + 1 : 0);
    const auto old_revision = Get32(p + 400), old_row = Get32(p + 404), old_rgb = Get32(p + 408);
    if (!sequence || id > baseline_id || !old_revision || old_revision == UINT32_MAX ||
        revision != old_revision + 1 || old_row >= rows || row != old_row || old_rgb > rgbs ||
        Zero(p + 412, 32) || final_rows != rows - unsigned(erase)) return false;
    if (erase) return rgb == old_rgb && final_rgbs == rgbs - unsigned(old_rgb != 0) &&
        !record && Zero(p + 168, 96) && Zero(p + 328, 32);
    if (op != 17 && rgb != old_rgb) return false;
    const uint32_t expected_rgb = rgb && !old_rgb ? rgbs + 1 : (rgb ? old_rgb : 0);
    return rgb == expected_rgb && final_rgbs == rgbs - unsigned(old_rgb != 0) + unsigned(rgb != 0);
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
        (Get32(r.prefix + 304) > Get32(r.prefix + 300) || !Zero(r.prefix + 308, 12)) || RootCrc(r) != Get32(r.trailer) || !IntentValid(r.intent)) return false;
    uint32_t rows = 0, rgbs = 0;
    bool intended_entry = false, has_target = false;
    const auto count = Get16(r.prefix + 6);
    for (size_t i = 0; i < count; ++i) {
        const auto *e = Entry(r, i);
        has_target |= Get32(e) == Get32(r.intent + 68);
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
    if ((Get32(r.intent + 8) == 20 ? has_target : !intended_entry) || Get32(r.prefix + 12) != Get32(r.intent + 64) ||
        Get32(r.prefix + 300) != Get32(r.intent + 84) || !Equal(r.prefix + 264, r.intent + 296, 32) ||
        Get32(r.prefix + 8) < Get32(r.intent + 80)) return false;
    if (Get32(r.prefix + 8) == Get32(r.intent + 80))
        return Get32(r.prefix + 16) == Get32(r.intent + (Get32(r.intent + 8) == 15 ? 68 : 396)) && Get64(r.prefix + 24) == Get64(r.intent + 24) &&
            Equal(r.prefix + 32, r.intent + 32, 32) && !Get32(r.prefix + 64) &&
            Get32(r.prefix + 68) == Get32(r.intent + 68) && Get32(r.prefix + 72) == Get32(r.intent + 72) &&
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
// Compare the complete directory in publication order. Only the target metadata
// and the exact one-slot left shifts caused by dense compaction may differ.
bool LifecycleRootChange(const uint8_t *old, const uint8_t *next, uint32_t op,
                         uint32_t id, uint32_t revision, uint32_t row, uint32_t rgb, uint32_t new_rgb) {
    const bool erase = op == 20, drop_rgb = rgb && (erase || !new_rgb);
    size_t out = 0;
    bool found = false;
    const uint32_t compaction = (erase || drop_rgb) ? Get32(next + 300) : Get32(old + 304);
    if (Get32(next + 304) != compaction || Get16(next + 6) + unsigned(erase) != Get16(old + 6) ||
        Get32(next + 16) != Get32(old + 16)) return false;
    for (size_t i = 0; i < Get16(old + 6); ++i) {
        const auto *a = old + 320 + 56 * i;
        if (Get32(a) == id) {
            if (found || a[53] != 1 || Get32(a + 4) != revision || a[54] != row + 1 || a[55] != rgb)
                return false;
            found = true;
            if (erase) continue;
            const auto *b = next + 320 + 56 * out++;
            if (Get32(b) != id || Get32(b + 4) != revision + 1 || !Equal(a + 8, b + 8, 8) ||
                b[53] != 1 || b[54] != a[54] || b[55] != new_rgb) return false;
            if (op == 18 && Get32(a + 16) != Get32(b + 16)) return false;
            if (op == 19 && !Equal(a + 20, b + 20, 33)) return false;
        } else {
            const auto *b = next + 320 + 56 * out++;
            if (!Equal(a, b, 54) || b[54] != a[54] - unsigned(erase && a[54] > row + 1) ||
                b[55] != a[55] - unsigned(drop_rgb && a[55] > rgb)) return false;
        }
    }
    return found && out == Get16(next + 6);
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
    const auto *intent = current.intent;
    if (LifecycleOperation(Get32(intent + 8)) && g == Get32(intent + 80))
        return LifecycleRootChange(prior.prefix, current.prefix, Get32(intent + 8), Get32(intent + 68),
                                   Get32(intent + 400), Get32(intent + 404), Get32(intent + 408), Get32(intent + 100));
    if (Get32(current.prefix + 304) != Get32(prior.prefix + 304)) return false;
    for (size_t i = 0; i < Get16(prior.prefix + 6); ++i) {
        const auto *e = Entry(prior, i); if (!e[53]) continue;
        bool found = false;
        for (size_t j = 0; j < Get16(current.prefix + 6); ++j)
            if (Equal(e, Entry(current, j), 56)) { found = true; break; }
        if (!found) return false;
    }
    return true;
}
bool RecordSlotsMatch(const uint8_t *record, uint8_t row1, uint8_t rgb1, uint32_t compaction_sequence) {
    const uint32_t original_row1 = Get32(record + 72) + 1, original_rgb1 = Get32(record + 76);
    if (Get32(record + 124) >= compaction_sequence)
        return original_row1 == row1 && original_rgb1 == rgb1;
    // An untouched survivor retains its receipt indices at publication. Dense
    // removals can only move existing slots left, never create or drop its RGB.
    return row1 && row1 <= original_row1 && rgb1 <= original_rgb1 && bool(rgb1) == bool(original_rgb1);
}
bool RecordValid(const uint8_t *p, size_t n) {
    if (!p || n <= kRecordHeaderBytes || n > kRecordMaxBytes || Get32(p) != 0x31525055u ||
        Get16(p + 4) != 2 || Get16(p + 6) != 2 || !Get32(p + 8) || !Get32(p + 12) ||
        !Get32(p + 16) || Get32(p + 20) != n - kRecordHeaderBytes || !Get64(p + 32) ||
        Get32(p + 72) >= 30 || Get32(p + 76) > 30 ||
        (Get32(p + 16) == 1 ? Get32(p + 116) != 1 :
         (Get16(p + 116) != 2 || Get16(p + 118) < 17 || Get16(p + 118) > 19)) ||
        !Get32(p + 120) || !Get32(p + 124) || Crc32(p, 24) != Get32(p + 24) ||
        Crc32(p + kRecordHeaderBytes, n - kRecordHeaderBytes) != Get32(p + 28)) return false;
    uint32_t crc = ~0u;
    for (size_t i = 0; i < kRecordHeaderBytes; ++i) crc = CrcStep(crc, i >= 112 && i < 116 ? 0 : p[i]);
    return ~crc == Get32(p + 112);
}
bool RecordMatchesIntent(const uint8_t *p, size_t n, const uint8_t *intent) {
    if (!IntentValid(intent) || !Get32(intent + 8) || !RecordValid(p, n) || n != Get32(intent + 360) ||
        Get32(p + 8) != Get32(intent + 64) || Get32(p + 12) != Get32(intent + 68) ||
        Get32(p + 16) != Get32(intent + 72) ||
        (Get16(p + 116) == 2 && Get16(p + 118) != Get32(intent + 8)) ||
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
    if (!v.revision || (v.revision == 1 ? (v.receipt_format != 1 || v.operation != 15) :
        (v.receipt_format != 2 || v.operation < 17 || v.operation > 19))) return false;
    std::memset(p, 0, kRecordHeaderBytes);
    Put32(p, 0x31525055u); Put16(p + 4, 2); Put16(p + 6, 2);
    Put32(p + 8, v.incarnation); Put32(p + 12, v.id); Put32(p + 16, v.revision); Put32(p + 20, n);
    Put32(p + 24, Crc32(p, 24)); Put32(p + 28, Crc32(body, n)); Put64(p + 32, v.token);
    std::memcpy(p + 40, v.digest, 32); Put32(p + 72, v.row); Put32(p + 76, v.rgb);
    std::memcpy(p + 80, v.baseline_config_sha, 32); Put16(p + 116, v.receipt_format); Put16(p + 118, v.receipt_format == 2 ? v.operation : 0);
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
    const bool create = v.operation == 15, erase = v.operation == 20;
    if ((!create && !LifecycleOperation(v.operation)) || v.rows > 30 || v.rgbs > 30 || v.count > 64 ||
        (create && (v.rows == 30 || v.count == 64 || v.high_id == UINT32_MAX)) ||
        (!create && (!v.rows || !v.count || !v.high_id)) || (v.with_rgb && v.rgbs == 30) || !v.generation || v.generation == UINT32_MAX || v.sequence == UINT32_MAX ||
        v.token <= v.high_token || !v.config_bytes || v.config_bytes > kConfigBodyMaxBytes ||
        (erase ? v.record_bytes != 0 : v.record_bytes <= kRecordHeaderBytes) || v.record_bytes > kRecordMaxBytes || v.namespace_files > 256 ||
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
