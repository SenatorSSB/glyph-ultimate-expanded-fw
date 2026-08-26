# Glyph build-input resolution observations

Status: current observational record; no selector mutation, installation, or
reproducibility claim.

## Purpose

This packet records timestamped, read-only observations for the 42 direct
toolchain, dependency, workflow, and reusable-workflow selectors selected from
the canonical GP-PROV-003 inventory, plus two derived build-device-config route
expressions. Source identity is bound by path, SHA-256, Git blob, and base
configurator SHA.

A resolved record means only that the observed full identity was obtained at the
recorded time. Mutable tags, ranges, version lines, unversioned packages,
runners, and selectors without an immutable identity remain bounded unresolved.
The nested reusable-workflow record distinguishes visible source/ref from proof
of live invocation, secrets, permissions, or repository ownership.

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

The checker is offline-only and verifies exact selector correspondence,
source-inventory identity, timestamp/URL/schema/nullability rules, the
visible-source-without-invocation distinction, and the presence of an observed
external identity.
