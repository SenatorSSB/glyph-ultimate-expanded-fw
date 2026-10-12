/* Persistent Ultimate profile store.  See the frozen multi-profile design. */
#ifndef _CORE_PROFILE_STORE_HPP
#define _CORE_PROFILE_STORE_HPP

#include <cstddef>
#include <cstdint>

#include <config.pb.h>

class ProfileStore {
  public:
    static constexpr uint8_t kCompactConfigFormat = 1;
    static constexpr size_t kMinimumAdmissionProfiles = 20;
    static constexpr size_t kMaxEntries = 64;
    static constexpr size_t kNameCapacity = 18;
    static_assert(kMaxEntries >= kMinimumAdmissionProfiles,
                  "the persistent store admission floor is twenty profiles");

    enum class Status : uint8_t {
        Ok, RecoveredPrevious, NotFound, Invalid, Conflict, Full, IoFailure, UnknownOutcome,
        MigrationRequired, MigrationFenced, ReadOnlyRecovery
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

    bool Begin();
    bool IsReady() const;
    bool IsReadOnlyRecovery() const;
    bool MigrationPending() const;
    uint32_t LegacyMigrationId(size_t legacy_index) const;
    uint32_t Incarnation() const;
    uint32_t Generation() const;
    size_t Count() const;
    const Entry *EntryAt(size_t index) const;
    const UltimateProfile *Activate(uint32_t id, Status *status = nullptr);
    const UltimateProfile *ActiveProfile() const;
    uint32_t ActiveId() const;
    TransactionResult Create(const UltimateProfile &profile, const char *name, uint32_t rank,
                             uint32_t token, uint32_t request_digest);
    TransactionResult Update(uint32_t id, const UltimateProfile &profile, uint32_t expected_revision,
                             uint32_t token, uint32_t request_digest);
    TransactionResult Rename(uint32_t id, const char *name, uint32_t expected_generation,
                             uint32_t token, uint32_t request_digest);
    TransactionResult Reorder(uint32_t id, uint32_t rank, uint32_t expected_generation,
                              uint32_t token, uint32_t request_digest);
    TransactionResult Delete(uint32_t id, uint32_t expected_generation, uint32_t referenced_id,
                             uint32_t token, uint32_t request_digest);
    TransactionResult QueryTransaction(uint32_t token, uint32_t request_digest) const;
    Status ImportLegacy(const Config &legacy, uint32_t *old_index_to_id, size_t mapping_capacity);
    Status CompleteMigration(const Config &compact);

  private:
    bool LoadDirectory();
    bool PublishDirectory(const Directory &next);
    bool ReadProfile(uint32_t id, uint32_t revision, UltimateProfile &into) const;
    bool WriteProfile(uint32_t id, uint32_t revision, const UltimateProfile &profile);
    bool ValidateProfile(const UltimateProfile &profile) const;
    int Find(uint32_t id) const;
    TransactionResult BeginMutation(uint32_t token, uint32_t digest) const;
    void Finish(TransactionResult *result, uint32_t id, uint32_t revision) const;

    Directory *_directory = nullptr;
    UltimateProfile _active_profile = UltimateProfile_init_default;
    UltimateProfile _candidate_profile = UltimateProfile_init_default;
    uint32_t _active_id = 0;
    bool _ready = false;
    bool _read_only_recovery = false;
};

extern ProfileStore profile_store;

#endif
