#pragma once
class ProfileStore {
 public:
  static constexpr unsigned kCompactConfigFormat = 1;
  enum class Status { Ok, RecoveredPrevious, Invalid };
  const UltimateProfile *Activate(uint32_t id, Status *status) { ++activations; active=id; *status=Status::Ok; return nullptr; }
  unsigned activations=0; uint32_t active=0;
};
extern ProfileStore profile_store;
