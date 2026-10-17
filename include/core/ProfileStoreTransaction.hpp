#pragma once
#include <cstdint>
#include <cstring>
struct ProfileStoreTransactionIdentity {
    uint64_t token = 0;
    uint8_t digest[32] = {};
    bool SameRequest(const ProfileStoreTransactionIdentity &other) const {
        return token == other.token && std::memcmp(digest, other.digest, sizeof(digest)) == 0;
    }
};
