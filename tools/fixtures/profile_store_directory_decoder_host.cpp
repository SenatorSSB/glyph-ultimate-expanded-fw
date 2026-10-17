#include <cstdint>
#include <cstdio>
#include <cstring>

// The checker supplies this generated translation unit through its first include
// path. Keeping production code in the same translation unit makes the
// intentionally internal directory decoder directly testable without changing
// firmware linkage or visibility.
#include "ProfileStore.under_test.cpp"

namespace {
constexpr size_t kWireBytes = kDirectoryWireBytes;
constexpr size_t kTrailer = kWireBytes - 4;

uint32_t crc32(const uint8_t *data, size_t length) {
    uint32_t crc = 0xffffffffu;
    for (size_t i = 0; i < length; ++i) {
        crc ^= data[i];
        for (uint8_t bit = 0; bit < 8; ++bit) crc = (crc >> 1) ^ (0xedb88320u & (0u - (crc & 1u)));
    }
    return ~crc;
}
void put16(uint8_t *p, uint16_t value) { p[0] = value; p[1] = value >> 8; }
void put32(uint8_t *p, uint32_t value) { for (size_t i = 0; i < 4; ++i) p[i] = value >> (8 * i); }

void seal(uint8_t (&wire)[kWireBytes]) { put32(wire + kTrailer, crc32(wire, kTrailer)); }
void valid(uint8_t (&wire)[kWireBytes], uint16_t count = 1) {
    std::memset(wire, 0, sizeof(wire));
    put32(wire, 0x32534450u); put16(wire + 4, 2); put16(wire + 6, count);
    put32(wire + 8, 7); put32(wire + 12, 1); put32(wire + 16, count);
    for (uint16_t i = 0; i < count; ++i) {
        uint8_t *entry = wire + kRootHeader + i * kEntryBytes;
        put32(entry, i + 1); put32(entry + 4, 1); put32(entry + 16, i);
    }
    seal(wire);
}
bool decode(uint8_t (&wire)[kWireBytes]) {
    ProfileStore::Directory result{};
    return DIRECTORY_DECODE_UNDER_TEST(wire, sizeof(wire), &result);
}
bool check(const char *name, bool expected, uint8_t (&wire)[kWireBytes]) {
    const bool actual = decode(wire);
    if (actual == expected) return true;
    std::fprintf(stderr, "%s expected %d got %d\n", name, expected, actual);
    return false;
}
} // namespace

int main() {
    uint8_t wire[kWireBytes];
    bool ok = true;
    valid(wire); ok &= check("valid", true, wire);
    valid(wire, ProfileStore::kMaxEntries); ok &= check("max", true, wire);
    valid(wire); put32(wire, 0); seal(wire); ok &= check("bad_magic", false, wire);
    valid(wire); put16(wire + 4, 3); seal(wire); ok &= check("version", false, wire);
    valid(wire); put16(wire + 6, ProfileStore::kMaxEntries + 1); seal(wire); ok &= check("count", false, wire);
    valid(wire); wire[100] ^= 1; ok &= check("crc", false, wire);
    valid(wire); put32(wire + 12, 0); seal(wire); ok &= check("incarnation", false, wire);
    valid(wire); put16(wire + 6, 1); put32(wire + 16, 0); seal(wire); ok &= check("high_water", false, wire);
    valid(wire); put32(wire + kRootHeader, 0); seal(wire); ok &= check("zero_id", false, wire);
    valid(wire); put32(wire + kRootHeader + 4, 0); seal(wire); ok &= check("zero_revision", false, wire);
    valid(wire); put32(wire + kRootHeader, 2); seal(wire); ok &= check("id_above_high_water", false, wire);
    valid(wire, 2); put32(wire + kRootHeader + kEntryBytes, 1); seal(wire); ok &= check("duplicate_id", false, wire);
    valid(wire); put32(wire + kRootHeader + 8, 1); seal(wire); ok &= check("previous_not_older", false, wire);
    valid(wire); put32(wire + 20, 3); seal(wire); ok &= check("migration_state", false, wire);
    valid(wire); put32(wire + 84, 3); seal(wire); ok &= check("migration_count", false, wire);
    valid(wire); put32(wire + 64, static_cast<uint32_t>(ProfileStore::Status::Aborted)); seal(wire); ok &= check("aborted_transaction_status", true, wire);
    valid(wire); put32(wire + 64, static_cast<uint32_t>(ProfileStore::Status::Aborted) + 1); seal(wire); ok &= check("transaction_status", false, wire);
    valid(wire); std::memset(wire + kRootHeader + 20, 'N', 32); seal(wire); ok &= check("full_32_byte_name", true, wire);
    valid(wire); std::memset(wire + kRootHeader + 20, 'N', 33); seal(wire); ok &= check("unterminated_name", false, wire);
    // Explicit deployed reader: wire tags/stride stay v1, never reinterpreted.
    uint8_t legacy[kLegacyDirectoryBytes] = {};
    put32(legacy, 0x31534450u); put16(legacy + 4, 1); put16(legacy + 6, 1);
    put32(legacy + 8, 8); put32(legacy + 12, 41); put32(legacy + 16, 4);
    put32(legacy + 32, 3); put32(legacy + 36, 1);
    put32(legacy + sizeof(legacy) - 4, crc32(legacy, sizeof(legacy) - 4));
    ProfileStore::Directory deployed{};
    ok &= DecodeLegacy(legacy, sizeof(legacy), &deployed) && deployed.entries[0].id == 3 && deployed.high_water_id == 4;
    legacy[40] ^= 1;
    ok &= !DecodeLegacy(legacy, sizeof(legacy), &deployed);
    if (!ok) return 1;
    std::puts("profile_store_directory_decoder_semantics=PASS");
    return 0;
}
