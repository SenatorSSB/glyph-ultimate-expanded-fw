#pragma once
#include "core/PackageStorageFormat.hpp"
#include "core/Sha256.hpp"

namespace package_storage {
enum class Probe : uint8_t { Present, Absent, Error };
enum class Floor : uint8_t { Unresolved, Unsupported, NoManaged, Supported };
enum class Logical : uint8_t { Unresolved, None, ProvenAborted, Incomplete, Committed };
struct ConfigFacts {
    uint32_t body_bytes = 0, crc = 0, rows = 0, rgbs = 0, store_format = 0, incarnation = 0,
        root_format = 0, managed_format = 0, sequence = 0, embedded_profiles = 0,
        reference_id = 0, reference_generation = 0, reference_row = 0;
    uint64_t reference_token = 0;
    uint8_t sha[32]{}, reference_digest[32]{}, migration_receipt[32]{};
    bool any_row_marker = false, newer_row_marker = false, source_valid = false, reference_digest_valid = false;
};
struct RowFacts {
    uint32_t mode = 0, id = 0, engine = 0, marker = 0, rgb = 0, legacy = 0,
        custom = 0, keyboard = 0;
    uint8_t sha[32]{};
};
struct NamespaceObject { char path[34]{}; size_t bytes = 0; bool directory = false; };

// Required production adapter. Each method is synchronous, read-only, and ends
// its entire I/O/codec frame before returning. No legacy fallback/reconciliation.
// Every Config/Row/RGB hash is exact deterministic SOURCE canonical protobuf.
// ConfigFacts::source_valid must be actual configured source semantic-validator
// output; wrapper/canonical validity alone is insufficient. Row/Rgb/Native bind
// to the exact path and index; they may not use stale active/default Config.
struct IntentFacts;
class NamespaceReader {
  public:
    virtual ~NamespaceReader() = default;
    // Exclusive, read-only interval. Reusable observations must expire before
    // returning to dispatch, which can run callbacks or start a transaction.
    virtual void BeginClassification() {}
    virtual void EndClassification() {}
    virtual bool MountedAndConfigured() const = 0;
    // Sticky for this entire observation, including every reread after Scan.
    // Canonical invalidity/source_valid=false is separate from checked I/O.
    virtual bool ObservationFailed() const = 0;
    // Enumerates complete same-mount namespace without opening files inside
    // the enumeration callback. eof=true is positive end, never I/O failure.
    virtual bool ObjectAt(size_t index, NamespaceObject &, bool &eof) = 0;
    virtual Probe Extent(const char *path, size_t &bytes) = 0;
    virtual bool Read(const char *path, size_t offset, uint8_t *out, size_t bytes) = 0;
    // Enforces exact8-byte wrapper/body CRC, canonical roundtrip and maximum.
    virtual bool Config(const char *path, uint32_t maximum, ConfigFacts &) = 0;
    // Exact supported historical /config.bin only. Boolean recognition grants
    // no Config facts/ownership; adapters without proof must reject.
    virtual bool HistoricalRetainedConfig() { return false; }
    virtual bool Row(const char *config_path, size_t index, RowFacts &) = 0;
    virtual bool Rgb(const char *config_path, size_t index, uint8_t sha[32]) = 0;
    // Source Prepare/ContextMatches + exact row/RGB semantic predicates.
    virtual bool Native(const char *config_path, size_t row, const uint8_t *record, size_t bytes) = 0;
    virtual bool LegacyProfile(const uint8_t *body, size_t bytes) = 0;
    // Exact append-only preceding rows/RGB and unrelated fields/presence/order.
    virtual bool AppendConfig(const char *baseline, const char *current) = 0;
    // Verify bounded edits against both canonical Config files. Non-production
    // adapters must implement the same proof before admitting lifecycle records.
    virtual bool LifecycleConfig(const char *, const char *, const IntentFacts &) { return false; }
};
struct IntentFacts {
    uint32_t operation = 0, phase = 0, terminal = 0, flags = 0, incarnation = 0, id = 0,
        revision = 0, baseline_generation = 0, generation = 0, sequence = 0,
        baseline_crc = 0, final_crc = 0, row = 0, rgb = 0, record_bytes = 0,
        config_bytes = 0, baseline_sequence = 0, baseline_rows = 0, final_rows = 0,
        baseline_rgbs = 0, final_rgbs = 0, baseline_high_id = 0;
    uint32_t old_revision = 0, old_row = 0, old_rgb = 0;
    uint64_t token = 0, baseline_token = 0;
    uint8_t digest[32]{}, baseline_config[32]{}, final_config[32]{}, record[32]{},
        row_sha[32]{}, rgb_sha[32]{}, baseline_root[32]{}, aggregate[32]{}, receipt[32]{}, immutable[32]{};
};
struct RootFacts {
    uint8_t *prefix = nullptr;
    uint32_t format = 0, control_phase = 0;
    uint8_t sha[32]{};
    IntentFacts intent{};
    bool present = false;
};
struct Classification {
    Floor floor = Floor::Unresolved;
    Logical logical = Logical::Unresolved;
    bool write_fenced = true;
    uint32_t incarnation = 0, generation = 0, package_sequence = 0;
    uint64_t high_token = 0;
    const char *diagnostic = "unclassified";
};
// Place this object IN existing publication_readback4128 after exclusive lease.
// It may not coexist there with any publication readback or READ owner.
struct ClassificationWorkspace {
    Classification classification{};
    RootFacts roots[3]{};
    ConfigFacts current{}, prior{}, scan_config{};
    NamespaceObject object{};
    RowFacts row{}, other_row{};
    Sha256 hash{}, aggregate_hash{};
    uint8_t digest[32]{}, row_sha[32]{}, rgb_sha[32]{}, record_sha[32]{}, entry_sha[32]{};
    uint8_t read_chunk[256]{};
    struct OwnedScratch {
        uint8_t word[16]{};
        size_t managed_count=0, mapped=0, item=0, i=0, j=0, n=0;
        uint32_t previous_id=0, id=0, sequence=0, extra_id=0;
        uint64_t token=0;
        const RootFacts *root=nullptr;
        const ConfigFacts *config=nullptr;
        const char *config_path=nullptr;
        const uint8_t *e=nullptr;
        bool all_extra=false;
    } owned{};
    struct RunScratch { unsigned next_phase=0; const RootFacts *selected=nullptr; unsigned v2=0; bool baseline_root_found=false, baseline_selected=false, store_published=false, baseline_current=false, baseline_prior=false; } run{};
    uint8_t old_record_sha[32]{}, old_wrapper_sha[32]{};
    uint64_t logical_bytes = 0;
    size_t namespace_files = 0;
    bool managed_observed = false, unsupported = false, corrupt = false;
};
static_assert(sizeof(ClassificationWorkspace) <= 4128, "classification borrows existing publication readback");
struct ClassifierOwners {
    ClassificationWorkspace &work;
    uint8_t *root0; // existing3908 root owner
    uint8_t *root1; // existing3908 root owner
    uint8_t *control; // existing3924 control owner (16 header +3908)
    uint8_t *intent; // exclusive512 alias of initialization owner
    uint8_t *record; // existing prepared_record4128, no native READ lease live
};
// Every failure remains fenced and reports unavailablezero checked facts.
// No method on NamespaceReader can write; this classifier never acquires grant.
void ClassifyNamespaceInto(NamespaceReader &, const ClassifierOwners &);
Classification ClassifyNamespace(NamespaceReader &, const ClassifierOwners &);
}
