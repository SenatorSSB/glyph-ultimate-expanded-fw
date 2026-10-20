#include "core/ProfileStore.hpp"
struct ProfileStore::Directory {
    uint32_t generation = 0, incarnation = 0, high_water_id = 0;
    uint32_t migration_state = 0, migration_version = 0, migration_count = 0;
    uint8_t migration_source[32]{}, migration_payloads[2][32]{}, migration_receipt[32]{},
        compact_digest[32]{};
    uint32_t migration_ids[2]{}, migration_revisions[2]{};
    TransactionIdentity last_identity{};
    TransactionResult last_result{};
    size_t count = 0;
    Entry entries[kMaxEntries]{};
};
extern "C" char directory_size[sizeof(ProfileStore::Directory)]; char directory_size[sizeof(ProfileStore::Directory)];
extern "C" char entry_size[sizeof(ProfileStore::Entry)]; char entry_size[sizeof(ProfileStore::Entry)];
