# GP-CONFIG-014 hardware protocol

Protocol version: `GP_CONFIG_014_HW_V1`

Status: `HARDWARE_TEST_REQUIRED`. No physical observations have been recorded.

## Exact handoff identity

- Candidate branch: `codex/gp-config-014-built-f`
- Candidate Git SHA: `e5c455637056ac535347c1176dd41c9a9d84d85a`
- Candidate tree: `5459271c2219e021414eda37c9155c5ea7a983cf`
- Sole parent / authorized canonical base: `3369819a34f82d579e21adff125a25de854f1b9b`
- UF2 SHA-256: `9ea39ed952c9f08d7134b8527ed93e37edcd09482fd198c5be2ae59f3c80e8af`
- Preserved locator: `local_backups/hardware-artifacts/e5c455637056ac535347c1176dd41c9a9d84d85a/9ea39ed952c9f08d7134b8527ed93e37edcd09482fd198c5be2ae59f3c80e8af/firmware.uf2`
- Fresh independent postimplementation review: PASS with no findings for the exact candidate, build output, custody bytes, correspondence, and protocol.
- Build output: `.pio/build/glyph_mk6/firmware.uf2`
- UF2 size: `796672` bytes
- Build: PASS using the authorized fallback `./scripts/build-glyph-mk6-quiet.sh`; RAM:   [===       ]  30.1% (used 78960 bytes from 262144 bytes); Flash: [==        ]  24.6% (used 386056 bytes from 1568768 bytes)

F is the committed-before-build sole child of composition merge M above.
M has source-free strict GP-VAL-034 DONE `62b559ae5ee2d6dee0ff54aeb56b2653d86253c6`
as its first parent and preserved C014 `a3664be5354ec4253122eb2e738e70e5dfdb9ccc`
as its second parent. F changes exactly the two authorized CustomControllerMode
source paths from that source-free base. Its complete 236-entry critical
source/build tree equals preserved C014. All governance and 97 queue objects
remain equal to the strict-DONE base. No C014 source enters canonical before
independent processing of exact human hardware PASS.

## Scope and evidence boundaries

The repair expands the modifier cache to the generated extent 20, initializes
its pointer/cache and refuses impossible counts at the authorized boundaries.
Valid 0..20 modifier masks, ordering, combos, priorities and arithmetic are
preserved. Host proof covers 0/10/11/20 and impossible 21/oversized counts under
both enum ABIs. Invalid count submission is HOST_ONLY / physical NOT_TESTED.
No same-session rebind coherence or digital-live21 claim is made.

Physical scope is the owner's actual Mk6 GameCube and ordinary supported USB
contexts. Record actual controller model/revision, backend, host and adapter.
No untested platform, official Configurator compatibility or gameplay semantics
are inferred. Nunchuk remains NOT_TESTED; root cause remains unproven.

Give one physical action at a time and wait for its observation. The tables
below organize evidence; they are not batch instructions. A crash, wrong
identity, stuck input, unexpected output/disconnect, unsafe route or failed
restoration stops testing. Preserve unexpected bytes and observations. A build,
host proof or synthetic checker record does not establish controller acceptance.

## First physical action

With the controller still on its existing accepted firmware, connect it once in
its normal gameplay mode. Report model/revision, backend and host/adapter,
whether startup reaches the normal dashboard/profile, and any anomaly.
Do not change firmware or Config yet. Wait for this report before the next step.

## Preconditions before changing firmware or Config

1. Finish the normal accepted firmware baseline observation and resolve any anomaly.
2. Freeze exact 014 F, build, reviewed protocol and preserved artifact after strict 034 DONE.
3. Keep the root-verified accepted C020 rollback F=7db4f447d5e796367071b7143fa6c9274c70ae5e, UF2 SHA256=7743fcbe3d71ec4159e6da5026a1b4560cbbef4d1654cb80b8907fcce344b500 available; verify custody at handoff. No 020 retest.
4. Do not load or activate 11/20 modifier test profiles on the accepted C020 firmware with its old ten-slot cache. The owner must first manually install the verified exact C014 UF2 under the frozen protocol; all capacity rows bind that exact F/artifact.
5. Use the owner-selected actual port and existing Configurator, gameplay and recovery routes.
6. Capture the complete current owner Config. GET_CONFIG supplies stored bytes, not live RAM. Preserve raw bytes, size, hash and extracted JSON. Require byte-exact decode/re-encode before any change.
7. Require the unchanged original artifact and all temporary artifacts to pass the existing dry-run guard. Never relax the guard.
8. Authenticate the actual resolved .pio schema/options/generated ABI against exact F and the tracked dependency closure.
9. Inspect available profiles, custom-mode capacity, actual bindings and backend visibility. Do not assume four spare slots or that required counts already exist.
10. Derive minimal temporary profile edits from the fresh owner Config, preserve the entire original and unchanged Ultimate profile, validate all counts, named bindings, references, ranges and finite bounded arithmetic offline. Review exact artifacts and manual commands before owner use.
11. After each authorized manual write, obtain independent raw readback, then owner reboot before gameplay. After restoration, compare raw bytes immediately and again after owner reboot. Stop on any mismatch.

The historical owner Config is reference evidence only. Fresh current Config,
actual port, profile bindings, expected outputs and concrete temporary artifacts
are WAITING_FOR_OWNER_INPUT. The first action above is safely executable;
subsequent mutation remains gated on the preservation and validation below.
Missing objective inputs never authorize guessing a profile or disabling a guard.

### Existing manual tooling and concrete artifact review

Use the existing generic tool on the owner-selected actual port. Its backup
wrapper is not a write artifact: extract only its `config` object after proving
complete raw decode/re-encode equality. GET_CONFIG supplies stored bytes,
not live RAM. Authenticate the actual `.pio` schema/options/generated ABI
against this exact F's resolved closure before interpreting or encoding bytes.

Run the existing tool from the exact F checkout with its isolated Python and
authenticated `.pio` dependencies. Before use, directly verify its tracked bytes
and resolved schema; an arbitrary checkout or fallback schema supplies no authority.
Existing operator command shapes (supply actual paths and port):

```text
.venv/bin/python tools/glyph_serial_config_tool.py --read --port <port> --backup-out <pre.json>
.venv/bin/python tools/glyph_serial_config_tool.py --dry-run --artifact <extracted-original-config.json>
.venv/bin/python tools/glyph_serial_config_tool.py --dry-run --artifact <reviewed-valid-test-config.json>
.venv/bin/python tools/glyph_serial_config_tool.py --write --artifact <reviewed-valid-test-config.json> --port <port> --backup-out <fresh-prewrite.json>
.venv/bin/python tools/glyph_serial_config_tool.py --read --port <port> --backup-out <post.json>
```

These are existing manual operator operations. No agent device-write or flashing
automation is authorized. Do not repurpose specialized005/010 tools or add a
writer. The existing Ultimate binding guard must pass unchanged for original
and temporary artifacts. A dry-run does not prove nanopb limits or restoration:
independently validate every populated count, named button, one-based profile
reference, string length, range and finite bounded modifier arithmetic against
actual F/source/schema. Preserve the complete original and unchanged Ultimate
profile. Inspect available slots rather than assuming space for four profiles.

Each concrete valid 0/10/11/20 artifact and its source-derived expected output
must receive independent review before submission. Count 10 must exercise entry 9,
count 11 entry 10, count 20 entry 19; storing/displaying a profile is insufficient.
Derive actual press combinations from fresh bindings and modifier order so the
intended high entry is observable. If overlap or another earlier modifier masks
it, use a separately reviewed minimal valid artifact. Never invent coordinates.

Never load or activate count 11/20 on accepted C020's ten-slot firmware.
Only after complete original preservation, exact rollback custody and a safe
restoration route are verified may the owner manually install this exact C014
UF2. Immediately before that action, re-hash the owner-held preserved bytes
with the native custody tool and match the exact F/artifact pair. Run that
custody verifier from the owner checkout, where the approved locator lives
and exact F must be an available Git commit. Do not
substitute a rebuild or mutable `.pio` output.

After each authorized manual valid write, independently capture complete raw
readback and compare with its reviewed encoded bytes. Then give one owner
reboot action before gameplay. Reboot between Config/profile changes under
GLYPH-UD-025. No same-session custom-mode replacement semantics are tested.

## Required observations on the exact candidate

| Row | Separate staged action | Required observation |
| --- | --- | --- |
| modifier_0 | Select the reviewed MODE_CUSTOM profile containing exactly 0 modifiers after Config validation and owner reboot. Record actual profile/index/backend, ordinary controls, relevant press/release and clean neutral. | For zero, confirm ordinary custom outputs without modifiers. |
| modifier_10 | Select the reviewed MODE_CUSTOM profile containing exactly 10 modifiers after Config validation and owner reboot. Record actual profile/index/backend, ordinary controls, relevant press/release and clean neutral. | Exercise a reviewed binding that reaches cache entry 9; loading or displaying the profile does not prove high-entry activation. |
| modifier_11 | Select the reviewed MODE_CUSTOM profile containing exactly 11 modifiers after Config validation and owner reboot. Record actual profile/index/backend, ordinary controls, relevant press/release and clean neutral. | Exercise a reviewed binding that reaches cache entry 10; loading or displaying the profile does not prove high-entry activation. |
| modifier_20 | Select the reviewed MODE_CUSTOM profile containing exactly 20 modifiers after Config validation and owner reboot. Record actual profile/index/backend, ordinary controls, relevant press/release and clean neutral. | Exercise a reviewed binding that reaches cache entry 19; loading or displaying the profile does not prove high-entry activation. |
| combos_modifiers | Exercise reviewed individual and combined bindings. Record source-predicted digital combo filtering, relevant modifiers and clean release. | Record actual output against the concrete reviewed artifact and source prediction; no anomaly or stuck input. |
| ultimate_x1 | Select the unchanged owner Ultimate profile. Exercise ordinary controls and the actual X1 binding with releases in required GameCube and ordinary supported USB contexts. Derive outputs from current owner remaps and unchanged tables. | Record actual output against the concrete reviewed artifact and source prediction; no anomaly or stuck input. |
| reconnect_reboot | Owner reconnects and reboots, then repeats representative ordinary/high-entry modifier and neutral checks. Record actual profile/backend/context. | Record actual output against the concrete reviewed artifact and source prediction; no anomaly or stuck input. |
| owner_config_restoration | Restore only the prevalidated byte-exact original Config through the existing generic manual tool if needed. Require explicit write success and independent raw byte/hash equality immediately and after owner reboot. Include menu-induced default-index changes. Verify original normal gameplay and neutral. | Record actual output against the concrete reviewed artifact and source prediction; no anomaly or stuck input. |

For each row record tester/time, actual profile/count, concrete artifact hash,
backend/host, actual press and release, source-derived expected result and actual
observation. Required GameCube and ordinary USB coverage must be recorded;
missing context remains an evidence gap. Initial startup after manual update
must be stable and show the expected short Git identity. Record it separately.

## Exact owner Config restoration and recovery

Menu profile selection can alter the default-index/watchdog override and startup
may save Config. Include those changes in restoration verification. If no Config
change occurred and final raw bytes equal the original, record verified equality.
Otherwise restore only the prevalidated byte-exact original with the existing
generic manual tool. Require explicit success and independent full raw byte/hash
equality immediately, then one owner reboot and another exact raw readback.
Verify original normal gameplay and neutral. A success flag alone is insufficient.

Accepted rollback F020 is `7db4f447d5e796367071b7143fa6c9274c70ae5e`,
UF2 SHA-256 `7743fcbe3d71ec4159e6da5026a1b4560cbbef4d1654cb80b8907fcce344b500`,
796160 bytes under its native owner-held content-addressed locator. Verify it
before mutation. This preserves recovery; no C020 rebuild or physical retest is
required. Use only the owner-controlled existing manual recovery method. Stop
if safe recovery/restoration is unavailable; preserve rejected stored bytes.

## Human report and independent processor handoff

Record exact F and UF2 SHA-256, preserved locator, protocol version, tester,
time, model/revision/backend/host, all eight required row IDs and actual
observations, anomalies, Config pre/post sizes/hashes, restoration and rollback.
Do not mark an omitted required row PASS. Keep hardware result pending until
an independent Hardware Evidence Processor verifies the complete exact human
evidence under `GLYPH_HARDWARE_EVIDENCE_V2`. No source integration or DONE
before that exact-snapshot PASS.

## Source references

- GP-CONFIG-014 native queue scope and immutable planning0118 lines530–549:
  valid 0/10/11/20, combos/modifiers, ordinaryUltimate/X1, reboot and restoration.
- `include/modes/CustomControllerMode.hpp` and
  `src/modes/CustomControllerMode.cpp` at exact F: capacity and mask/order scope.
- `src/core/mode_selection.cpp` lines102–150: MODE_CUSTOM and valid one-based custom reference.
- Authenticated `config.proto`/`config.options`: fixed extents and references.
- `tools/glyph_serial_config_tool.py` lines224–268,279–356,380–393,396–511,
  544–560,594–654: explicit read/dry-run/write, schema loading, guard and readback limits.
- `HAL/pico/src/display/DefaultConfigMenu.cpp` lines272–301 and
  `HAL/pico/src/comms/backend_init.cpp` lines100–119: menu/default override and possible save.
- `src/modes/Ultimate.cpp` lines351–356 and `src/core/InputMode.cpp` lines57–85:
  unchanged X1/input routes, concrete owner remaps required.
- `docs/agent_framework/USER_DIRECTION.md` lines527–533: Config change, reboot, gameplay workflow.
