/* Frozen test-capacity accounting for the persistent Ultimate profile store. */
#ifndef _CORE_PROFILE_STORE_CAPACITY_HPP
#define _CORE_PROFILE_STORE_CAPACITY_HPP

#include <cstddef>

class ProfileStoreCapacity {
  public:
    static constexpr size_t kTestCapacityBytes = 512u * 1024u;
    static constexpr size_t kReservedFreeBytes = 16u * 1024u;

    // Two directory roots remain present while a representative set of
    // immutable records is active.  This is deliberately an upper-bound
    // admission calculation, independent of filesystem allocator details.
    static constexpr bool FitsRepresentativeSet(size_t profile_count,
                                                size_t max_record_bytes,
                                                size_t directory_bytes) {
        return profile_count * max_record_bytes + 2u * directory_bytes <=
               kTestCapacityBytes - kReservedFreeBytes;
    }
};

#endif
