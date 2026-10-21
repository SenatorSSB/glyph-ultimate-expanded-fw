# Initial lookahead and first inline-file growth: finite source lemma

This is an existence argument about permitted source states, not a target
measurement, a complete filesystem image witness, or a whole-stack PASS.
Production is frozen at4209c03a5cd35416ab7fdd6d9a349c063e06106e.

In the pinned LittleFS implementation, successful mount ends with
`lfs_alloc_drop`: both `free.size` and `free.i` become zero. `lfs_alloc_ack`
changes only `free.ack`. Read-only file and directory activity does not refill
the allocator lookahead. A healthy filesystem with no pending global changes
does not require an allocation merely to execute force-consistency.

A root directory can have an erased append region with enough room for one
small new regular-file entry. The create branch commits CREATE, name and empty
INLINESTRUCT attributes. The append/CRC success branch of relocatingcommit
does not call `lfs_alloc`. Thus neither an absent temporary-file removal nor
creation of a new temporary-file name necessarily forces an earlier allocator
scan. Creating its file cache uses heap allocation, which is distinct from
LittleFS block allocation. This is not a claim that every root history appends.

The new file starts inline at position zero. Current target configuration has
cache_size256 and block_size4096, so the inline threshold is256. Writes that do
not cross that threshold need not allocate a filesystem block. The first write
whose resulting size exceeds256 calls outline, which acknowledges allocations
and then calls relocate. With lookahead still empty, relocate calls alloc, whose
first scan follows immediately through rawtraverse. These predicates have no
source-level contradiction in a healthy phase2, format0/root2/count0
Configurator start. The normal boot marker/migration conditions permit that
start without an intervening Config write.

Consequently, an empty-lookahead scan during the first payload outline must
remain a feasible case unless a stronger exact predecessor invariant is proved.
It cannot be excluded merely because the file open already completed.

The cache-miss/read-callback and deepest encoder-stack co-liveness are separate
obligations. Root metadata beyond one cache chunk can leave reads near its tail,
while allocator directory fetch begins at a revision word; that provides a
candidate miss construction, but this note does not claim its complete cache
trace is proved. The resource worker separately checks exact encoder position,
emitted frames, interrupt eligibility and full route arithmetic.

No source, filesystem image, device state, build flags, support-domain contract
or resource limit was changed. Earlier conditional equations remain historical.
