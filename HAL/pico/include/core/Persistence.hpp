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
#include "core/CheckedStorageFile.hpp"
#include "core/PackageStorageFence.hpp"
#include <config.pb.h>
#include "core/config_validation.hpp"

class Persistence {
  public:
    typedef struct _ConfigHeader {
        uint32_t config_size = 0;
        uint32_t config_crc = 0;
    } ConfigHeader;

    static_assert(sizeof(ConfigHeader) == 8, "Config file header is two LE32 words");
    enum class PackageConfigFile : uint8_t {
        Current, Prior, Staged, Legacy, MigrationSource, MigrationTemporary
    };
    struct PackageConfigFacts {
        uint8_t sha[32]{};
        uint32_t crc = 0;
        uint32_t bytes = 0;
    };

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

    enum class SaveResult { Saved, Conflict, StorageFailure, Uncertain, UnknownOutcome = Uncertain };
    // Read-only exact named observations. No fallback, restoration, migration,
    // reconciliation, callback retention, or persistent writer acquisition.
    Config &PackageConfigScratch(); // borrowed loaded_candidate, classifier lease only
    LoadResult ObservePackageConfig(PackageConfigFile, Config &, PackageConfigFacts &, bool &source_valid,
                                   size_t maximum = 0);
    bool PreparePackageConfig(Config &, const PackageConfigFacts &baseline,
                                   const PackageConfigFacts &expected,
                                   const void *package_owner, uint64_t token);
    SaveResult PublishPreparedPackageConfig();

    bool IsMutationFenced() const { return _mutation_fenced || PackageStorageFence::MutationFenced(); }
    SaveResult ReconcileConfig(Config &authoritative);
    // Synchronous core0 compare-and-save. Checks both the loaded generation
    // and freshly verified durable bytes before touching any staged file.
    SaveResult SaveConfigIfGenerationMatches(Config &config, uint64_t expected_generation);

    // Exact raw persisted migration source, copied with bounded scratch and
    // never replaced on retry. Paths remain independent of Config rotation.
    bool CaptureLegacySource(uint8_t digest[32]);
    bool LegacySourceIdentity(uint8_t digest[32]);
    LoadResult ReadLegacyProfile(size_t index, UltimateProfile &profile);

    bool SaveConfig(Config &config);
    bool LoadConfig(Config &config);
    bool CheckSavedConfig();
    size_t LoadConfigRaw(Print &out, bool validate = true);

    static constexpr size_t config_offset = sizeof(ConfigHeader);

  private:
    static const char *PackageFilename(PackageConfigFile);
    LoadResult ReadPackageFacts(const char *, size_t maximum, PackageConfigFacts &);
    bool ValidateObservedPackageConfig(const Config &) const;
    LoadResult PrepareObservedPackageConfig();
    LoadResult InitializeObservedPackageConfig();
    void DecodeObservedPackageConfig();
    LoadResult FinishObservedPackageConfig();
    bool MatchPackageConfig(const char *, const PackageConfigFacts &);
    static bool PublishPackageStaged();
    static bool RotatePackagePrior();
    static bool VerifyPackagePrior();
    static bool RotatePackageFinal();
    static bool PreparePackageSave();
    static bool VerifyPackageSave();
    static bool VerifyPackageBaseline();
    static bool VerifyPackagePublished();
    static SaveResult FinishPackageSave(bool);
    // config.bin is immutable migration input once a compact Config exists.
    // New writes use a separate name so an interrupted migration cannot erase
    // the only legacy source record.
    static constexpr char config_filename[] = "config-v2.bin";
    static constexpr char prior_compact_filename[] = "config-v2.prev";
    static constexpr char legacy_config_filename[] = "config.bin";

    bool _configuration_ok = false;
    bool _mounted = false;
    bool _mutation_fenced = false;
    uint32_t _pending_crc = 0;
    size_t _pending_size = 0;
    uint32_t _config_generation = 0;
    ConfigSemanticValidator _validator = nullptr;

    enum class CaptureAction : uint8_t { Refused, ExistingExact, NeedsCopy };
    bool ValidateLegacySource();
    bool CheckCaptureInput();
    bool AdmitCaptureSource();
    CaptureAction PrepareCaptureSource(uint8_t digest[32]);
    bool ExecuteCaptureSource(uint8_t digest[32]);
    bool RemoveCaptureTemporary();
    bool CopyCapturedSource();
    bool VerifyPublishCapturedSource(uint8_t digest[32]);
    const char *SelectReadConfigCandidate();
    LoadResult InitializeReadConfigCandidate(CheckedStorageFile &);
    LoadResult FinishConfigDecode(CheckedStorageFile &,bool);
    static bool InitializeStagedConfig();
    static bool FailStagedConfig();
    LoadResult ReadConfigCandidate();
    LoadResult LoadConfigDriver(Config &);
    LoadResult CompleteReadConfigCandidate(CheckedStorageFile &);
    LoadResult FinishLoadedConfig(Config &);
    static bool EncodeStagedConfig();
    static void InitializeStagedStream();
    static void EndStagedStream();
    static bool FinishSaveConfig(bool);
    static void InitializeSaveContext(Persistence *,Config *);
    static bool InitializeOrdinarySaveContext(Persistence *,Config *);
    static bool PositionStagedConfig();
    static bool CompleteStagedConfig();
    SaveResult VerifyExpectedConfigGeneration(uint64_t expected_generation);
    bool PrepareSaveConfig(const Config &config);
    bool RemoveSaveTemporary();
    static bool StageSaveConfig();
    bool VerifyStagedConfig(Config &config);
    bool RotateSavedConfig();
    bool PublishStagedConfig(Config &config);
    bool CheckSavedConfig(CheckedStorageFile &config_file, LoadResult *failure = nullptr);
};

extern Persistence persistence;

#endif
