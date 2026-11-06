#pragma once
#if defined(GLYPH_PACKAGE_V1) && GLYPH_PACKAGE_V1
#include "core/PackageNamespaceClassifier.hpp"
#include "modes/UltimateNativeProfile.hpp"
#include "core/Persistence.hpp"
class ProfileStore;
class Persistence;

// One synchronous core0 classifier invocation. The caller owns all source
// workspace leases and excludes IRQ/core1/storage reentry. This object owns no
// Config/profile/native image, file, heap allocation or persistent authority.
class GlyphPackageSourceReader final : public package_storage::NamespaceReader {
 public:
    // Legacy third argument is ignored for source compatibility. The streamed
    // append proof never borrows or overwrites ConfigWriteCandidate.
    GlyphPackageSourceReader(ProfileStore &, Persistence &, bool = true);
    ~GlyphPackageSourceReader() override;
    bool MountedAndConfigured() const override;
    bool ObservationFailed() const override;
    bool ObjectAt(size_t, package_storage::NamespaceObject &, bool &eof) override;
    package_storage::Probe Extent(const char *, size_t &) override;
    bool Read(const char *, size_t, uint8_t *, size_t) override;
    bool Config(const char *, uint32_t, package_storage::ConfigFacts &) override;
    bool Row(const char *, size_t, package_storage::RowFacts &) override;
    bool Rgb(const char *, size_t, uint8_t[32]) override;
    bool Native(const char *, size_t, const uint8_t *, size_t) override;
    bool LegacyProfile(const uint8_t *, size_t) override;
    bool AppendConfig(const char *, const char *) override;
    // Internal candidate only; exact canonical hash/CRC/extent plus configured
    // source predicate. Does not load or overwrite either Config workspace.
    bool DescribeConfig(const ::Config &, package_storage::ConfigFacts &);
 private:
    bool LoadNamedConfig(const char *, uint32_t, uint8_t *sha = nullptr,
                         uint32_t *crc = nullptr, uint32_t *bytes = nullptr,
                         bool *source_valid = nullptr);
    bool ValidateCandidateProfile();
    bool CanonicalCandidateProfile(const uint8_t *, size_t);
    void ClearProfileLease();
    bool ValidateMaterializedNative();
    Persistence::PackageConfigFacts _config_facts{};
    Persistence::PackageConfigFile _config_file{};
    bool _config_valid = false;
    struct ConfigOutputs {
        uint8_t *sha = nullptr;
        uint32_t *crc = nullptr, *bytes = nullptr;
        bool *source_valid = nullptr;
        uint32_t maximum = 0;
    } _config_outputs{};
    const uint8_t *_native_record = nullptr;
    size_t _native_bytes = 0, _native_index = 0;
    ProfileStore &_store;
    Persistence &_persistence;
    ultimate_native::PayloadLease _profile_lease{};
    bool _failed = false;
};
#endif
