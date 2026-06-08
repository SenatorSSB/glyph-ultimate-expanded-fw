# Official Configurator Manual Import/Export Test Plan

Status: `MANUAL_TEST_PLAN_ONLY_NOT_A_RESULT`

## Purpose

This is a plan-only packet for a later human/operator manual official
configurator import/export check. It does not record a result and does not
claim that the generated preview is importable, exportable, or compatible.

## Candidate Artifact

- candidate preview artifact:
  `docs/export/fixtures/generated_official_configurator_candidate_preview.json`
- candidate preview hash:
  `UNKNOWN_TO_BE_FILLED_AFTER_OPERATOR_SELECTS_ARTIFACT`

## Operator Fields To Fill Later

- official configurator app/version:
  `UNKNOWN_TO_BE_FILLED_BY_OPERATOR`
- operator:
  `UNKNOWN_TO_BE_FILLED_BY_OPERATOR`
- import route:
  `UNKNOWN_TO_BE_FILLED_BY_OPERATOR`
- export/back-and-forth route:
  `UNKNOWN_TO_BE_FILLED_BY_OPERATOR`
- input artifact path:
  `UNKNOWN_TO_BE_FILLED_BY_OPERATOR`
- input artifact hash:
  `UNKNOWN_TO_BE_FILLED_BY_OPERATOR`
- output artifact path:
  `UNKNOWN_TO_BE_FILLED_BY_OPERATOR`
- output artifact hash:
  `UNKNOWN_TO_BE_FILLED_BY_OPERATOR`

## Post-Capture Comparison

After a future capture exists, run:

```bash
python3 tools/check_glyph_official_configurator_export_candidate_diff.py
```

A future result-specific checker may be added only after the captured output
artifact exists and is reviewed.

## Pass/Fail Criteria For Future Result Packet

- pass only if the operator records app/version, route, input artifact path and
  hash, output artifact path and hash, and a reviewer inspects the diff;
- fail if import is rejected, export is unavailable, hashes are missing, output
  cannot be parsed as JSON, or unsupported claims would be required;
- inconclusive if any required operator field remains unknown.

## Explicit Non-Claims

- no device write
- no WebSerial
- no runtime-loaded config
- no firmware flashing automation
- no hardware behavior validation
- no official compatibility claim until a result is recorded and inspected
- no nunchuk validation

This packet explicitly does not record a result.
