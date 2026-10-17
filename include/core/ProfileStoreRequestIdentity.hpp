#pragma once
#include <config.pb.h>
#include <pb_encode.h>
#include "core/ProfileStoreTransaction.hpp"
#include "core/Sha256.hpp"

// Request identity domain v1: ASCII domain including NUL followed by nanopb's
// deterministic semantic encoding of the decoded request with token zero.
// All known request fields (presence, payload, generations, ID, name, rank,
// mode and operation) are bound. Unknown protobuf fields have no semantics.
// The independent full 64-bit token is persisted alongside this digest.
inline bool ProfileStoreRequestIdentity(ProfileStoreRequest &request,
                                        ProfileStoreTransactionIdentity &identity) {
    Sha256 hash;
    static constexpr char domain[] = "Glyph.ProfileStore.Request.v1";
    hash.Update(domain, sizeof(domain));
    pb_ostream_t stream = {};
    stream.callback = [](pb_ostream_t *out, const pb_byte_t *bytes, size_t count) -> bool {
        static_cast<Sha256 *>(out->state)->Update(bytes, count); return true;
    };
    stream.state = &hash;
    stream.max_size = SIZE_MAX;
    identity.token = request.request_token;
    request.request_token = 0;
    const bool ok = pb_encode(&stream, ProfileStoreRequest_fields, &request);
    request.request_token = identity.token;
    if (ok) hash.Final(identity.digest);
    return ok;
}
