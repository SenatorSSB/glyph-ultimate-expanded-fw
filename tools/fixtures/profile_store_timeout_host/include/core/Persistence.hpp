#pragma once
#pragma once

#include "host_stubs.hpp"
#include_next "core/config_validation.hpp"

class Persistence {
 public:
  bool CheckSavedConfig() { return true; }
  size_t LoadConfigRaw(Print &, bool = true) { return 0; }
  bool ValidateConfig(const Config &, ConfigValidationError &) const { return true; }
  bool SaveConfig(Config &) { ++save_calls; return true; }
  uint32_t ConfigGeneration(const Config &) const { return 17; }
  unsigned save_calls = 0;
};

extern Persistence persistence;
