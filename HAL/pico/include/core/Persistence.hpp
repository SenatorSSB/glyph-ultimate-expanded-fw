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
    LoadResult LoadConfigChecked(Config &config);

    bool SaveConfig(Config &config);
    bool LoadConfig(Config &config);
    bool CheckSavedConfig();
    size_t LoadConfigRaw(Print &out, bool validate = true);

    static constexpr size_t config_offset = sizeof(ConfigHeader);

  private:
    static constexpr char config_filename[] = "config.bin";

    bool _configuration_ok = false;
    bool _mounted = false;
    ConfigSemanticValidator _validator = nullptr;

    bool CheckSavedConfig(File &config_file, LoadResult *failure = nullptr);
};

extern Persistence persistence;

#endif