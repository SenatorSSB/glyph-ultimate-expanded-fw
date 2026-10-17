// Non-Pico targets retain the existing source-owned/null Ultimate fallback.
// Persistent profile storage is intentionally a Pico/LittleFS implementation.
#if !defined(ARDUINO_ARCH_RP2040)
#include "core/ProfileStore.hpp"

ProfileStore::ProfileStore(ProfileStoreStorage *) {}
bool ProfileStore::Begin() { return true; }
bool ProfileStore::IsReady() const { return true; }
bool ProfileStore::IsReadOnlyRecovery() const { return false; }
bool ProfileStore::MigrationPending() const { return false; }
uint32_t ProfileStore::LegacyMigrationId(size_t) const { return 0; }
uint32_t ProfileStore::Incarnation() const { return 0; }
uint32_t ProfileStore::Generation() const { return 0; }
size_t ProfileStore::Count() const { return 0; }
const ProfileStore::Entry *ProfileStore::EntryAt(size_t) const { return nullptr; }
ProfileStore::Status ProfileStore::Read(uint32_t, UltimateProfile &, uint32_t *) const { return Status::NotFound; }
const UltimateProfile *ProfileStore::Activate(uint32_t, Status *status) { if (status) *status = Status::NotFound; return nullptr; }
const UltimateProfile *ProfileStore::ActiveProfile() const { return nullptr; }
uint32_t ProfileStore::ActiveId() const { return 0; }
ProfileStore::TransactionResult ProfileStore::Create(const UltimateProfile &, const char *, uint32_t, uint32_t, uint32_t) { return {Status::IoFailure}; }
ProfileStore::TransactionResult ProfileStore::Update(uint32_t, const UltimateProfile &, uint32_t, uint32_t, uint32_t) { return {Status::IoFailure}; }
ProfileStore::TransactionResult ProfileStore::Duplicate(uint32_t, uint32_t, const char *, uint32_t, uint32_t, uint32_t) { return {Status::IoFailure}; }
ProfileStore::TransactionResult ProfileStore::Rename(uint32_t, const char *, uint32_t, uint32_t, uint32_t) { return {Status::IoFailure}; }
ProfileStore::TransactionResult ProfileStore::Reorder(uint32_t, uint32_t, uint32_t, uint32_t, uint32_t) { return {Status::IoFailure}; }
ProfileStore::TransactionResult ProfileStore::Delete(uint32_t, uint32_t, uint32_t, uint32_t, uint32_t) { return {Status::IoFailure}; }
ProfileStore::TransactionResult ProfileStore::QueryTransaction(uint32_t, uint32_t) const { return {Status::NotFound}; }
ProfileStore::Status ProfileStore::ImportLegacy(const Config &, uint32_t *, size_t) { return Status::IoFailure; }
ProfileStore::Status ProfileStore::CompleteMigration(const Config &) { return Status::IoFailure; }
void ProfileStore::ResetDiagnostic() {}
const char *ProfileStore::LastDiagnostic() const { return ""; }
ProfileStore profile_store;
#endif
