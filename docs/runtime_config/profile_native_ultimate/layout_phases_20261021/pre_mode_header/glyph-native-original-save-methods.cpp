Persistence::SaveResult Persistence::SaveConfigIfGenerationMatches(Config &config, uint64_t expected_generation) {
    if (_mutation_fenced) return SaveResult::Uncertain;
    if (expected_generation != _config_generation) return SaveResult::Conflict;
    if (!IsAvailable()) return SaveResult::StorageFailure;
    CompactConfigRecovery::Source source;
    const char *filename = nullptr;
    if (!select_config_filename(config_filename, prior_compact_filename, legacy_config_filename, filename, source))
        return SaveResult::StorageFailure;
    CheckedStorageFile current(filename, "r");
    if (!current) return SaveResult::StorageFailure;
    ConfigHeader header;
    const bool checked = CheckSavedConfig(current) && current.seek(0) &&
        current.read(reinterpret_cast<uint8_t *>(&header), sizeof(header)) == static_cast<int>(sizeof(header));
    const bool current_closed = current.close();
    if (!checked || !current_closed) return SaveResult::StorageFailure;
    if (expected_generation != header.config_crc) return SaveResult::Conflict;
    // All Config writers execute synchronously on core0. No callback or yield
    // runs a Config writer between this fence and SaveConfig's publication.
    if (SaveConfig(config)) return SaveResult::Saved;
    return _mutation_fenced ? SaveResult::Uncertain : SaveResult::StorageFailure;
}

bool Persistence::SaveConfig(Config &config) {
    using namespace CheckedStorage;
    if (!IsAvailable() || _mutation_fenced) return false;
    size_t encoded_size = 0;
    if (!pb_get_encoded_size(&encoded_size, Config_fields, &config)) return false;
    static constexpr char temporary_filename[] = "config-v2.tmp";
    auto removed = Remove(temporary_filename, Kind::Config);
    if (!removed) { _mutation_fenced = removed.outcome == Outcome::Uncertain; return false; }
    ConfigHeader header{};
    {
        CheckedStorageFile file(temporary_filename, "w+");
        auto staging_failed = [this, &file]() {
            file.close();
            if (file.uncertain()) _mutation_fenced = true;
            return false;
        };
        if (!file) return staging_failed();
        if (file.write(reinterpret_cast<const uint8_t *>(&header), sizeof(header)) != sizeof(header))
            return staging_failed();
        pb_ostream_t stream = as_pb_ostream(file);
        if (!pb_encode(&stream, Config_fields, &config) || stream.bytes_written != encoded_size || !file.seek(config_offset))
            return staging_failed();
        CRC32 crc;
        for (size_t i = 0; i < encoded_size; ++i) {
            int value = file.read();
            if (value < 0) return staging_failed();
            crc.update(static_cast<uint8_t>(value));
        }
        header.config_size = encoded_size; header.config_crc = crc.finalize();
        if (!file.seek(0) || file.write(reinterpret_cast<const uint8_t *>(&header), sizeof(header)) != sizeof(header) || !file.sync())
            return staging_failed();
        if (!file.close()) { _mutation_fenced = file.uncertain(); return false; }
    }
    {
        CheckedStorageFile staged(temporary_filename, "r");
        bool verified = staged && CheckSavedConfig(staged) && staged.seek(config_offset);
        // Compare independently reopened bytes with a second deterministic encode.
        verified = verified && compare_config_bytes(staged, config, encoded_size);
        if (!staged.close() || !verified) { _mutation_fenced = staged.uncertain(); return false; }
    }

    auto current = Stat(config_filename, nullptr, Kind::Config);
    if (!current && current.outcome != Outcome::NotFound) return false;
    if (current) {
        auto prior_removed = Remove(prior_compact_filename, Kind::Config);
        if (!prior_removed) { _mutation_fenced = prior_removed.outcome == Outcome::Uncertain; return false; }
        auto rotated = Rename(config_filename, prior_compact_filename, Kind::Config);
        if (!rotated) { _mutation_fenced = rotated.outcome == Outcome::Uncertain; return false; }
    }
    _pending_crc = header.config_crc; _pending_size = encoded_size;
    auto publication = Rename(temporary_filename, config_filename, Kind::Config);
    if (!publication) {
        if (publication.outcome == Outcome::Uncertain) {
            _mutation_fenced = true;
            // Exact authenticated readback can resolve a lost acknowledgement.
            CheckedStorageFile published(config_filename, "r");
            ConfigHeader actual{};
            bool match = published && CheckSavedConfig(published) && published.seek(0) &&
                published.read(reinterpret_cast<uint8_t *>(&actual), sizeof(actual)) == static_cast<int>(sizeof(actual)) &&
                actual.config_crc == _pending_crc && actual.config_size == _pending_size &&
                compare_config_bytes(published, config, encoded_size);
            if (published.close() && match) {
                _config_generation = header.config_crc; _mutation_fenced = false; return true;
            }
            return false;
        }
        if (current) {
            auto rollback = Rename(prior_compact_filename, config_filename, Kind::Config);
            if (!rollback) _mutation_fenced = true;
        }
        return false;
    }
    _config_generation = header.config_crc;
    return true;
}

