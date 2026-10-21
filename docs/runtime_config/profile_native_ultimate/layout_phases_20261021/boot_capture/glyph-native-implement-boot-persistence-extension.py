from pathlib import Path
r=Path('/private/tmp/glyph-profile-native-20261020');p=r/'HAL/pico/src/core/Persistence.cpp';s=p.read_text()
a='SavePhaseState save_phase{};';b=a+'''
// Reuse the original single load candidate; only scalar phase facts survive
// preparation. Filenames below refer solely to the existing static constants.
Config loaded_candidate;
struct LoadPhaseState { CompactConfigRecovery::Source source; uint32_t crc; } load_phase{};
struct CapturePhaseState { const char *filename; size_t length; } capture_phase{};
struct LoadPhaseReset { ~LoadPhaseReset() { std::memset(&load_phase, 0, sizeof(load_phase)); } };
struct CapturePhaseReset { ~CapturePhaseReset() { std::memset(&capture_phase, 0, sizeof(capture_phase)); } };
''';assert s.count(a)==1;s=s.replace(a,b)
s=s.replace('bool copy_checked_file(const char *from,','__attribute__((noinline)) bool copy_checked_file(const char *from,',1).replace('bool hash_file(const char *path,','__attribute__((noinline)) bool hash_file(const char *path,',1).replace('bool Persistence::LegacySourceIdentity(uint8_t digest[32])','__attribute__((noinline)) bool Persistence::LegacySourceIdentity(uint8_t digest[32])',1)
a=s.index('bool Persistence::CaptureLegacySource(uint8_t digest[32])');b=s.index('Persistence::LoadResult Persistence::ReadLegacyProfile(',a);old=s[a:b];Path('/private/tmp/glyph-native-original-capture.cpp').write_text(old)
cut=old.index('    auto removed = Remove("/ultimate-migration.tmp"');prep=old[:cut];execute=old[cut:]
prep=prep.replace('bool Persistence::CaptureLegacySource(uint8_t digest[32])','__attribute__((noinline)) Persistence::CaptureAction Persistence::PrepareCaptureSource(uint8_t digest[32])').replace('    const char *filename = nullptr;','    auto &filename = capture_phase.filename;').replace('    size_t length = 0;','    auto &length = capture_phase.length;').replace('return false;','return CaptureAction::Refused;').replace('        return LegacySourceIdentity(previous) && std::memcmp(previous, digest, sizeof(previous)) == 0;','        return LegacySourceIdentity(previous) && std::memcmp(previous, digest, sizeof(previous)) == 0 ? CaptureAction::ExistingExact : CaptureAction::Refused;')
new=prep+'''    return CaptureAction::NeedsCopy;
}

bool Persistence::CaptureLegacySource(uint8_t digest[32]) {
    using namespace CheckedStorage;
    std::memset(&capture_phase, 0, sizeof(capture_phase));
    CapturePhaseReset reset;
    const auto action = PrepareCaptureSource(digest);
    if (action != CaptureAction::NeedsCopy) return action == CaptureAction::ExistingExact;
'''+execute.replace('copy_checked_file(filename, "/ultimate-migration.tmp", length, uncertain)','copy_checked_file(capture_phase.filename, "/ultimate-migration.tmp", capture_phase.length, uncertain)')
s=s[:a]+new+s[b:]
a=s.index('Persistence::LoadResult Persistence::LoadConfigChecked(Config &config)');b=s.index('\nbool Persistence::CheckSavedConfig()',a);old=s[a:b];Path('/private/tmp/glyph-native-original-load.cpp').write_text(old)
cut=old.index('    if (source == CompactConfigRecovery::Source::PriorCompact)');prep=old[:cut];execute=old[cut:]
prep=prep.replace('Persistence::LoadResult Persistence::LoadConfigChecked(Config &config)','__attribute__((noinline)) Persistence::LoadResult Persistence::ReadConfigCandidate()').replace('    static Config candidate;','    auto &candidate = loaded_candidate;').replace('    CompactConfigRecovery::Source source;','    auto &source = load_phase.source;')
new=prep+'''    load_phase.crc = header.config_crc;
    return LoadResult::Loaded;
}

Persistence::LoadResult Persistence::LoadConfigChecked(Config &config) {
    std::memset(&load_phase, 0, sizeof(load_phase));
    LoadPhaseReset reset;
    const auto prepared = ReadConfigCandidate();
    if (prepared != LoadResult::Loaded) return prepared;
'''+execute.replace('if (source ==','if (load_phase.source ==').replace('    config = candidate;','    config = loaded_candidate;').replace('_config_generation = header.config_crc','_config_generation = load_phase.crc')
s=s[:a]+new+s[b:];p.write_text(s)
p=r/'HAL/pico/include/core/Persistence.hpp';s=p.read_text();a='    SaveResult VerifyExpectedConfigGeneration(uint64_t expected_generation);';s=s.replace(a,'''    enum class CaptureAction : uint8_t { Refused, ExistingExact, NeedsCopy };
    CaptureAction PrepareCaptureSource(uint8_t digest[32]);
    LoadResult ReadConfigCandidate();
'''+a);p.write_text(s)
