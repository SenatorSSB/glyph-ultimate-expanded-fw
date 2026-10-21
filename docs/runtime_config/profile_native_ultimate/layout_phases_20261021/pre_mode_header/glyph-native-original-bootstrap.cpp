__attribute__((always_inline)) inline bool ProfileStore::Bootstrap(bool recovery) {
    if (_required_root_format > 2) {
        _root_invalid = true;
        _read_only_recovery = true;
        return false;
    }
    static CheckedStorage::Geometry g; g = {};
    if (!_storage->Geometry(g) || !g.erase_bytes || g.total_bytes < kReserve) {
        _read_only_recovery = true;
        return false;
    }
    static Result ctrl; ::new (&ctrl) Result(_storage->Probe(kControl));
    if (ctrl.outcome != Outcome::NotFound) {
        uint32_t phase = 0;
        if (!ctrl || !LoadControl(*_next, phase)) {
            _read_only_recovery = true;
            return false;
        }
        _v2 = true;
        if (_expected_incarnation && _next->incarnation != _expected_incarnation) {
            _read_only_recovery = true;
            return false;
        }
        if (phase == 1) {
            if (recovery) {
                _read_only_recovery = true;
                return false;
            }
            return InitializeV2(*_next);
        }
        if (phase == 3) {
            _uncertain = true;
            if (recovery) {
                LoadDirectory();
                _read_only_recovery = true;
                return _ready;
            }
            return ReconcileTransaction();
        }
        const uint32_t floor = _next->generation, high = _next->high_water_id,
                       inc = _next->incarnation;
        if (!LoadDirectory())
            return false;
        if (Generation() != floor || _directory->high_water_id != high || Incarnation() != inc ||
            !SameDirectory(*_directory, *_next)) {
            _root_invalid = true;
            _read_only_recovery = true;
            return _ready;
        }
        return true;
    }
    // Config independently records that v2 authority was accepted. Losing all
    // v2 files must not resurrect the retained pre-upgrade v1 roots.
    if (_required_root_format >= 2) {
        _root_invalid = true;
        _read_only_recovery = true;
        return false;
    }
    // A missing control with any v2 path is damaged, never permission to downgrade.
    for (unsigned i = 0; i < 2; ++i) {
        static char p[32];
        RootPath(p, sizeof(p), i);
        if (_storage->Probe(p).outcome != Outcome::NotFound) {
            _read_only_recovery = true;
            return false;
        }
    }
    bool exists[2]{}, valid[2]{};
    static uint8_t old[kLegacyDirectoryBytes];
    for (unsigned i = 0; i < 2; ++i) {
        static char p[32];
        ProfileStorePaths::DirectoryPath(p, sizeof(p), i);
        static Result probe; ::new (&probe) Result(_storage->Probe(p));
        exists[i] = probe.outcome != Outcome::NotFound;
        valid[i] = probe && _storage->CheckedRead(p, old, sizeof(old), Kind::Root) &&
                   DecodeLegacy(old, sizeof(old), i ? _other : _directory);
    }
    if (exists[0] || exists[1]) {
        if (!valid[0] || !valid[1]) {
            _root_invalid = true;
            if (valid[1])
                *_directory = *_other;
            _ready = valid[0] || valid[1];
            _read_only_recovery = true;
            return _ready;
        }
        if (_directory->incarnation != _other->incarnation ||
            (_directory->generation == _other->generation &&
             !SameDirectory(*_directory, *_other))) {
            _read_only_recovery = true;
            return false;
        }
        if (_other->generation > _directory->generation) {
            Directory *swap = _directory;
            _directory = _other;
            _other = swap;
        }
        if (_directory->generation - _other->generation > 1 ||
            _directory->high_water_id < _other->high_water_id) {
            _read_only_recovery = true;
            return false;
        }
        if (_expected_incarnation && Incarnation() != _expected_incarnation) {
            _read_only_recovery = true;
            return false;
        }
        _ready = true;
        if (recovery || _directory->migration_state == 1) {
            _read_only_recovery = true;
            return true;
        }
        // Preserve every existing payload; malformed dependencies stop upgrade.
        for (size_t i = 0; i < Count(); ++i) {
            const auto &e = _directory->entries[i];
            if (!ReadProfile(e.id, e.revision, _candidate_profile) ||
                (e.previous_revision &&
                 !ReadProfile(e.id, e.previous_revision, _candidate_profile))) {
                _read_only_recovery = true;
                return false;
            }
        }
        for (size_t i = 0; i < _directory->migration_count; ++i) {
            if (!ReadProfile(
                    _directory->migration_ids[i],
                    _directory->migration_revisions[i],
                    _candidate_profile
                ) ||
                !HashMessage(
                    UltimateProfile_fields,
                    &_candidate_profile,
                    _directory->migration_payloads[i]
                )) {
                _read_only_recovery = true;
                return false;
            }
        }
        if (_directory->migration_count)
            Receipt(*_directory);
    } else {
        if (_expected_incarnation || recovery) {
            _read_only_recovery = true;
            return false;
        }
        _directory->incarnation = 1;
    }
    // Reserve bootstrap/upgrade space before the first new persistent authority.
    if (g.free_bytes <
        kReserve + 4 * FileCharge(kDirectoryWireBytes + 16, g.erase_bytes) + 4ull * g.erase_bytes) {
        _read_only_recovery = true;
        return false;
    }
    *_next = *_directory;
    if (!WriteControl(*_next, 1)) {
        _read_only_recovery = true;
        return false;
    }
    _v2 = true;
    return InitializeV2(*_next);
}
