# GP-CONFIG-022 owner Config compatibility

Status: preparation only. No device or Config write is authorized.

The verified owner directive `01a11b4c-0621-74d2-9651-0ea861c45e57` approves one bounded repair: RGB block 11 retains its eleven initialized mappings, removes its nine counted empty records, and explicitly sets LF1 to black (color 0). All other fields, mappings, colors, profiles, names, defaults and backend settings must remain unchanged. Firmware applies no automatic migration.

## Before the hardware stage

Use archived owner bytes only for host characterization. They do not establish the current stored Config or replace a fresh backup. The archived original is 4201 bytes, SHA-256 `f589317b59b3ab7543cad563e2e0877dc5f491227e6e35777bc732d402bb1480`; its corresponding block has the expected nine empty tail records.

The offline helper is `tools/prepare_glyph_gp_config022_compatibility.py`. It has no device transport, port option or write operation. It uses the existing protobuf Python generator with the authenticated schema and invokes the exact candidate's host validator. Its new output directory contains review artifacts only.

The helper requires the exact candidate checkout, full candidate Git SHA, original backup wrapper, host-validator proof record, and `archived` or `fresh-owner` provenance label. The label alone does not prove freshness. The independent reviewer must authenticate the actual acquisition and source/build evidence.

Before owner use, require:

1. Fresh raw Config backup through the owner's already established safe manual GET/read workflow, using a separately authenticated operator environment. Preserve its complete backup wrapper, raw bytes, byte count and SHA-256. Keep earlier build and owner-session environments frozen.
2. Exact original raw decode/reencode and JSON restoration equality under the authenticated schema. Unknown fields, noncanonical bytes that cannot roundtrip exactly, or disagreement between the backup's JSON and raw payload stop preparation.
3. Exact identification of block 11: twenty records, the eleven approved named targets in source order, followed by nine empty zero-target/zero-color records. Any different structure requires review before correction.
4. Minimal correction: remove only the nine tail records and explicitly set retained LF1 color to 0. Preserve the other ten retained colors and every unrelated field. Protobuf omits zero scalar values on the wire; the corrected JSON artifact explicitly states `color: 0`.
5. Actual exact-candidate validation: original decodes and receives the expected RGB-target rejection; the corrected payload passes. Preserve the validator binary hash, compile command and complete project dependency/source hashes. Bind them to the exact committed candidate; a generic protobuf encoder does not establish firmware acceptance.
6. Complete structural and raw-byte diffs, the full block-11 before/after table, exact original restoration artifact, and byte-exact restoration re-encoding.
7. Fresh independent review of this complete packet. Stop on any unrelated change, wrong candidate/schema, incomplete source closure, unexpected rejection, unknown signature or restoration mismatch.

The ordinary owner-operated writer remains a separate existing capability. This helper does not invoke it or authorize its use.

## Required packet

| Section | Required facts |
| --- | --- |
| ORIGINAL | Fresh raw path, byte count, SHA-256, acquisition provenance, original artifact and exact codec roundtrip |
| CORRECTED | Artifact path/hash, encoded raw path/count/hash, exact candidate/schema/validator proof, all eleven retained targets and nine removed records, complete semantic/raw diff |
| RESTORATION | Original artifact path/hash, expected restored raw count/hash and exact restoration roundtrip |
| REVIEW | Independent reviewer, exact packet/artifact/source identities, findings and approval; no physical PASS inferred |

The generated `packet.json` indexes `original.raw`, `original.json`, `corrected.raw`, `corrected.json`, `restoration.json`, `before-after-block11.json`, `semantic-diff.json` and `raw-diff.txt`. Until independent review it is marked `REQUIRED_BEFORE_OWNER_USE`. A failed preparation is not an approved packet.

## Later manual hardware sequence

The final hardware protocol must bind exact committed F, its preserved UF2 and SHA-256, source/build/custody review, and the accepted rollback artifact. Give one dependent owner action at a time.

First establish the existing accepted-firmware baseline and fresh backup. An unchanged original with the identified legacy RGB defect can supply the safely reviewed persisted-rejection observation: C022 must refuse operation, retain the stored bytes, and repeat refusal after reboot. Do not assume Configurator recovery is reachable during refusal. Recovery uses the owner's established pre-load MB1/ROM BOOTSEL path and exact accepted rollback, followed by raw readback comparison.

Before any corrected Config is stored, obtain separate explicit owner authorization for that exact reviewed compatibility artifact and the existing manual write/recovery route. Require explicit success, complete raw-byte equality and a repeat readback after reboot. No executor device or Config write follows from this document.

The normal C022 physical gate includes ordinary gameplay, active and disabled/unassigned physical-button lighting, static/dynamic paths and supported GC/USB sanity. In that same gate, observe the complete corrected block-11 appearance as one grouped matrix:

| Target | Approved source-default appearance |
| --- | --- |
| LF1 | Black, color 0 |
| LF2, LF3, LT1, RF1, RF2, RF5, RF6, RT1, MB1, LF5 | Each retains `#22D3EE` / 2282478 |

Use an existing source-supported profile that references block 11, identified from the fresh Config and exact source. Do not change unrelated RGB references or add profiles to create a test route. If retained owner colors differ from source defaults, the reviewed packet must state their actual unchanged values. A fresh route or substantive discrepancy stops for review.

The pre-fix LF1 appearance is source-inferred. No historical physical proof or separate preliminary appearance campaign is required. Acceptance asks whether the corrected candidate produces the approved appearance, including LF1 black, while ordinary gameplay remains correct.

Original restoration requires the accepted rollback firmware because the legacy zero-target Config is intentionally rejected by C022. Restore only through the separately authorized existing manual workflow; require exact original raw count/hash immediately and after reboot, plus ordinary gameplay and clean release. Preserve every anomaly and failed result.

Nunchuk remains NOT_TESTED. Root cause remains UNPROVEN. Host proof, codec equality and a successful build are separate from exact human hardware acceptance.
