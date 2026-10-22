#pragma once

#include <config.pb.h>
#include <cstddef>
#include <cstdint>

// Schema 5 is a fixed, finite raw-coordinate program. These are wire limits,
// independent of C++ enum ABI, and do not change ProfileStore admission limits.
namespace ultimate_native {
constexpr uint8_t kSchema = 5;
constexpr uint16_t kEncoding = 1, kEngineAbi = 1;
constexpr size_t kBodyMax = 3336, kProfileMax = 3341, kRecordMax = 3373;
constexpr uint16_t kTrue = 0xffff;

struct OwnedProgram;
struct PreparedView {
    const uint8_t *body = nullptr;
    uint32_t generation = 0;
    uint16_t body_length = 0;
    uint16_t condition_token_offsets[96] = {};
    uint8_t all_counts[96] = {}, any_counts[96] = {}, none_counts[96] = {};
    uint16_t table_offset = 96, source_offset = 0, rule_offset = 0,
             binding_offset = 0, effect_offset = 0, mask_offset = 0;
    uint16_t mode_gate = 0, ls_digital_gate = 0, rs_digital_gate = 0, dpad_gate = 0;
    uint8_t condition_count = 0, early_condition_count = 0, source_count = 0,
            rule_count = 0, binding_count = 0, effect_count = 0;
    uint8_t default_table = 0, ls_source = 0, rs_source = 0, dpad_flags = 0;
    uint16_t engine_abi = 0;
    uint8_t body_digest[32] = {};
    bool valid = false;
    bool published = false;
    const OwnedProgram *owner = nullptr;
};
struct OwnedProgram { uint8_t body[kBodyMax] = {}; PreparedView view; };
struct CandidateWorkspace { OwnedProgram program; uint32_t error_offset = 0; uint8_t error_code = 0; };

// A synchronous lease is valid only while its source buffer is immutable.
// It is explicitly released before the source is reused. Encoding a released
// lease fails; copying a protobuf wrapper never extends the lease lifetime.
struct PayloadLease {
    const uint8_t *bytes = nullptr;
    size_t size = 0;
    bool live = false;
    void Release() { bytes = nullptr; size = 0; live = false; }
};
uint16_t Read16(const uint8_t *p);
bool Prepare(const uint8_t *body, size_t size, uint32_t generation, PreparedView &view);
bool CopyProgram(const PreparedView &source, OwnedProgram &destination, uint32_t generation, bool publish = false);
bool ContextDigest(const GameModeConfig &config, uint8_t digest[32]);
bool IsOwnedView(const PreparedView &);
bool ContextMatches(const PreparedView &, const GameModeConfig &);
bool ValidProfile(const UltimateProfile &);
const PreparedView &CandidateView();
bool PreserveProfile(UltimateProfile &);
const PayloadLease *Lease(const UltimateProfile &);
void Bind(UltimateProfile &, PayloadLease &);
bool BindOwned(UltimateProfile &, const OwnedProgram &, PayloadLease &);
// Presence scanning is independent of Nanopb callback internals. Native bytes
// are admitted only in standalone profiles, never embedded Config profiles.
bool DecodeProfile(const uint8_t *, size_t, UltimateProfile &, PayloadLease &);
bool PrepareRequest(const uint8_t *, size_t, ProfileStoreRequest &, PayloadLease &);
void RejectEmbedded(Config &);
void ClearEmbeddedCallbacks(Config &);
bool RejectPayload(pb_istream_t *, const pb_field_t *, void **);
} // namespace ultimate_native
