Persistence::LoadResult Persistence::LoadConfigChecked(Config &config) {
    if (!IsAvailable() || _validator == nullptr) {
        return LoadResult::StorageFailure;
    }

    // Config is too large for the core stack. This boot-owned candidate never
    // becomes active and is reset for every attempt, including partial decodes.
    static Config candidate;
    candidate = Config_init_default;

    CompactConfigRecovery::Source source;
    const char *selected_filename = nullptr;
    if (!select_config_filename(config_filename, prior_compact_filename, legacy_config_filename, selected_filename, source))
        return LoadResult::StorageFailure;
    CheckedStorageFile config_file(selected_filename, "r");
    if (!config_file) {
        // The selected Boolean FS API cannot distinguish absence from I/O failure.
        // Absent remains reserved for positively proved absence; it is not inferred.
        return LoadResult::StorageFailure;
    }

    LoadResult failure = LoadResult::Rejected;
    if (!CheckSavedConfig(config_file, &failure)) {
        config_file.close();
        return failure;
    }
    const size_t file_size = config_file.size();
    if (file_size < config_offset || !config_file.seek(config_offset)) {
        config_file.close();
        return LoadResult::StorageFailure;
    }

    ConfigFileReader reader{ &config_file };
    ultimate_native::RejectEmbedded(candidate);
    pb_istream_t istream{};
    istream.callback = read_config_file;
    istream.state = &reader;
    istream.bytes_left = file_size - config_offset;
    if (!pb_decode(&istream, Config_fields, &candidate)) {
        config_file.close();
        return reader.io_failed ? LoadResult::StorageFailure : LoadResult::Rejected;
    }
    if (istream.bytes_left != 0 || config_file.position() != file_size ||
        config_file.size() != file_size) {
        config_file.close();
        return LoadResult::StorageFailure;
    }

    ultimate_native::ClearEmbeddedCallbacks(candidate);
    ConfigValidationError error;
    if (!ValidateConfig(candidate, error)) {
        config_file.close();
        return LoadResult::Rejected;
    }

    ConfigHeader header;
    if (!config_file.seek(0) ||
        config_file.read(reinterpret_cast<uint8_t *>(&header), sizeof(header)) != static_cast<int>(sizeof(header))) {
        config_file.close();
        return LoadResult::StorageFailure;
    }
    if (!config_file.close()) return LoadResult::StorageFailure;
    if (source == CompactConfigRecovery::Source::PriorCompact) {
        auto restored = CheckedStorage::Rename(prior_compact_filename, config_filename, CheckedStorage::Kind::Config);
        if (!restored) {
            if (restored.outcome == CheckedStorage::Outcome::Uncertain) _mutation_fenced = true;
            return LoadResult::StorageFailure;
        }
    }
    config = candidate;
    _config_generation = header.config_crc;
    return LoadResult::Loaded;
}
