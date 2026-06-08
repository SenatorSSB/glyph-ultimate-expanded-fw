# Glyph Runtime Config Phase 6/7 Hardware Matrix Template

Status: TEMPLATE_ONLY_NOT_A_RESULT.

This template is for future implementation slices only. It records no hardware
validation and makes no runtime-loaded config, storage, parser, device-write,
flashing, public release, official configurator compatibility, or nunchuk
validation claim.

| Row | Future slice | Planned check | Expected result | Result |
| --- | --- | --- | --- | --- |
| parser compiled payload valid baseline | Slice 7A | Boot firmware with approved compiled/test runtime-config payload | Valid payload activates only after full validation; baseline behavior remains bounded | NOT_RUN |
| parser invalid payload fallback | Slice 7A | Present invalid compiled/test payload | Firmware ignores candidate and preserves source-owned baseline | NOT_RUN |
| wrong version fallback | Slice 7A | Present unsupported version | Firmware ignores candidate and preserves source-owned baseline | NOT_RUN |
| wrong mode fallback | Slice 7A | Present non-`MODE_ULTIMATE` scope | Firmware ignores candidate and preserves source-owned baseline | NOT_RUN |
| wrong checksum fallback | Slice 7A | Present checksum/CRC mismatch | Firmware ignores candidate and preserves source-owned baseline | NOT_RUN |
| duplicate table id fallback | Slice 7A | Present duplicate table ID | Firmware ignores candidate and preserves source-owned baseline | NOT_RUN |
| out-of-range coordinate fallback | Slice 7A | Present coordinate outside accepted bounds | Firmware ignores candidate and preserves source-owned baseline | NOT_RUN |
| missing storage fallback | Slice 7B | Boot without runtime-config storage artifact | Firmware keeps source-owned baseline and performs no hidden write | NOT_RUN |
| corrupt storage fallback | Slice 7B | Boot with corrupt runtime-config storage artifact | Firmware keeps source-owned baseline and performs no hidden write | NOT_RUN |
| read-only storage no-write check | Slice 7B | Exercise storage read-only path | No runtime-config storage mutation occurs | NOT_RUN |
| write path explicit user action check | Slice 7C/8A | Exercise approved write path | Write occurs only through explicit user-visible action | NOT_RUN |
| no hidden write check | Slice 7C/8A | Boot and invalid-candidate paths | No hidden write, auto-delete, auto-rewrite, or flashing occurs | NOT_RUN |
| baseline preservation | Slice 7A/7B/7C/8A | Compare current known-good source-owned baseline behavior | Baseline preserved when candidate absent or invalid | NOT_RUN |
| profile regression | Slice 7A/7B/7C/8A | Exercise existing applicable non-nunchuk profile scope | No regression in recorded applicable scope | NOT_RUN |
| nunchuk NOT_TESTED | Any future slice | Nunchuk scope | Nunchuk remains NOT_TESTED unless separately validated | NOT_TESTED |

## Required Result Packet Fields

- branch and commit;
- build artifact identity;
- payload fixture identity and checksum where applicable;
- device/hardware scope;
- operator/user report;
- pass/fail rows;
- rollback/fallback notes;
- non-claims.
