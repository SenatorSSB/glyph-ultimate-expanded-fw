# Official Configurator Export Target Contract

Status: `OFFLINE_CONTRACT_ONLY`

## Purpose

Define an offline, source-backed target contract for official-configurator-
oriented comparison work.

This contract is intentionally docs/tools only. It stops before production
export, official compatibility claims, device write, WebSerial, runtime-loaded
config, or firmware flashing automation.

## Non-Goals

- no production export output;
- no device write;
- no WebSerial;
- no runtime-loaded config implementation;
- no runtime-config storage implementation;
- no firmware binary/protobuf parser implementation;
- no firmware flashing automation;
- no official configurator compatibility claim;
- no universal compatibility claim;
- no Senscope neutral profile schema change;
- no game-semantic change.

## Allowed Input Classes

- the official Glyph configurator corpus manifest;
- the official Glyph configurator corpus JSON fixtures;
- the official corpus diff packet;
- the official configurator source-authority packet;
- offline preview metadata derived from the above;
- offline negative-corpus and blocker packets that keep the contract closed.

## Allowed Output Preview Classes

- offline preview only JSON metadata fixtures;
- source-backed shape summaries;
- provenance/hash summaries;
- validation reports for offline preview content;
- blocker packets when source authority is insufficient.

## Source-Backed Field Subset

The preview contract may only describe fields and shapes observed in the
official corpus:

- top-level keys:
  `gameModeConfigs`, `communicationBackendConfigs`, `keyboardModes`,
  `rgbConfigs`, `defaultBackendConfig`, `defaultUsbBackendConfig`,
  `rgbBrightness`, `defaultDashboardOption`
- `gameModeConfigs` entries:
  - `applicableBackends`, `buttonRemapping`, `layoutPlate`, `menuButtonIcon`,
    `modeId`, `name`, `rgbConfig`, `socdPairs`
  - keyboard entry shape:
    `applicableBackends`, `keyboardModeConfig`, `layoutPlate`, `modeId`,
    `name`, `rgbConfig`, `socdPairs`
- `communicationBackendConfigs` entry shapes:
  - `backendId`, `defaultModeConfig`
  - `activationBinding`, `backendId`
- `keyboardModes` entry shape:
  - `buttonsToKeycodes`
- `rgbConfigs` entry shape:
  - `animation`, `buttonColors`
- observed scalar defaults:
  - `defaultBackendConfig = 1`
  - `defaultUsbBackendConfig = 1`
  - `rgbBrightness = 255`
  - `defaultDashboardOption = DASHBOARD_MENU_BUTTON_HINTS`

## Required Metadata And Provenance

Any offline preview fixture or validator output must include:

- corpus ID;
- manifest path;
- manifest hash;
- fixture paths;
- fixture hashes;
- source classification;
- explicit unknowns;
- explicit non-claims;
- offline-only labels.

Required source classification for this corpus:

- `primary_official_configurator_corpus`

## Required Hashes

The contract requires the manifest and fixture hashes recorded in the official
corpus manifest to be preserved exactly in preview metadata:

- manifest hash for `docs/calibration/export_corpus/official_glyph_configurator_2026-06-06/manifest.json`
- fixture hash for the default-profiles JSON fixture
- fixture hash for the back-and-forth custom-profile JSON fixture

If any of those hashes are missing or do not match the corpus manifest, the
preview must fail closed and fall back to a blocker packet.

## Observable Boundary

The official corpus is a single top-level JSON object with mode/config families
and scalar defaults. That is the only boundary this contract treats as
observable.

This contract does not assert whether future export output should be
profile-scoped, global, or mixed beyond the observed corpus shape.

## Unsupported Or Unknown Fields

Unknown or unsupported by this contract:

- exact configurator app version;
- exact capture timestamp beyond the manifest date;
- exact push/download route details;
- semantics of the nested values beyond their observed structural roles;
- any field or payload shape not present in the official corpus fixtures;
- any claim that generated output will be accepted by the official configurator
  without separate proof.

## Validation Rules

1. Preview fixtures must carry the `offline_preview_only` label and the
   companion non-production labels:
   `not_production_export`, `not_device_write`, `not_webserial`,
   `not_runtime_loaded_config`, `not_official_compatibility_claim`.
   Those labels mean the preview is not production export, not device write,
   not WebSerial, not runtime-loaded config, and not official compatibility
   claim.
2. Preview fixtures must preserve the official corpus IDs, paths, and hashes.
3. Preview fixtures must preserve the observed top-level key set and the
   observed counts for `gameModeConfigs`, `communicationBackendConfigs`,
   `keyboardModes`, and `rgbConfigs`.
4. Preview fixtures must keep external-remapper evidence quarantined.
5. Preview fixtures must not introduce a production export, official
   compatibility claim, device-write claim, WebSerial claim, runtime-loaded
   config claim, or firmware-flashing claim.
6. If a preview fixture is absent, a blocker packet must explain the missing
   source authority instead of inventing output.

## Invalid Classes

- external-remapper-only evidence promoted as official;
- missing provenance;
- missing fixture hash;
- unknown field claimed as source-backed;
- device-write flag;
- runtime-loaded config claim;
- official compatibility claim;
- universal compatibility claim;
- nunchuk validation claim;
- production export claim.

## Round-Trip Expectations

The official corpus contains a user-provided back-and-forth fixture that is
useful for offline structural comparison.

This contract does **not** claim:

- that generated output is importable by the official configurator;
- that generated output round-trips through the official configurator;
- that compatibility is universal across devices or versions;
- that a production exporter exists.

Any future compatibility check remains offline, source-backed, and
non-authoritative unless separately proven.

## Stop Line Before Production Export

This contract stops before production export output.

No part of this contract may be used to assert:

- production export;
- vendor-specific export claims;
- official configurator compatibility;
- device write;
- WebSerial;
- runtime-loaded config;
- firmware flashing automation.

## Stop Lines

- stop line before official compatibility claims;
- stop line before WebSerial/device-write;
- stop line before runtime-loaded config;
- stop line before flashing automation.

The contract remains offline preview only.

## Explicit Non-Claims

- no production export claim;
- no device write claim;
- no WebSerial claim;
- no runtime-loaded config claim;
- no runtime-config storage claim;
- no firmware binary/protobuf parser claim;
- no firmware flashing automation claim;
- no universal official configurator compatibility claim;
- no nunchuk validation claim;
- no Senscope neutral profile schema change;
- no game-semantic change.
