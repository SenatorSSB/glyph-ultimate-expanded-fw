# GP-CONFIG-020: bounded Button ABI repair

Status: dual-ABI host proof PASS; postcommit target object proof required in the source-free handoff. No firmware or hardware acceptance.

## Authority and lineage

The direct starting base is `0f7fe50b3b5f385397a9737bc4c0a50ddda683c8`.
The immutable proposal is `76cb953cd6bfe5398db11669f3d195175361700c`,
with same-base Curator receipt `5a82aa06e116cb8c8580cee87a55f1ea98f406cb`.
Both originate at `38017600deb243b5e281edec6d0d378b997d9e40`.
The adopted C020 order authorizes this new attempt; GP-VAL-043 is its separate
finite governance successor. GP-VAL-037 remains DONE for its original contract.

Original C `256bf44cea71f6d5c87aa1675c8dac9f6b79259f`, its parent
`3dac79dac4eefcf832510817e8cb5ecd6a27f219`, and failed F
`0a5dd751c391198140ed146853a69fc825d902c7` remain unchanged.
This repair is constructed directly on the adopted base. Its exact commit,
parent, tree and complete eleven-path raw inventory belong in the later
source-free handoff, avoiding a commit hash referring to itself.

## Source change

The original validator assumed a four-byte Button. The actual selected Mk6
compiler instead reported one byte and refused that candidate's static
assertions. The generated header matched the authenticated fixture.

This repair asserts eight-bit bytes, an unsigned underlying enum type without
padding, and one of the verified one- or four-byte widths. The target proof
separately requires one byte. It retains full-object `memcmp` comparisons;
there is no narrowing or untrusted typed enum read. All 60 named IDs, the 12
binding classes, count checks, traversal and remap-disable decision remain
unchanged. The handler insertion, public header and TinyUSB host stub are
identical to original C. Schema, decoder, defaults, build flags and all other
critical source are unchanged.

## Evidence boundary

The JSON companion records source identities and host proof results before
commit. The explicitly authorized actual Mk6 diagnostic compile is performed
only after the clean candidate commit; its exact candidate-bound execution
record belongs in the later source-free handoff. It compiles objects only.
A full firmware link and UF2 remain prohibited until GP-VAL-043 strict DONE.

The dedicated SetConfig harness mocks the binding validator result. Its
call-order and transaction tests do not establish actual-helper transaction
behavior. GP-VAL-043 separately owns both ABI configurations of the existing
real-helper transaction consumer. This report does not claim that successor
obligation has passed.

The earlier canonical-fingerprint anomaly remains UNKNOWN. The additional
synthetic accepted-transition suite run on failed F remains a failed run: its
fixture used a source-bearing candidate where a source-free base was required.
Neither record is waived or relabelled PASS. New 043 synthetic fixtures must
start from the authenticated source-free base.

No hardware test, artifact custody, device write, flashing or release is part
of this phase. No stored-load protection, RGB policy, USB fallback or gameplay
semantics are added. Nunchuk remains NOT_TESTED and the root cause of earlier
physical behavior remains unproven.

## Host results

Both explicit ABI modes pass the complete focused checker. Short mode observes
Button size/alignment 1/1 and Config 26912/8; ordinary mode observes Button 4/4
and Config 51240/8. These host Config layouts are not claimed identical to Mk6.
Each mode verifies all 12 descriptor sizes, offsets, strides and capacities
before decoding, exhausts raw and wire byte values across all binding classes,
and retains accepted defaults, nested counts, last-element rejection, ordering,
mask identity and no mutation. Wide wire outcomes are recorded in the JSON.
Negative controls detect truncation, typed invalid enum reads in isolated
sanitizer processes, and mixed C/C++ descriptor layouts before decode. The
unchanged dedicated mock transaction harness passes all ten cases per mode.

The companion JSON records each of the nine code/proof-source blobs, immutable
schema/decoder/build input hashes, compiler versions, ABI flags and exact output.
The two report files are excluded from their own blob inventory; the later
Git raw inventory independently binds all eleven committed files.
