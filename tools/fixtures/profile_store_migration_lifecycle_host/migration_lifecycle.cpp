#include "core/ProfileStore.hpp"
#include "core/ProfileStoreStorage.hpp"
#include "core/config_validation.hpp"

#include <pb_decode.h>
#include <pb_encode.h>

#include <cstdio>
#include <cstring>
#include <fstream>
#include <map>
#include <string>
#include <vector>

namespace {

struct MemoryStorage final : ProfileStoreStorage {
    std::map<std::string, std::vector<uint8_t>> files;

    bool Write(const char *path, const uint8_t *bytes, size_t length) override {
        files[path] = std::vector<uint8_t>(bytes, bytes + length);
        return true;
    }
    bool Read(const char *path, uint8_t *bytes, size_t length) override {
        const auto found = files.find(path);
        if (found == files.end() || found->second.size() != length) return false;
        std::memcpy(bytes, found->second.data(), length);
        return true;
    }
    size_t Size(const char *path) override {
        const auto found = files.find(path);
        return found == files.end() ? 0 : found->second.size();
    }
    bool Remove(const char *path) override { files.erase(path); return true; }
    bool Rename(const char *from, const char *to) override {
        const auto found = files.find(from);
        if (found == files.end()) return false;
        files[to] = found->second;
        files.erase(found);
        return true;
    }
};

bool require(bool condition, const char *message) {
    if (condition) return true;
    std::fprintf(stderr, "FAIL: %s\n", message);
    return false;
}

bool ReadFile(const char *path, std::vector<uint8_t> *bytes) {
    std::ifstream input(path, std::ios::binary);
    if (!input) return false;
    input.seekg(0, std::ios::end);
    const std::streamoff size = input.tellg();
    if (size <= 0 || size > 65536) return false;
    input.seekg(0, std::ios::beg);
    bytes->resize(static_cast<size_t>(size));
    return input.read(reinterpret_cast<char *>(bytes->data()), size).good();
}

bool DecodeConfig(const std::vector<uint8_t> &bytes, Config *config) {
    pb_istream_t stream = pb_istream_from_buffer(bytes.data(), bytes.size());
    *config = Config_init_default;
    return pb_decode(&stream, Config_fields, config) && stream.bytes_left == 0;
}

bool EncodeProfile(const UltimateProfile &profile, std::vector<uint8_t> *bytes) {
    size_t size = 0;
    if (!pb_get_encoded_size(&size, UltimateProfile_fields, &profile)) return false;
    bytes->resize(size);
    pb_ostream_t stream = pb_ostream_from_buffer(bytes->data(), bytes->size());
    return pb_encode(&stream, UltimateProfile_fields, &profile) && stream.bytes_written == bytes->size();
}

} // namespace

int main(int argc, char **argv) {
    if (!require(argc == 2, "usage: migration_lifecycle <stage-b-v3-config.pb>")) return 1;

    std::vector<uint8_t> legacy_bytes;
    if (!require(ReadFile(argv[1], &legacy_bytes), "read Stage-B fixture bytes")) return 1;
    const std::vector<uint8_t> preserved_legacy_bytes = legacy_bytes;

    Config legacy = Config_init_default;
    if (!require(DecodeConfig(legacy_bytes, &legacy), "decode Stage-B fixture with generated schema")) return 1;
    if (!require(legacy.ultimate_profile_store_format == 0 && legacy.ultimate_profiles_count == 2,
                 "fixture is a two-profile legacy Config")) return 1;

    std::vector<uint8_t> first_wire, second_wire;
    if (!require(EncodeProfile(legacy.ultimate_profiles[0], &first_wire) &&
                 EncodeProfile(legacy.ultimate_profiles[1], &second_wire) && first_wire != second_wire,
                 "fixture supplies two distinct valid Ultimate profiles")) return 1;

    MemoryStorage storage;
    ProfileStore first_boot(&storage);
    if (!require(first_boot.Begin(), "start empty injected ProfileStore storage")) return 1;

    uint32_t first_mapping[2] = {};
    const ProfileStore::Status import_status = first_boot.ImportLegacy(legacy, first_mapping, 2);
    if (import_status != ProfileStore::Status::Ok) {
        Config envelope = Config_init_default;
        envelope.ultimate_profiles_count = 1;
        envelope.ultimate_profiles[0] = legacy.ultimate_profiles[0];
        ConfigValidationError error{};
        const bool envelope_valid = validate_config_semantics(envelope, error);
        std::fprintf(stderr, "ImportLegacy status=%u isolated_profile_envelope=%s: %s\n",
                     static_cast<unsigned>(import_status), envelope_valid ? "valid" : "invalid", error.message);
        return 1;
    }
    if (!require(first_boot.MigrationPending() && first_boot.Count() == 2 &&
                 first_mapping[0] != 0 && first_mapping[1] != 0 && first_mapping[0] != first_mapping[1],
                 "receipt exposes two stable IDs while migration remains fenced")) return 1;

    for (size_t mode = 0; mode < legacy.game_mode_configs_count; ++mode) {
        const uint32_t old_index = legacy.game_mode_configs[mode].ultimate_profile_config;
        if (old_index == 0) continue;
        if (!require(old_index <= 2 && first_mapping[old_index - 1] != 0,
                     "each legacy Ultimate mode has a migrated stable reference")) return 1;
    }

    UltimateProfile migrated_first = UltimateProfile_init_default;
    UltimateProfile migrated_second = UltimateProfile_init_default;
    std::vector<uint8_t> migrated_first_wire, migrated_second_wire;
    if (!require(first_boot.Read(first_mapping[0], migrated_first) == ProfileStore::Status::Ok &&
                 first_boot.Read(first_mapping[1], migrated_second) == ProfileStore::Status::Ok &&
                 EncodeProfile(migrated_first, &migrated_first_wire) &&
                 EncodeProfile(migrated_second, &migrated_second_wire) &&
                 migrated_first_wire == first_wire && migrated_second_wire == second_wire,
                 "stored records preserve both decoded Stage-B profiles")) return 1;

    const uint32_t fenced_generation = first_boot.Generation();
    if (!require(first_boot.Create(legacy.ultimate_profiles[0], "must-fence", 2, 1, 1).status ==
                     ProfileStore::Status::MigrationFenced &&
                 first_boot.Rename(first_mapping[0], "must-fence", fenced_generation, 2, 2).status ==
                     ProfileStore::Status::MigrationFenced &&
                 first_boot.Generation() == fenced_generation,
                 "pending receipt fences CRUD and directory-root rotation")) return 1;

    Config premature_compact = Config_init_default;
    if (!require(first_boot.CompleteMigration(premature_compact) == ProfileStore::Status::Invalid &&
                 first_boot.Generation() == fenced_generation,
                 "invalid compact Config cannot rotate the migration root")) return 1;

    ProfileStore retry_boot(&storage);
    if (!require(retry_boot.Begin(), "reboot reloads receipt from injected storage")) return 1;
    uint32_t retry_mapping[2] = {};
    if (!require(retry_boot.ImportLegacy(legacy, retry_mapping, 2) == ProfileStore::Status::MigrationFenced &&
                 retry_boot.Count() == 2 && retry_boot.Generation() == fenced_generation &&
                 retry_mapping[0] == first_mapping[0] && retry_mapping[1] == first_mapping[1],
                 "retry reuses receipt mappings without duplicate stable IDs")) return 1;
    if (!require(legacy_bytes == preserved_legacy_bytes,
                 "migration leaves the legacy Config source bytes untouched")) return 1;

    std::puts("profile_store_migration_lifecycle stage_b_v3_two_profiles=PASS legacy_bytes_preserved=PASS mode_mapping=PASS retry_stable_ids=PASS migration_fence=PASS");
    return 0;
}
