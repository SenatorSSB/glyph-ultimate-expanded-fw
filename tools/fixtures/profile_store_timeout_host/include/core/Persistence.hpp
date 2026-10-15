#pragma once

#include "host_stubs.hpp"
#include_next "core/config_validation.hpp"
#include <pb_encode.h>

// Functional host boundary: durable configuration and generation are independent
// of the live Config passed to the retained production Configurator backend.
class Persistence {
 public:
  enum class LoadResult { Loaded, Absent, Rejected, StorageFailure };
  enum class SaveResult { Saved, Conflict, StorageFailure, Uncertain };
  bool IsMutationFenced() const { return uncertain; }
  SaveResult ReconcileConfig(Config &config) { if(fail_load) return SaveResult::Uncertain; config=durable; uncertain=false; return SaveResult::Saved; }
  bool CheckSavedConfig() { return seeded; }
  size_t LoadConfigRaw(Print &, bool = true) { return 0; }
  bool ValidateConfig(const Config &config, ConfigValidationError &error) const {
    return !fail_validation && validate_config_semantics(config, error);
  }
  static uint32_t GenerationFor(const Config &config) {
    size_t size = 0;
    if (!pb_get_encoded_size(&size, Config_fields, &config)) return 0;
    std::vector<uint8_t> bytes(size);
    pb_ostream_t out = pb_ostream_from_buffer(bytes.data(), bytes.size());
    if (!pb_encode(&out, Config_fields, &config)) return 0;
    uint32_t crc = UINT32_MAX;
    for (uint8_t byte : bytes) {
      crc ^= byte;
      for (unsigned bit = 0; bit < 8; ++bit)
        crc = (crc >> 1) ^ (0xedb88320u & (0u - (crc & 1u)));
    }
    return ~crc;
  }
  void Seed(const Config &config) {
    durable = config;
    generation = GenerationFor(config);
    seeded = true;
  }
  LoadResult LoadConfigChecked(Config &config) {
    ++load_calls;
    if (fail_load) return LoadResult::StorageFailure;
    if (!seeded) return LoadResult::Absent;
    config = durable;
    if (advance_after_load) { ++generation; advance_after_load = false; }
    return LoadResult::Loaded;
  }
  bool LoadConfig(Config &config) { return LoadConfigChecked(config) == LoadResult::Loaded; }
  bool SaveConfig(Config &config) {
    ++save_calls;
    if (fail_save) return false;
    Seed(config);
    return true;
  }
  SaveResult SaveConfigIfGenerationMatches(Config &config, uint64_t expected) {
    if (advance_before_save) { ++generation; advance_before_save = false; }
    if (expected != generation) return SaveResult::Conflict;
    if (uncertain_after_save) {
      Seed(config); ++save_calls; uncertain = true; uncertain_after_save = false;
      return SaveResult::Uncertain;
    }
    return SaveConfig(config) ? SaveResult::Saved : SaveResult::StorageFailure;
  }
  uint32_t ConfigGeneration(const Config &) const { return generation; }
  Config durable = Config_init_default;
  uint32_t generation = 0;
  unsigned save_calls = 0, load_calls = 0;
  bool seeded = false, fail_save = false, fail_load = false;
  bool uncertain = false, uncertain_after_save = false;
  bool fail_validation = false, advance_after_load = false, advance_before_save = false;
};

extern Persistence persistence;
