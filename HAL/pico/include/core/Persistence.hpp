/*
 * This file is part of HayBox
 * Copyright (C) 2024 Jonathan Haylett
 *
 * HayBox is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License version 3 as
 * published by the Free Software Foundation.
 *
 * This software is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this software. If not, see <http://www.gnu.org/licenses/>.
 */

#ifndef _CORE_PERSISTENCE_HPP
#define _CORE_PERSISTENCE_HPP

#include <LittleFS.h>
#include <config.pb.h>
#include "core/config_validation.hpp"

class Persistence {
  public:
    typedef struct _ConfigHeader {
        size_t config_size = 0;
        uint32_t config_crc = 0;
    } ConfigHeader;

    Persistence();
    ~Persistence();

    enum class LoadResult { Loaded, Absent, Rejected, StorageFailure };

    bool SetValidator(ConfigSemanticValidator validator);
    bool ValidateConfig(const Config &config, ConfigValidationError &error) const;
    bool IsAvailable() const;
    // Deterministic generation for compare-and-set callers. It is the checked
    // persisted protobuf body CRC, not a new on-disk schema field.
    uint32_t ConfigGeneration(const Config &config) const;
    LoadResult LoadConfigChecked(Config &config);

    enum class SaveResult { Saved, Conflict, StorageFailure };
    // Synchronous core0 compare-and-save. Checks both the loaded generation
    // and freshly verified durable bytes before touching any staged file.
    SaveResult SaveConfigIfGenerationMatches(Config &config, uint64_t expected_generation);

    bool SaveConfig(Config &config);
    bool LoadConfig(Config &config);
    bool CheckSavedConfig();
    size_t LoadConfigRaw(Print &out, bool validate = true);

    static constexpr size_t config_offset = sizeof(ConfigHeader);

  private:
    // config.bin is immutable migration input once a compact Config exists.
    // New writes use a separate name so an interrupted migration cannot erase
    // the only legacy source record.
    static constexpr char config_filename[] = "config-v2.bin";
    static constexpr char prior_compact_filename[] = "config-v2.prev";
    static constexpr char legacy_config_filename[] = "config.bin";

    bool _configuration_ok = false;
    bool _mounted = false;
    uint32_t _config_generation = 0;
    ConfigSemanticValidator _validator = nullptr;

    bool CheckSavedConfig(File &config_file, LoadResult *failure = nullptr);
};

extern Persistence persistence;

#endif
