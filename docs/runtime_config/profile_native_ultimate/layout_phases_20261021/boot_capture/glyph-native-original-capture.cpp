bool Persistence::CaptureLegacySource(uint8_t digest[32]) {
    using namespace CheckedStorage;
    if (!IsAvailable() || _mutation_fenced) return false;
    CompactConfigRecovery::Source selected;
    const char *filename = nullptr;
    if (!select_config_filename(config_filename, prior_compact_filename, legacy_config_filename, filename, selected)) return false;
    size_t length = 0;
    {
        CheckedStorageFile source(filename, "r");
        if (!source) return false;
        const bool valid = CheckSavedConfig(source);
        length = source.size();
        if (!source.close() || !valid) return false;
    }
    if (length > 65536 || !hash_file(filename, digest)) return false;
    auto snapshot = Stat("/ultimate-migration.src", nullptr, Kind::Config);
    if (snapshot) {
        uint8_t previous[32];
        return LegacySourceIdentity(previous) && std::memcmp(previous, digest, sizeof(previous)) == 0;
    }
    if (snapshot.outcome != Outcome::NotFound) return false;
    Geometry geometry{};
    if (!Capacity(geometry) || !geometry.erase_bytes) return false;
    // Snapshot must not consume the project reserve or copy-on-write metadata
    // reserve even before ProfileStore performs its complete import admission.
    const uint64_t blocks = (uint64_t(length) + geometry.erase_bytes - 1) / geometry.erase_bytes;
    const uint64_t charged = uint64_t(length) + 4 * (blocks + 1);
    const uint64_t staged = ((charged + geometry.erase_bytes - 1) / geometry.erase_bytes) * geometry.erase_bytes;
    if (geometry.free_bytes < staged + 16384 + uint64_t(4) * geometry.erase_bytes) return false;
    auto removed = Remove("/ultimate-migration.tmp", Kind::Config);
    if (!removed) { _mutation_fenced = removed.outcome == Outcome::Uncertain; return false; }
    bool uncertain = false;
    if (!copy_checked_file(filename, "/ultimate-migration.tmp", length, uncertain)) {
        _mutation_fenced = uncertain; return false;
    }
    uint8_t actual[32];
    if (!hash_file("/ultimate-migration.tmp", actual) || std::memcmp(actual, digest, sizeof(actual))) return false;
    auto published = Rename("/ultimate-migration.tmp", "/ultimate-migration.src", Kind::Config);
    if (!published && published.outcome != Outcome::Uncertain) return false;
    if (!LegacySourceIdentity(actual) || std::memcmp(actual, digest, sizeof(actual))) {
        _mutation_fenced = published.outcome == Outcome::Uncertain; return false;
    }
    return true;
}

