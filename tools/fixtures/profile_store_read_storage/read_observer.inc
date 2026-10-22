#include "core/config_validation.hpp"
static unsigned read_phases = 0;
static unsigned observed_storage[16]{};
void ReadStoragePhase(unsigned phase) { read_phases |= 1u << phase; }
void reset_read_observation() { read_phases = 0; std::memset(observed_storage, 0, sizeof(observed_storage)); }
CheckedStorage::Fault read_observer(Kind, CheckedStorage::Operation operation,
                                  CheckedStorage::Phase phase, const char *) {
    if (phase == CheckedStorage::Phase::After) ++observed_storage[unsigned(operation)];
    return CheckedStorage::Fault::None;
}
void roundtrip_response(const ProfileStoreResponse &response, const char *label, bool print) {
    // Callback descriptors have no generated size macro. Profiles retain the
    // admitted4096 bound; each actual response must fit the existing8192 frame.
    static_assert(4096 < 8192, "admitted profile fits response frame");
    uint8_t frame[8192];
    size_t n = 0;
    require(pb_get_encoded_size(&n, ProfileStoreResponse_fields, &response), "response size terminates");
    auto stream = pb_ostream_from_buffer(frame, sizeof(frame));
    require(pb_encode(&stream, ProfileStoreResponse_fields, &response) && stream.bytes_written == n,
            "real nanopb response encode within frame");
    ProfileStoreResponse decoded = ProfileStoreResponse_init_default;
    auto input = pb_istream_from_buffer(frame, n);
    require(pb_decode(&input, ProfileStoreResponse_fields, &decoded) && !input.bytes_left,
            "response full nanopb decode");
    require(decoded.has_profile && encode(decoded.profile) == encode(response.profile),
            "response profile exact roundtrip");
    if (print) std::printf("response label=%s id=%u profile_bytes=%zu response_bytes=%zu host_response_object=%zu response_frame_bound=%u admitted_profile_bound=%u frame=8192\n",
            label, response.profile_id, encode(response.profile).size(), n, sizeof(response),
            unsigned(8192), unsigned(4096));
}
Bytes fixture_bytes(const char *path) {
    std::ifstream in(path, std::ios::binary);
    require(bool(in), "fixture file exists");
    return Bytes(std::istreambuf_iterator<char>(in), {});
}
void check_profile_fixture(const char *path, const char *label) {
    auto b = fixture_bytes(path);
    ProfileStoreResponse response = ProfileStoreResponse_init_default;
    auto input = pb_istream_from_buffer(b.data(), b.size());
    require(pb_decode(&input, UltimateProfile_fields, &response.profile) && !input.bytes_left,
            "maximum fixture nanopb decode");
    ConfigValidationError error;
    require(validate_ultimate_profile_semantics(response.profile, error), "maximum fixture actual validator");
    require(b.size() <= 4096, "maximum fixture admitted record wire bound");
    response.has_profile = true; response.protocol_version = 1; response.profile_id = 1;
    response.profile_revision = 130; response.store_generation = 160;
    for (unsigned i = 0; i < 1000; ++i) roundtrip_response(response, label, i == 0);
}
void check_retained_response(const char *path, const char *label) {
    auto b = fixture_bytes(path);
    ProfileStoreResponse response = ProfileStoreResponse_init_default;
    auto input = pb_istream_from_buffer(b.data(), b.size());
    require(pb_decode(&input, ProfileStoreResponse_fields, &response) && !input.bytes_left,
            "retained physical response nanopb decode");
    ConfigValidationError error;
    require(validate_ultimate_profile_semantics(response.profile, error), "physical profile validation");
    for (unsigned i = 0; i < 1000; ++i) roundtrip_response(response, label, i == 0);
}

#if READ_PRODUCTION_TRACE
#include "core/ProfileStoreReadTrace.hpp"
struct TraceObservation { unsigned next=10, fail=0; };
bool trace_observer(void *context, uint32_t stage, uint32_t value) {
    auto &o = *static_cast<TraceObservation *>(context);
    require(stage == o.next++, "production trace stages strictly 10 through 18");
    if (stage == 11) require(value > 32 && value <= 4128, "trace reports record bytes");
    if (stage == 18) require(value == 1, "trace reports validation success");
    return stage != o.fail;
}
void check_failed_trace_cleanup(ProfileStore &s) {
    for (unsigned fail = 10; fail <= 18; ++fail) {
        { TraceObservation observed; observed.fail=fail;
          ProfileStoreReadTrace::Scope scope(trace_observer, &observed);
          UltimateProfile out{};
          require(s.Read(1,out) == Status::Invalid && ProfileStoreReadTrace::Failed(), "failed trace aborts read");
          require(observed.next == fail+1, "no stages after failed observer"); }
        no_leaks("trace failure cleanup");
        UltimateProfile out{};
        require(s.Read(1,out) == Status::Ok, "scope restores untraced READ");
    }
    std::puts("production_trace=PASS ordered_stages=10..18 failure_each_stage=true close_and_allocation_cleanup=true scope_restores_READ=true");
}
#endif
