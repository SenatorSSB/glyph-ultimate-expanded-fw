# G11m Prototype Test Strategy

Status: docs-only

## 1. Current test reality

- No lightweight, repo-local unit-test convention is currently established for these prototype helpers.
- Quiet firmware build is the current verification baseline.
- The prototype self-test helper provides compile-visible deterministic vectors.

## 2. Near-term test strategy

- Keep the self-test helper compile-visible.
- Add deterministic self-test cases as pure helper code when useful.
- Use build success as compile/integration verification for prototype helper changes.
- Introduce a local harness only after a repo-level convention is explicitly chosen.

## 3. Future options

- Native C++ host-side test target.
- PlatformIO native environment.
- Firmware-internal debug self-test pathway.
- External script-based helper compilation checks.
- Defer framework choice until selected runtime behavior exists.

## 4. Recommendation

- Do not add dependencies in this batch.
- Continue expanding compile-visible deterministic helper self-tests.
- Choose a test framework either immediately before or immediately after the first selected-mode runtime behavior, not during this batch.
