#pragma once

#include <cstddef>
#include <cstdint>

// Phase 7A compiled scaffold only.
// Not runtime-active; no storage; no device write; no WebSerial; no flashing automation.
// This parser validates the offline GCFG-like candidate shape without mutating
// RuntimeConfigView, reading storage, writing storage, or changing controller outputs.

namespace UltimateRuntimeConfigParser {

constexpr uint8_t kGcfgMagic0 = 'G';
constexpr uint8_t kGcfgMagic1 = 'C';
constexpr uint8_t kGcfgMagic2 = 'F';
constexpr uint8_t kGcfgMagic3 = 'G';
constexpr uint8_t kGcfgFormatVersion = 1;
constexpr uint32_t kModeUltimateCrc32 = 0x981d6fd6u;
constexpr size_t kRuntimeConfigTableCount = 27;
constexpr size_t kRuntimeConfigPointCount = 9;
constexpr size_t kHeaderSize = 13;
constexpr size_t kChecksumSize = 4;
constexpr size_t kOrderSize = kRuntimeConfigTableCount;
constexpr size_t kPointPayloadSize = kRuntimeConfigTableCount * kRuntimeConfigPointCount * 2;
constexpr size_t kPayloadSize = kHeaderSize + kOrderSize + kPointPayloadSize + kChecksumSize;

enum class ParseStatus : uint8_t {
    Ok,
    NullPayload,
    TruncatedPayload,
    WrongMagic,
    WrongVersion,
    WrongMode,
    WrongTableCount,
    WrongPointCount,
    WrongOrderLength,
    DuplicateTableId,
    UnknownTableId,
    WrongPayloadLength,
    WrongChecksum,
};

struct ParseResult {
    ParseStatus status;
    size_t table_count;
    size_t point_count_per_table;
};

constexpr uint32_t ReadLe32(const uint8_t *payload, size_t offset) {
    return static_cast<uint32_t>(payload[offset])
        | (static_cast<uint32_t>(payload[offset + 1]) << 8)
        | (static_cast<uint32_t>(payload[offset + 2]) << 16)
        | (static_cast<uint32_t>(payload[offset + 3]) << 24);
}

inline uint32_t Crc32(const uint8_t *payload, size_t length) {
    uint32_t crc = 0xffffffffu;
    for (size_t index = 0; index < length; ++index) {
        crc ^= payload[index];
        for (uint8_t bit = 0; bit < 8; ++bit) {
            const uint32_t mask = 0u - (crc & 1u);
            crc = (crc >> 1) ^ (0xedb88320u & mask);
        }
    }
    return ~crc;
}

inline ParseResult ParseUltimateRuntimeConfigPayload(const uint8_t *payload, size_t length) {
    if (payload == nullptr) {
        return {ParseStatus::NullPayload, 0, 0};
    }
    if (length < kHeaderSize + kChecksumSize) {
        return {ParseStatus::TruncatedPayload, 0, 0};
    }
    if (length != kPayloadSize) {
        return {ParseStatus::WrongPayloadLength, 0, 0};
    }
    if (
        payload[0] != kGcfgMagic0 ||
        payload[1] != kGcfgMagic1 ||
        payload[2] != kGcfgMagic2 ||
        payload[3] != kGcfgMagic3
    ) {
        return {ParseStatus::WrongMagic, 0, 0};
    }
    if (payload[4] != kGcfgFormatVersion) {
        return {ParseStatus::WrongVersion, 0, 0};
    }
    if (ReadLe32(payload, 5) != kModeUltimateCrc32) {
        return {ParseStatus::WrongMode, 0, 0};
    }
    const uint8_t table_count = payload[9];
    const uint8_t point_count = payload[10];
    const uint8_t order_count = payload[12];
    if (table_count != kRuntimeConfigTableCount) {
        return {ParseStatus::WrongTableCount, table_count, point_count};
    }
    if (point_count != kRuntimeConfigPointCount) {
        return {ParseStatus::WrongPointCount, table_count, point_count};
    }
    if (order_count != table_count) {
        return {ParseStatus::WrongOrderLength, table_count, point_count};
    }

    bool seen[kRuntimeConfigTableCount] = {};
    for (size_t index = 0; index < kRuntimeConfigTableCount; ++index) {
        const uint8_t table_id = payload[kHeaderSize + index];
        if (table_id >= kRuntimeConfigTableCount) {
            return {ParseStatus::UnknownTableId, table_count, point_count};
        }
        if (seen[table_id]) {
            return {ParseStatus::DuplicateTableId, table_count, point_count};
        }
        seen[table_id] = true;
    }

    const uint32_t expected_crc = ReadLe32(payload, length - kChecksumSize);
    const uint32_t actual_crc = Crc32(payload, length - kChecksumSize);
    if (actual_crc != expected_crc) {
        return {ParseStatus::WrongChecksum, table_count, point_count};
    }
    return {ParseStatus::Ok, table_count, point_count};
}

}  // namespace UltimateRuntimeConfigParser
