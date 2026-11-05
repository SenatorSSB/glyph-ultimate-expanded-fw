#pragma once
#include "core/CheckedStorage.hpp"
#include <cstddef>
#include <cstdint>

// Borrowed byte views only. These functions check format/counter/arithmetic
// facts; they never confer admission, validate native gameplay, or write storage.
namespace package_storage {
constexpr size_t kRootPrefixBytes = 3904;
constexpr size_t kIntentBytes = 512;
constexpr size_t kRootBytes = 4420;
constexpr size_t kControlBytes = 4436;
constexpr size_t kRecordHeaderBytes = 128;
constexpr size_t kRecordMaxBytes = 3469;
constexpr size_t kConfigBodyMaxBytes = 8191;
struct RootView {
    const uint8_t *prefix; // exactly 3904 existing root-prefix owner bytes
    const uint8_t *intent; // exactly 512 exclusive initialization-owner bytes
    const uint8_t *trailer; // exactly four existing root-prefix trailer bytes
};
uint16_t Get16(const uint8_t *);
uint32_t Get32(const uint8_t *);
uint64_t Get64(const uint8_t *);
void Put16(uint8_t *, uint16_t);
void Put32(uint8_t *, uint32_t);
void Put64(uint8_t *, uint64_t);
uint32_t Crc32(const uint8_t *, size_t);
uint32_t RootCrc(const RootView &);
void HashRoot(const RootView &, uint8_t out[32]);
void EmptyIntent(uint8_t intent[kIntentBytes]);
bool IntentValid(const uint8_t intent[kIntentBytes]);
bool SourcePrefixValid(const uint8_t prefix[kRootPrefixBytes]);
bool RootValid(const RootView &);
bool ControlValid(const uint8_t header[16], const RootView &);
bool ControlPhaseValid(const uint8_t header[16], const uint8_t intent[kIntentBytes]);
void FinishRoot(uint8_t prefix[kRootPrefixBytes], const uint8_t intent[kIntentBytes], uint8_t trailer[4]);
void FinishControl(uint8_t header[16], const RootView &, uint32_t phase);
bool SameRoot(const RootView &, const RootView &);
bool SameImmutableIntent(const uint8_t *, const uint8_t *);
bool RootPairValid(const RootView &slot0, const RootView &slot1, unsigned &selected);

struct RecordIdentity {
    uint32_t incarnation, id, row, rgb, generation, sequence;
    uint64_t token;
    const uint8_t *digest; // 32 bytes
    const uint8_t *baseline_config_sha; // 32 bytes
};
bool RecordValid(const uint8_t *record, size_t bytes);
bool RecordMatchesIntent(const uint8_t *record, size_t bytes, const uint8_t intent[kIntentBytes]);
bool MakeRecordHeader(uint8_t header[kRecordHeaderBytes], const uint8_t *body,
                      size_t body_bytes, const RecordIdentity &);
bool RecordPath(char *out, size_t capacity, uint32_t id, uint32_t revision, bool temporary);

struct AdmissionArithmetic {
    uint64_t used, free, total, protected_bytes, token, high_token;
    uint32_t rows, rgbs, count, high_id, generation, sequence;
    uint32_t namespace_files, config_bytes, record_bytes;
    bool with_rgb;
};
// Arithmetic is NOT admission authority. Only exact namespace/classification/
// source-validator binding may populate these values and acquire write scope.
bool FileCharge(uint64_t bytes, uint64_t &charged);
bool AdmissionNeed(const AdmissionArithmetic &, uint64_t &needed);
bool ExactGeometry(const CheckedStorage::Geometry &);
}
