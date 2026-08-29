# Glyph build-input resolution observations

Status: current observational record; no selector mutation, installation, or
reproducibility claim.

## Purpose

This packet records timestamped, read-only observations for the 42 direct
toolchain, dependency, workflow, and reusable-workflow selectors selected from
the canonical GP-PROV-003 inventory, plus two expressions derived from the
tracked build-device-config workflow in exact inventory order. Source identity
is bound by path, SHA-256, Git blob, and base configurator SHA; the workflow and
metadata blobs are direct dependencies of this packet.

A resolved record means only that the observed full identity was obtained at the
recorded time. Mutable tags, ranges, version lines, unversioned packages,
runners, and selectors without an immutable identity remain bounded unresolved.
The nested reusable-workflow record remains bounded unresolved unless a
permitted upstream commit-tree observation is retained. Every unresolved record
uses the immutable base-source locator for its declaration; the sole resolved
record is the platform commit observed through git ls-remote.

## Non-claims

This packet does not install or resolve dependencies locally, change selectors,
inspect caches, execute workflows or glyph_nuker, build firmware, publish or
accept artifacts, establish reproducibility, infer caller/ownership/permissions,
or make firmware, runtime, device, Nunchuk, root-cause, or gameplay claims.
Unresolved results are bounded to the authoritative locators and methods
recorded in the fixture; they are not proof of global absence.

## Validation

Run:

```bash
python3 tools/check_glyph_build_input_resolution_observations.py
```

The checker is offline-only and verifies exact source-derived selector order,
base ancestry and three-file blob closure, per-record source class and lookup
policy, timestamp/locator/schema/nullability rules, workflow-derived expressions,
and the sole permitted observed external identity.
