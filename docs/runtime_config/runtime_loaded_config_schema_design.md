# Runtime-Loaded Config Schema Design

## Purpose

This document describes a design candidate for a future runtime-loaded config
schema for the current `MODE_ULTIMATE` baseline.

It is intentionally design-only. It does not implement runtime-loaded config,
storage, transport, or firmware behavior changes.

## Versioning

The future schema must carry an explicit version so that the firmware can
reject unsupported versions and decide whether a migration path exists.

Versioning is a product and implementation decision, not a runtime shortcut.
If the schema version is not recognized, the firmware must fail closed to the
known-good baseline rather than guessing.

## Allowed Bounded Data

The future schema may own only bounded data that is already source-backed or
can be source-backed later:

- the 27 `StickPoint[9]` table values;
- stable table ids for the 27-table corpus;
- table names;
- source-backed role metadata;
- source-backed provenance;
- versioning metadata;
- hashes and checksums;
- bounded constants that are explicitly source-backed.

If a future constant is not source-backed, it does not belong in this schema.

## Forbidden Semantics

This schema must not own firmware semantics or hidden control flow.

Forbidden capabilities include:

- macros;
- turbo;
- timing automation;
- arbitrary scripting;
- one-shot behavior;
- toggles;
- history-dependent logic;
- evaluator phase-order mutation;
- hidden device-write behavior;
- transport authority;
- hardware validation claims.

## Metadata and Provenance

The schema must carry enough metadata to prove which source-backed baseline it
represents and which source files or fixtures were used to derive it.

At minimum, the design expects:

- source authority references;
- version metadata;
- checksums or hashes where practical;
- provenance for table data and role metadata;
- an explicit note that the payload is not firmware source.

## Validation Rules

Validation must happen before use.

The current design target is to reject, at minimum:

- unknown schema version;
- unknown mode scope;
- missing required tables;
- malformed table points;
- coordinates outside `[0,255]`;
- boolean coordinates;
- unknown role classes;
- unknown priority classes;
- unsupported phase-order mutation;
- arbitrary script text;
- macro, turbo, or timing automation;
- one-shot, toggle, or history-dependent behavior;
- missing source authority;
- hardware validation claims without a hardware-result source;
- nunchuk hardware validation claims without a hardware-result source;
- device-write instructions;
- serial transport payloads;
- embedded firmware patches.

## Fallback Requirements

Any invalid or unsupported runtime-loaded config must fall back to a known-good
baseline.

Fallback must be deterministic and safe. The baseline must be source-backed,
known-good, and validated before it is used as a fallback.

The exact storage and recovery mechanism is intentionally deferred from this
design.

## Migration Requirements

Any future migration path must answer:

- how version transitions are detected;
- which versions may migrate in place;
- which versions must fail closed;
- how unsupported or partial migrations fall back;
- how provenance is preserved across a migration;
- how the known-good baseline is validated after migration.

This document does not choose a migration algorithm.

## Invalid Config Classes

The schema must treat the following classes as invalid inputs:

- macro or timing automation attempts;
- turbo or rapid-fire attempts;
- arbitrary script attempts;
- hidden device-write behavior;
- missing fallback policy;
- out-of-range coordinates;
- missing tables;
- unknown roles without source authority;
- runtime configs that claim nunchuk validation;
- runtime configs that claim WebSerial or device-write authority.

## Compatibility Caveats

This design is not:

- a universal official configurator compatibility claim;
- a Senscope neutral profile schema;
- a device-write transport contract;
- a protobuf or binary wire-format contract;
- a hardware validation result.

If any of those become product decisions later, they require their own approval
and source authority.

## Future Product Decisions

The following decisions remain open and must be resolved before
implementation:

- storage location;
- representation format;
- boot-time validation strategy;
- fallback policy;
- version migration policy;
- maximum config size;
- profile-bound versus global config;
- update or transport path;
- official configurator source authority;
- hardware validation matrix;
- nunchuk handling decision.

## Explicit Implementation Stop Line

This document stops before:

- firmware interpreter implementation;
- storage implementation;
- runtime-loaded config consumption in firmware;
- protobuf or binary serializer/parser implementation;
- WebSerial or device-write implementation;
- flashing automation;
- public release workflow automation.

Any implementation after this stop line must be separately approved and
validated.
