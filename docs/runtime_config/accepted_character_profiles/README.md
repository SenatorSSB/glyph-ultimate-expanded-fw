# Accepted character profiles — Kazuya v4 and future Pikachu/Kazuya names

The exact v4 source is promoted at [canonical Kazuya](../../../profiles/kazuya/README.md):
**HOST_VERIFIED**, **DEVICE_CREATED_AND_READBACK_VERIFIED**, and
**GAMEPLAY_ACCEPTED (owner-reported)** for ID51/revision1/nameKazTest4. The owner
report was “everything works perfectly and as designed now”. This is contextual
owner acceptance of the exact installed payload, not invented per-case timings.

[Accepted identity](ACCEPTED_KAZUYA.json) binds accepted5e30341e sourceSHA, wrapper/
body/preprocessing/provenance and compile/resource report to sealed historical and
fresh READ51 and the sealed owner gameplay report. [Owner authority](OWNER_AUTHORITY.md)
authorizes canonical adoption and packet preparation, with **zero controller
mutations in this run**. The later approved method correction uses existing
RENAME7 instead of UPDATE, with unchanged profile revisions and ranks.

## Canonical adoption and history

Prior live canonical: `bf6f1e2e6814c6b6f1eb710175a488961c8295e7`. Accepted candidate:
`5e30341ee06761e20e864ccc013ca6658e42b5ca`. The canonical source is byte-exact v4,
including human source name KazTest4, which is separate from store metadata.
[Root migration](ROOT_PATH_MIGRATION.json) preserves former v1 source/README;
all v1–v4 tests/manifests/results and archival Ultimate remain unchanged. Earlier
versioned README statuses describe their historical checkpoints.

The [accepted verifier](../../../tools/check_glyph_accepted_character_profiles.py)
replays immutable history without changing its pins. It validates/compiles/reports
the current canonical source, checks all1102 current production/harness inputs
against5e, executes authoring17/23 and original v1–v4 native6/8/11/11 tests in a
temporary exact Git snapshot, and runs canonical v4 through the current C++ native
preprocessor/SOCD/evaluator with frozen v4 assertions. It seals both source and
input identity again after running. This replaces naive direct execution of old
root-path-pinned tests from a post-promotion checkout; no historical test is relabeled.

```sh
python3 tools/glyph_native_profile_json.py validate profiles/kazuya/Kazuya.profile.json
python3 tools/glyph_native_profile_json.py compile profiles/kazuya/Kazuya.profile.json --output /tmp/Kazuya.accepted.pb
python3 tools/glyph_native_profile_json.py compile profiles/kazuya/Kazuya.profile.json --format protobuf-json --output /tmp/Kazuya.accepted.protobuf.json
python3 tools/glyph_native_profile_json.py report profiles/kazuya/Kazuya.profile.json --output /tmp/Kazuya.accepted.report.json
python3 tools/check_glyph_accepted_character_profiles.py --report /tmp/Kazuya.accepted.validation.json
python3 tools/check_glyph_profile_store_production_tool.py
python3 docs/runtime_config/accepted_character_profiles/test_packet_checks.py
python3 tools/check_glyph_docs_navigation.py
```

Tests need existing jsonschema/grpc/Nanopb/C++ dependencies; no downloads or firmware
build. [Validation](VALIDATION.json), [fresh independent review](INDEPENDENT_REVIEW.json)
and [publication receipt](PUBLICATION_RECEIPT.json) record actual final results and
integration identity. No firmware source/build inputs changed. A profile-source
promotion does not need a new UF2 or additional gameplay campaign.

## Current controller and future operation

[Read-only inventory](CONTROLLER_INVENTORY.md): native27 Ultimate (keep as Pikachu),
48 Kazuya/v1,49 KazTest2/v2,50 KazTest3/v3 (individually proven superseded),51 KazTest4
(keep as Kazuya). All27 current records remain intact, including22 legacy records.
ID51 is currently referenced; candidates48/49/50 are not. [Exact plan](CONTROLLER_PLAN.json)
binds all hashes and lineage; raw Config, USB identity and transaction receipts
stay in the owner's private backup. Fresh execution preflight is mandatory.

The [future owner packet ACP-20261025-01](OWNER_PACKET.md) uses checked metadata-only
RENAME27→Pikachu and51→Kazuya, retaining stable IDs, payloads, ranks0/154 and
revisions1/1. It first requires physical safe return to ID27, then individually
fenced DELETEs of only48/49/50, full readback/preservation and a bounded genuine
owner menu smoke. Final native list is Pikachu/Kazuya; ordinary non-Ultimate modes
are reported separately. Leave ID27 active. [Offline packet checker](packet_checks.py)
never opens a device or transmits operations; the existing production tool exposes
only the approved existing RENAME operation through its normal safeguards.

**Current mutation status:** ID27 renamed NO; ID51 renamed NO; old experiments
deleted NO; ProfileStore mutations NONE; firmware flashed NO. Packet commands
are unexecuted and require a separate explicit owner approval. Final metadata
names are intended, not a claim about the current visible menu.

## Deferred boundaries

Crouch Jab loops remain deferred; no additional sublayers/optimizations or
functionality outside reported gameplay acceptance is promoted. Exact accepted
v4 remains rollback/reference before future experiments. Nunchuk NOT_TESTED;
root cause/game internal timing claims remain unproven. No firmware, payload,
controller architecture or layout redesign occurs in this chapter.
