#pragma once
#include "core/Sha256.hpp"
#include <config.pb.h>
#include <pb_encode.h>

namespace runtime_identity {
// Descriptor-generic: all known fields, no native padding, Config or headers.
inline bool PayloadDigest(const UltimateProfile &profile, uint8_t digest[32]) {
    Sha256 hash;
    static constexpr char domain[] = "Glyph.RuntimeIdentity.UltimateProfile.v1";
    hash.Update(domain, sizeof(domain));
    pb_ostream_t stream = {};
    stream.callback = [](pb_ostream_t *out, const pb_byte_t *bytes, size_t count) -> bool {
        static_cast<Sha256 *>(out->state)->Update(bytes, count);
        return true;
    };
    stream.state = &hash;
    stream.max_size = 4096; // Existing admitted standalone profile bound; callback removes generated size macro.
    if (!pb_encode(&stream, UltimateProfile_fields, &profile)) return false;
    hash.Final(digest);
    return true;
}
} // namespace runtime_identity
