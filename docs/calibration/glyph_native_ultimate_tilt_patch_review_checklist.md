# Glyph Native Ultimate Tilt Patch Review Checklist

Use this checklist while reviewing the behavior-changing runtime branch.
Mark each item with `[x]` only when source-backed and verified.

## 1) Source Diff Scope

- [ ] Diff scope is `src/modes/Ultimate.cpp` only, unless explicit approval documents extra files.
- [ ] No config/proto/profile/schema changes unless explicitly approved.
- [ ] No SOCD behavior/source changes.
- [ ] No button remap semantic changes.

## 2) Behavior Boundaries

- [ ] No macros.
- [ ] No turbo behavior.
- [ ] No timing automation.
- [ ] No push-to-device behavior added.
- [ ] No hidden profile mutation behavior.
- [ ] No C-stick/right-stick/trigger behavior changes unless explicitly approved.

## 3) Numeric Checks

- [ ] Output values are byte-safe (`0..255`).
- [ ] No overflow/wrap reliance.
- [ ] No implicit/undocumented flipper behavior reliance.
- [ ] Neutral-relative vs absolute-byte handling is explicit and unambiguous.
- [ ] Source-provenance exists for all numeric assumptions.

## 4) Existing Behavior Preservation

- [ ] Baseline direction behavior preserved.
- [ ] Existing `ModX` / `ModY` behavior preserved.
- [ ] Shield-aware branches preserved.
- [ ] Extended Up-B angle branches preserved.
- [ ] C-stick ASDI/slideoff branch preserved.
- [ ] D-pad layer behavior preserved.
- [ ] Nunchuk override behavior preserved.
- [ ] Trigger outputs preserved.

## 5) Verification Commands

- [ ] Existing Python checks executed and passed.
- [ ] Native Ultimate scanner executed before/after patch.
- [ ] Snapshot comparison strategy documented and reviewed.
- [ ] Build command executed and passed.
- [ ] Diff helper report captured for scope review.

## 6) Hardware Smoke-Test Checklist Reference

- [ ] Hardware smoke-test checklist document is linked and current.
- [ ] Hardware owner approved the smoke-test plan.
- [ ] Runtime patch branch is not flashed before checklist sign-off.
- [ ] Hardware-owner smoke test is still required before device use; this checklist does not claim hardware testing has happened.
- [ ] No flashing or push-to-device automation was added by the runtime branch.
