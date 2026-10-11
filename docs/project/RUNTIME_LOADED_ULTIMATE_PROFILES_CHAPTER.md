# Runtime-Loaded Ultimate Profiles Chapter Ledger

Status: `STAGE_0_SOURCE_AND_RESOURCE_ANALYSIS`.

## Authority and scope

- Authority: direct owner chapter, “Runtime-Loaded Ultimate Profiles — Persisted
  Coordinates, Routing, Sublayers, Priorities, and Bounded Output Effects”,
  supplied 2026-10-11.
- Canonical base: live `origin/configurator`
  `28ba39da5f517baa40f3dee8d868c9bb583dde4a`, verified 2026-10-11.
- Isolated branch/worktree: managed worktree
  `runtime-loaded-ultimate-profiles`, based on that exact commit.
- This chapter does not use the private friend-firmware package as a baseline
  or source authority.

## Fixed chapter decisions

- Store versioned Ultimate runtime profiles additively in persisted `Config`.
- Bind an Ultimate `GameModeConfig` to a runtime profile by an explicit
  persisted reference, never by display name.
- An absent reference retains the source-owned legacy Ultimate behavior.
- An explicit but invalid or unsupported runtime extension is rejected; it
  never silently falls back to unrelated source-owned modifier values.
- Stage A owns only persisted, validated 9-way coordinate tables while legacy
  role/routing remains in firmware. Stages B and C are gated on Stage-A human
  hardware evidence.
- The runtime vocabulary is finite and declarative: no scripts, macros, turbo,
  timing, loops, or arbitrary expressions.

## Exclusions and safety boundaries

- No Senscope game-semantics ownership, browser UI, official configurator
  compatibility, WebSerial, automatic device writes, or automatic flashing.
- The daemon never writes Config to or flashes a physical controller.
- No active `RuntimeConfigView` replacement, candidate-view publication,
  generated wrapper publication, or RAM-backed active-table publication.
- Nunchuk remains `NOT_TESTED` unless the owner reports a test.

## Stage state

| Stage | State | Evidence / next permissible action |
| --- | --- | --- |
| 0 — schema, resource, source authority | active | Inspect actual proto/codegen, Config limits, persistence and routing; establish a reproducible schema approach and bounded representation. |
| A — persisted coordinates | blocked on Stage 0 | Implement only after the source/resource design is validated; prepare one discriminating hardware packet before Stage B. |
| B — roles, sublayers, priorities | blocked on Gate A PASS | No implementation before exact Stage-A owner hardware PASS. |
| C — bounded output effects | blocked on Gate A PASS | No implementation before Stage-A proof and Stage-B source/host proof. |

## Controls and measurements

- Preserve exact source, build and artifact identities for every hardware-facing
  candidate; no merge to `configurator` before the required human PASS.
- Required resource report: `sizeof(Config)`, static/global RAM, stack
  warnings, flash use, and encoded Config sizes for legacy, one, two and
  maximum profiles.
- Chapter worker model/effort and review identities will be recorded when a
  worker is dispatched or a candidate is produced.

## Known starting facts

- The live remote verification required network-enabled execution and matched
  the owner launch observation.
- The original checkout had unrelated dirty changes; this isolated worktree is
  clean and those files are not part of this chapter.
- The current firmware persists its one `Config` protobuf via LittleFS and
  validates decoded candidates before publication. The current source-owned
  Ultimate runtime tables are legacy behavior, not runtime-loaded profiles.

## Current stop condition

None. Stage-0 investigation is authorized by the owner direction. A concrete
schema reproducibility, resource, source-authority, or architecture
contradiction must be recorded here before requesting an owner decision.
