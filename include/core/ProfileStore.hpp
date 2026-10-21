/* Persistent Ultimate profile store.  See the frozen multi-profile design. */
#ifndef _CORE_PROFILE_STORE_HPP
#define _CORE_PROFILE_STORE_HPP

#include "core/ProfileStoreStorage.hpp"
#include "core/ProfileStoreTransaction.hpp"
#include "modes/UltimateNativeProfile.hpp"

#include <config.pb.h>
#include <cstddef>
#include <cstdint>

class ProfileStore {
  public:
    static constexpr uint8_t kCompactConfigFormat = 1;
    static constexpr size_t kMinimumAdmissionProfiles = 20;
    static constexpr size_t kMaxEntries = 64;
    static constexpr size_t kNameCapacity = 33;
    static_assert(
        kMaxEntries >= kMinimumAdmissionProfiles,
        "the persistent store admission floor is twenty profiles"
    );

    enum class Status : uint8_t {
        Ok,
        RecoveredPrevious,
        NotFound,
        Invalid,
        Conflict,
        Full,
        IoFailure,
        UnknownOutcome,
        MigrationRequired,
        MigrationFenced,
        ReadOnlyRecovery,
        Referenced,
        Aborted
    };

    struct Entry {
        uint32_t id = 0;
        uint32_t revision = 0;
        uint32_t previous_revision = 0;
        uint32_t payload_version = 0;
        uint32_t rank = 0;
        char name[kNameCapacity] = {};
    };

    struct TransactionResult {
        Status status = Status::NotFound;
        uint32_t id = 0;
        uint32_t revision = 0;
        uint32_t generation = 0;
    };

    // Internal in-RAM representation; its serialized form is explicitly
    // encoded in ProfileStore.cpp and never persisted as a native struct.
    struct Directory;

    explicit ProfileStore(ProfileStoreStorage *storage = nullptr);
    bool Begin(uint32_t expected_incarnation = 0, uint32_t required_root_format = 0);
    bool BeginRecovery(uint32_t expected_incarnation = 0, uint32_t required_root_format = 0);
    using TransactionIdentity = ProfileStoreTransactionIdentity;

    struct CapacityInfo {
        uint64_t total_bytes = 0, used_bytes = 0, free_bytes = 0, reserve_bytes = 16384,
                 protected_bytes = 0, staging_bytes = 0;
        uint32_t block_size = 0, page_size = 0, admissible_profiles = 0;
        bool mutation_feasible = false;
    };
    enum class RecordHealth : uint8_t {
        Healthy,
        RecoveredPrevious,
        Missing,
        Corrupt,
        Unsupported
    };

    enum HealthFlag : uint32_t {
        FilesystemUnavailable = 1,
        RootInvalid = 2,
        MigrationFencedFlag = 4,
        TransactionUncertain = 8,
        ReadOnlyFlag = 16,
        LegacyUpgradeRequired = 32
    };

    CapacityInfo Capacity() const;
    RecordHealth Health(uint32_t id) const;
    uint32_t HealthFlags() const;
    bool IsTransactionUncertain() const;
    bool ReconcileTransaction();
    Status CollectGarbage();

    bool IsReady() const;
    bool IsReadOnlyRecovery() const;
    bool MigrationPending() const;
    uint32_t LegacyMigrationId(size_t legacy_index) const;
    uint32_t Incarnation() const;
    uint32_t Generation() const;
    uint64_t LastTransactionToken() const;
    size_t Count() const;
    const Entry *EntryAt(size_t index) const;
    Status Read(uint32_t id, UltimateProfile &into, uint32_t *revision = nullptr) const;
    const UltimateProfile *Activate(uint32_t id, Status *status = nullptr);
    const UltimateProfile *ActiveProfile() const;
    const ultimate_native::PreparedView *ActiveNativeView() const { return _active_native.view.valid ? &_active_native.view : nullptr; }
    uint32_t ActiveId() const;
    uint32_t ActiveRevision() const { return _active_revision; }
    TransactionResult Create(
        const UltimateProfile &profile,
        const char *name,
        uint32_t rank,
        uint32_t token,
        uint32_t request_digest
    );
    TransactionResult Update(
        uint32_t id,
        const UltimateProfile &profile,
        uint32_t expected_revision,
        uint32_t token,
        uint32_t request_digest
    );
    TransactionResult Duplicate(
        uint32_t id,
        uint32_t expected_revision,
        const char *name,
        uint32_t rank,
        uint32_t token,
        uint32_t request_digest
    );
    TransactionResult Rename(
        uint32_t id,
        const char *name,
        uint32_t expected_generation,
        uint32_t token,
        uint32_t request_digest
    );
    TransactionResult Reorder(
        uint32_t id,
        uint32_t rank,
        uint32_t expected_generation,
        uint32_t token,
        uint32_t request_digest
    );
    TransactionResult Delete(
        uint32_t id,
        uint32_t expected_generation,
        uint32_t referenced_id,
        uint32_t token,
        uint32_t request_digest
    );
    TransactionResult QueryTransaction(uint32_t token, uint32_t request_digest) const;
    TransactionResult QueryTransaction(uint64_t token) const;
    TransactionResult QueryTransaction(const TransactionIdentity &identity) const;
    TransactionResult Create(
        const UltimateProfile &,
        const char *,
        uint32_t,
        const TransactionIdentity &
    );
    TransactionResult Update(
        uint32_t,
        const UltimateProfile &,
        uint32_t,
        const TransactionIdentity &
    );
    TransactionResult Duplicate(
        uint32_t,
        uint32_t,
        const char *,
        uint32_t,
        const TransactionIdentity &
    );
    TransactionResult Rename(uint32_t, const char *, uint32_t, const TransactionIdentity &);
    TransactionResult Reorder(uint32_t, uint32_t, uint32_t, const TransactionIdentity &);
    TransactionResult Delete(uint32_t, uint32_t, uint32_t, const TransactionIdentity &);
    using LegacyReader = bool (*)(void *, size_t, UltimateProfile &);
    Status ImportLegacyStream(
        const Config &,
        const uint8_t source_digest[32],
        LegacyReader,
        void *,
        uint32_t *,
        size_t
    );
    bool PrepareCompact(Config &compact) const;
    bool ValidateCompactReceipt(const Config &compact) const;
    Status ImportLegacy(const Config &legacy, uint32_t *old_index_to_id, size_t mapping_capacity);
    Status CompleteMigration(const Config &compact);
    void ResetDiagnostic();
    const char *LastDiagnostic() const;

  private:
    bool LoadDirectory();
    enum class BootstrapAction : uint8_t { Complete, Refused, Reconcile, Initialize, PublishAndInitialize };
    BootstrapAction PrepareBootstrap(bool recovery);
    bool ExecuteBootstrap(BootstrapAction action);
    bool ReadRoot(uint8_t slot, Directory &out) const;
    bool WriteControl(const Directory &, uint32_t phase);
    bool LoadControl(Directory &, uint32_t &phase) const;
    bool InitializeV2(const Directory &seed);
    bool Admit(size_t staged_record_bytes, size_t records = 1);
    bool EvaluateAdmission(size_t staged_record_bytes, size_t records);
    bool Protected(uint32_t id, uint32_t revision) const;
    bool LoadProtectedRoot() const;
    TransactionResult Start(const TransactionIdentity &) const;
    TransactionResult Commit(
        Directory &,
        uint32_t id,
        uint32_t revision,
        const TransactionIdentity &
    );
    bool _recovery_only = false;
    bool _uncertain = false;
    bool _v2 = false;
    bool _root_invalid = false;
    uint32_t _expected_incarnation = 0;
    uint32_t _required_root_format = 0;
    mutable bool _protected_ready = false;
    Directory *_next = nullptr;
    Directory *_other = nullptr;

    bool PublishDirectory(const Directory &next);
    bool ReadProfile(
        uint32_t id,
        uint32_t revision,
        UltimateProfile &into,
        bool *unsupported = nullptr
    ) const;
    TransactionResult FinalizePreparedCreate();
    void PrepareCreate();
    TransactionResult PrepareDuplicate(uint32_t id, uint32_t rev, const TransactionIdentity &t);
    bool PublishPreparedProfile();
    bool PrepareProfileWrite(uint32_t id, uint32_t revision, const UltimateProfile &profile);
    bool ValidateProfile(const UltimateProfile &profile) const;
    int Find(uint32_t id) const;
    TransactionResult BeginMutation(uint32_t token, uint32_t digest) const;
    void Finish(TransactionResult *result, uint32_t id, uint32_t revision) const;

    Directory *_directory = nullptr;
    UltimateProfile _active_profile = UltimateProfile_init_default;
    UltimateProfile _candidate_profile = UltimateProfile_init_default;
    ultimate_native::OwnedProgram _active_native;
    ultimate_native::PayloadLease _active_native_lease;
    uint32_t _native_generation = 0;
    uint32_t _active_id = 0;
    uint32_t _active_revision = 0;
    bool _ready = false;
    bool _read_only_recovery = false;
    ProfileStoreStorage *_storage = nullptr;
    ProfileStoreIoStage _last_io_stage = ProfileStoreIoStage::None;
};

extern ProfileStore profile_store;

#endif
