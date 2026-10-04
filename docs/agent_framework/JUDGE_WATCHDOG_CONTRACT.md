# Judge Watchdog Contract

Status label: CURRENT.

The judge/watchdog is read-only by default. It returns one verdict and the next
required action.

## Verdicts

Use current Revision 3 GLYPH-UD-027 and VALIDATION_AND_GATES.md. Tier 1 always
blocks; Tier 2 blocks when directly affected; Tier 3 remains honest framework
debt unless a concrete Tier-1/Tier-2 contradiction is identified. A DONE verdict
requires every applicable safety/regression gate, not an automatic global
meta-proof. FAIL/TIMEOUT/incomplete never becomes PASS. No new GP-VAL without
UNPROVEN_SAFETY_FACT; enforce one ordinary plus one exceptional successor and
exact substantive exceptions. Rejected transport is readback debt, not a reason
to restart governance. Hardware/source/review boundaries are not overridden.

- `DONE`: Objective is complete, validation passed, and gates are satisfied.
- `CONTINUE`: A concrete next delta remains and is within scope.
- `BLOCKED`: Work cannot continue without user input, missing source evidence,
  or an external event.
- `NEEDS_HARDWARE`: Active firmware behavior changed or may have changed; build
  proof and hardware PASS are required before merge.
- `UNSAFE`: Scope enters forbidden paths or bypasses source/build/hardware
  authority.
- `LOOPING`: The cycle is spending effort without reducing uncertainty or
  producing a validated delta.

## LOOPING Conditions

Return `LOOPING` when any condition is present:

- Docs/status work continues without blocking justification.
- Checks are repeated without reducing uncertainty.
- Process polish displaces ready product, source, or checker progress.
- The supervisor cannot name a concrete validated delta.
- Two docs-only cycles in a row occur without an objective blocker.

## Required Return Format

```text
Verdict: DONE / CONTINUE / BLOCKED / NEEDS_HARDWARE / UNSAFE / LOOPING
Reasons:
- ...
Required next action:
- ...
Gate notes:
- ...
```
