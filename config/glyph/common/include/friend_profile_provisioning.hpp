#pragma once

// Private, boot-only installer. setup() calls this before releasing core1.
// No runtime-loaded coordinate architecture or canonical migration is involved.
#include "core/Persistence.hpp"
#include <pb_encode.h>
#include <cstring>

namespace friend_profile {
constexpr char kMarkerPath[] = "/friend_ultimate_20261011_applied.flag";
constexpr char kMarkerPayload[] = "friend_ultimate_20261011_applied_v1\n";
constexpr size_t kMarkerLength = sizeof(kMarkerPayload) - 1;

inline bool marker_valid() {
    File marker = LittleFS.open(kMarkerPath, "r");
    if (!marker) return false;
    bool valid = marker.size() == kMarkerLength;
    for (size_t i = 0; valid && i < kMarkerLength; ++i) {
        valid = marker.read() == static_cast<unsigned char>(kMarkerPayload[i]);
    }
    valid = valid && marker.read() == -1;
    marker.close();
    return valid;
}

struct Comparison {
    const uint8_t *expected;
    size_t length;
    size_t position;
};

inline bool compare_chunk(pb_ostream_t *stream, const pb_byte_t *bytes, size_t count) {
    auto &comparison = *static_cast<Comparison *>(stream->state);
    if (count > comparison.length - comparison.position ||
        std::memcmp(comparison.expected + comparison.position, bytes, count) != 0) {
        return false;
    }
    comparison.position += count;
    return true;
}

// Compare every persisted field through deterministic nanopb encoding, without
// comparing C++ padding. The fixed private buffer bounds this installer only.
inline bool config_equal(const Config &expected, const Config &actual,
                         size_t &expected_length, size_t &actual_length) {
    static uint8_t encoded_expected[16384];
    expected_length = actual_length = 0;
    if (!pb_get_encoded_size(&expected_length, Config_fields, &expected) ||
        !pb_get_encoded_size(&actual_length, Config_fields, &actual) ||
        expected_length != actual_length || expected_length > sizeof(encoded_expected)) {
        return false;
    }
    auto expected_stream = pb_ostream_from_buffer(encoded_expected, sizeof(encoded_expected));
    if (!pb_encode(&expected_stream, Config_fields, &expected) ||
        expected_stream.bytes_written != expected_length) return false;
    Comparison comparison{encoded_expected, expected_length, 0};
    pb_ostream_t actual_stream{};
    actual_stream.callback = compare_chunk;
    actual_stream.state = &comparison;
    actual_stream.max_size = actual_length;
    return pb_encode(&actual_stream, Config_fields, &actual) &&
        actual_stream.bytes_written == actual_length && comparison.position == expected_length;
}

inline bool provision_once(Config &defaults) {
    if (!persistence.IsAvailable()) return false;
    if (marker_valid()) return true;
    ConfigValidationError error;
    if (!persistence.ValidateConfig(defaults, error) || !persistence.SaveConfig(defaults)) return false;
    // Match LoadConfigChecked's established stack-safe boot candidate pattern.
    static Config readback;
    readback = Config_init_default;
    if (persistence.LoadConfigChecked(readback) != Persistence::LoadResult::Loaded ||
        !persistence.ValidateConfig(readback, error)) return false;
    size_t expected_length = 0, actual_length = 0;
    if (!config_equal(defaults, readback, expected_length, actual_length)) return false;
    File marker = LittleFS.open(kMarkerPath, "w");
    if (!marker) return false;
    const bool written = marker.write(reinterpret_cast<const uint8_t *>(kMarkerPayload),
                                      kMarkerLength) == kMarkerLength;
    marker.flush();
    marker.close();
    if (!written || !marker_valid()) {
        LittleFS.remove(kMarkerPath);
        return false;
    }
    return true;
}
} // namespace friend_profile
