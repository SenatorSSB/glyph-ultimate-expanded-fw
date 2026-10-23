# CPM-HW-1DE243C7-R2-E1 — context numbering only

Status: PREPARED; exact owner approval required before resuming packet execution.

R2 remains byte-exact with SHA-256
762095c8b6ab92d959f0b8ca40ab6ce78e741652044c00fb61c18351215f55d5.
Firmware candidate, UF2, tools, payloads, mutation sequence and all other fences
remain unchanged. No DELETE or CREATE has occurred.

The saved XInput read reports persisted/backend2/requested27/active27/revision1/
schema5/incarnation1, wire context_row3 and the exact ID27 runtime digest.
Firmware include/core/RuntimeIdentity.hpp Observe assigns s.row=i+1. Thus the
zero-based Config index2 is correctly reported as wire row3. The R2 command used
one SAFE_MODE argument for two differently numbered interfaces and stopped.

Amend section5 solely as follows: MODE_INDEX_ZERO_BASED is the actual current
zero-based Config row. IDENTITY_ROW_ONE_BASED must equal MODE_INDEX_ZERO_BASED+1
and the saved runtime wire context_row. For this retained read these are 2 and3.
Do not reinterpret or edit saved identity, Config or source. Reject zero,
out-of-range or any other mapping. Both existing helper audits remain mandatory.

After the owner returns to Configurator, uniquely match the same unit/location,
capture the exact existing R2 safe-ultimate full snapshot with --safe, then run:

```bash
MODE_INDEX_ZERO_BASED=2
IDENTITY_ROW_ONE_BASED=3
test "$IDENTITY_ROW_ONE_BASED" -eq "$((MODE_INDEX_ZERO_BASED + 1))"
"$PY" "$CHECK" compare "$CAPTURE/reference-2-after" "$CAPTURE/safe-ultimate" \
  --kind selection --mode "$MODE_INDEX_ZERO_BASED" --backend 2
"$PY" "$CHECK" identity "$CAPTURE/safe-ultimate" "$CAPTURE/safe-ultimate-identity.json" \
  --mode "$IDENTITY_ROW_ONE_BASED"
```

Require both PASS and no SEL/dangling reference, exact all43 records, unchanged
store generation and token high-water; Config only the actual normal Ultimate/
XInput selection fields. Any other mismatch means STOP. Do not reread identity
to conceal the previous mismatch; retain original raw output and STOP log.

Only then resume the remaining exact R2 steps. Every DELETE remains separately
fenced, receipt-before-send and stop-on-first-deviation; CREATE remains exact
canonical Kazuya with dynamic rank and returned ID. No additional mutation,
activation, gameplay test, flash, firmware change or retry is authorized.

Approval sentence:

I approve CPM-HW-1DE243C7-R2-E1 only: apply the source-proven zero-based Config to one-based identity row conversion, require both safe-selection audits to pass, then resume the remaining approved R2 packet unchanged.
