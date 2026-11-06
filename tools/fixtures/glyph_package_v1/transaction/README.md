# Portable package transaction host proofs

Copy `build.py`, `run.py`, `regressions.py` and `harness.cpp` together. The tools
read an explicit candidate repository and immutable `glyph-package-v1` corpus;
there are no worker-directory paths in their source.

```sh
python3 path/to/run.py --repo GLYPH_REPO --corpus FROZEN_CORPUS --out EVIDENCE
python3 path/to/regressions.py --repo GLYPH_REPO --corpus FROZEN_CORPUS \
  --out REGRESSION_EVIDENCE --binary EVIDENCE/build/package-fault-harness
```

`run.py` builds automatically. `--framework` and `--nanopb` override the usual
PlatformIO dependency locations. Arduino-Pico must be exactly3.6.3. The host needs
C/C++17 compilers, Python protobuf/grpcio-tools and the repository's existing host
fixture dependencies. No dependency installation, hardware or Git action occurs.

For a bounded smoke run use `--contexts first,second,prior --limit 2`. Such a run
returns `complete:false`; it is never the complete gate. `--start` and `--limit`
select event ranges for diagnosis. Use a fresh output directory for final evidence.
`--no-build` verifies the existing manifest against current source/tool hashes and
refuses stale inputs. A completed full run requires `summary.json` to contain
`complete:true` with no failures, not merely an exit code from a bounded probe.

## Exact production binding

The harness includes the actual candidate `ProfileStore.cpp` and links actual
Persistence, source adapter, complete namespace classifier, storage format,
CheckedStorage/fence, strict Config parser, native program and configured Glyph
semantic validators. It freshly generates nanopb files from the candidate schema
and options. `build/source-manifest.json` binds all compiled source, important
headers, tool sources, generated files, exact framework header and binary hash.

Filesystem operations use the real pinned LittleFS engine against a512KiB NOR
model enforcing1->0 programming and4096-byte erase. The Arduino host facade only
supplies constructor configuration/mount availability; it is not the storage
backend. The separate real-framework no-autoformat proof remains required.
Neither this harness nor synthetic NOR establishes physical durability/gameplay.

## Publication cuts and restart

`seed` is the only mode that formats. It deliberately creates the initial test
namespace, closes every seed file, verifies exact bytes and saves raw NOR.

Every `execute` process consumes that exact NOR image. Its fault hook records
EVERY Before/After CheckedStorage operation while an admitted package writer owns
the transaction. On the selected boundary it captures raw NOR immediately, then
returns Before Fail or After LostAcknowledgement. Error unwind must leave those
raw bytes unchanged and release all native handles. Same-boot QUERY and STATUS
must retain the sticky central fence and perform zero writes.

A NEW `inspect` process mounts the captured raw image directly: no formatting,
namespace reseeding, restoration or reconstruction. Boot, QUERY, explicit known
CREATE re-entry, a fresh token against pending reservation/stale guards, raw-writer
fence denial and pending LIST/READ/Activate checks all assert0program/0erase and
exact unchanged NOR. Known terminal re-entry is read-only; a genuinely unaccepted
fresh request is not automatically retried. Unscoped direct CheckedStorage writes
must also fail without effects.

Restart queries are compared with the immutable Python query model for the actual
observed namespace, including older package receipts during later PREPARED,
changed digest, unknown high token, source root/control/G6 receipt collisions and
current Config SHA. Every produced response is checked by the immutable closed
operation/status/disposition grammar. Only exact source-validator tuples and
construction of the constant schema adapter are memoized. Every namespace
classification/query still executes; outcomes are not cached across cuts.

Three contexts cover first V2->V3 publication, second publication with the retained
mixed V2/V3 peer, and later publication after raw/G6/default changes with protected
older receipts. Clean CREATE namespaces must match the immutable complete final
namespace byte for byte. Lost successful responses are modeled by discarding the
packet and restarting from committed NOR; exact CREATE re-entry cannot republish.

Passing cut images and actual event traces are losslessly zlib-compressed after
restart checks; raw SHA256 is retained in results.jsonl. Failure images stay raw.
Each record binds the source fingerprint and exact event. A progress/interrupted
summary always has `complete:false`.

## Additional actual-source regressions

`regressions.py` currently performs30 checks/groups:

- Allowed raw UPDATE, DUPLICATE, RENAME, REORDER, DELETE, root advance and GC.
- Exact old managed entry/aggregate/intent/record/Config preservation after each.
- Allowed actual G6 save and managed receipt validation; candidate guards cover
  owned row/RGB rewrite, foreign managed reference, package-token reuse, stale
  generation and impossible/nonexistent G6 result identity/generation.
- Subsequent CREATE uses ID5 after duplicate/delete consumed ID4; complete final
  namespace equals the immutable model.
- Two source-valid canonical Config bodies with equal CRC32/distinct SHA256:
  expected SHA guard refuses with CONFLICT and zero writes.
- Native header and preprocessing-context negatives return INVALID/zero writes.
- Missing protected current/previous raw record and used<observed logical bytes
  refuse before any publication.
- Four immutable CREATE semantic digest witnesses, including maximum frame input.
- Canonical/source-invalid unmarked prior Config refuses without overwriting it;
  RGB count30 plus present new RGB returns FULL7/zero writes.
- Public SaveConfig rejects impossible G6 receipt fields and changed completed
  migration-v2 receipt without writes.
- Default ProfileStoreStorage fallback and historical delete helper negatives:
  unresolved, unsupported, unscoped, wrong path/token, package scope rejection
  before effects, and revoked legacy authority recheck before destination removal.

## Actual evidence retained here and remaining gaps

Recorded bounded smoke:6 cuts PASS (2 in each context), complete:false. Recorded
actual regression suite:30 PASS. Each is bound to its build/source manifest; later
parent repairs, including8ff34e08, require a fresh build and affected reruns. Earlier source snapshots
recorded4817/5030 cut passes and2099 passes respectively, no observed failures;
those runs were stopped when source review repairs invalidated their snapshots.
They are conditional historical evidence, never final candidate coverage.

The recorded clean traces contain1388 first-transition,1612 second-transition and
2030 prior-receipt Before/After events:5030 total. Rerun the default complete
matrix after all root-owned repairs and exact source/tool snapshot are settled.

This harness starts at the actual canonical decoder/ProfileStore dispatch seam.
It DOES NOT compile ConfiguratorBackend or packetio command9/COBS transport. Exact
transport dispatch/framing remains a separate required proof. It checks response
shapes exercised by real operations, not the entire3120-shape combinatorial corpus.
The four actual digest vectors are covered. All abstract admission boundary
witnesses are not replayed through production here; targeted concrete binding
counterexamples above are covered. Linked target flash/static/stack/IRQ/resource
proof, independent review, final commit/publication and physical acceptance remain
parent-owned gates. Host alias/bounds/unwind assertions are not ARM resource proof.

Final handoff gaps added by the last parent review: exact6/7-byte future-root
marker controls and preflight final-recheck I/O lost-ack versus positive-drift
controls are not added to these30 regressions. Parent retained concrete probes
and owns extending them. Malformed nested payload INVALID response behavior is
also outside this ProfileStore-seam harness and needs actual backend coverage.
No full matrix is running at handoff; prior runs were stopped on source drift.
