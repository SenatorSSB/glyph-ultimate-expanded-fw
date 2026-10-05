# GP-CONFIG-017 hardware protocol

Protocol version: `GP_CONFIG_017_HW_V1`

Status: `HARDWARE_TEST_REQUIRED`. No physical observations are recorded.

## Exact handoff identity

- Candidate branch: `codex/gp-config-017-built-f`
- Candidate Git SHA: `5994f1657e45e0883c6c75468a19be7e3b49a72c`
- Candidate tree: `0404687bb795e78f0f607fbad865369578615cff`
- Sole parent / authorized canonical base: `a7b8758a4d9d353fcfeb0592cc155b4f50f4f358`
- UF2 SHA-256: `e68105ff1fa033308ec9761d87260908a1cd145068e73eb2df516e34ee2e0fe5`
- Preserved locator: `local_backups/hardware-artifacts/5994f1657e45e0883c6c75468a19be7e3b49a72c/e68105ff1fa033308ec9761d87260908a1cd145068e73eb2df516e34ee2e0fe5/firmware.uf2`
- Fresh independent postimplementation review: PASS with no findings for the exact candidate, build output, custody bytes, correspondence, and protocol.
- Build output: `.pio/build/glyph_mk6/firmware.uf2`
- UF2 size: `796672` bytes
- Build: PASS using authorized fallback `./scripts/build-glyph-mk6-quiet.sh`; RAM:   [===       ]  30.1% (used 78960 bytes from 262144 bytes); Flash: [==        ]  24.6% (used 386184 bytes from 1568768 bytes)

F was committed before build as the sole child of composition merge M above.
M has source-free strict035 DONE `ace41056887ec08616a5c67f026880e1b0d8e81a` as first parent and
preserved C017 `478f438804275f3e0c23e6f36bfd26e34aa343bf` as second parent. F and M share
one tree. Relative to that source-free base only
`HAL/pico/include/comms/NeoPixelBackend.hpp` changes; all236critical inputs equal
C017, and all99queue objects remain equal to the source-free base. Canonical
firmware remains accepted014 until independent exact human HEP PASS.

## Actual validation and custody basis

All15 focused checks PASS with full native snapshot MATCH before runtime copying;
independent source witnesses verify all1430 tracked entries,236critical exactC
and99queue exactG. Whole copied .venv/.platformio-home/.pio-libdeps source cache
bytes, modes and symlink targets were pinned before compilation; all19 immutable
decoder source roles and actual resolved21-role include/generation/version proof PASS.
Tracked HEAD/index/live bytes and modes remain exact before/after build. Compiled
ELF contains clean `5994f165`. The preserved UF2 is a regular nonsymlink read-only
file, rehashed after preservation; accepted014 rollback is separately rehashed.
Actual F full aggregate FAIL/AGGREGATE_TIMEOUT with13 recorded outcomes (11PASS,
old034 synthetic fixture FAIL and final-budget setconfig timeout); native final
fingerprint UNAVAILABLE, separate outer fullnative MATCH. Production300/120
deadlines unchanged. An extra root prebuild campaign call rejected an ignored
cache workflow path before compilation; that FAIL is retained as cache applicability
debt, with native build tracked/source integrity and exact cache/decoder proof
providing the final build basis. Postbuild fullnative fingerprint is UNAVAILABLE
at an ignored embedded dependency directory; no postbuild MATCH/fullcampaign
PASS or aggregate PASS is claimed. No reproducibility or physical acceptance claim.

## Scope and evidence boundaries

Only the existing null RGB block moves before `_config->speed`. Time bookkeeping,
nonnull static/SHIFT/XWAVE paths, blank LEDs, brightness zero, show and return
are preserved. Both time ABIs and actual host negatives passed. FastLED host
conversion is synthetic. Physical null reachability remains UNKNOWN, rootcause
UNPROVEN and Nunchuk NOT_TESTED. Do not force a null or invalid configuration.
A successful build or host test does not establish controller acceptance.

Give one dependent physical action at a time and wait for its observation.
Record controller revision, host/adapter/backend, actual firmware and profile.
For actual controller output, use host/game observations; mini-screen indications
alone do not prove output. Existing owner RGB observations remain separate and
unattributed unless direct evidence establishes attribution.

## First physical action

With the controller on its existing accepted firmware, connect it once in normal
gameplay mode. Report model/revision, backend, host/adapter, selected profile,
whether startup reaches its ordinary dashboard, ordinary RGB behavior and any
anomaly. Do not change firmware or Config yet. Wait for this report.

## Preconditions before any firmware or Config change

1. Resolve any accepted-firmware baseline anomaly and establish the owner's
   existing manual gameplay, Config read/restore, firmware update and recovery routes.
2. Keep the exact accepted014 rollback UF2, rehashed at this handoff:
   F `e5c455637056ac535347c1176dd41c9a9d84d85a`, SHA-256
   `9ea39ed952c9f08d7134b8527ed93e37edcd09482fd198c5be2ae59f3c80e8af`,796672bytes.
   Its content-addressed owner locator follows the same custody contract. No rebuild.
3. Capture fresh complete stored owner Config using the existing supported manual
   read route. Preserve original raw bytes, byte count, SHA-256 and decoded JSON.
   Invoke the existing `tools/glyph_serial_config_tool.py` only from exact F
   checkout `/private/tmp/glyph-config017/build`, using its `.venv/bin/python`
   and the authenticated resolved `.pio` schema/generator closure. Keep full F
   identity, source/index integrity and dependency proof exact; another checkout
   or stale schema does not supply this route. The owner-selected established
   Configurator port/read workflow must already be confirmed.
   The supported manual read is `.venv/bin/python tools/glyph_serial_config_tool.py
   --read --port <owner-selected-port> --backup-out <fresh-backup.json>`.
   Preserve the complete backup including rawConfigPayloadBase64, byte count/hash
   and decoded Config. Only after full raw decode/re-encode equality, extract
   the backup's `config` object as the ordinary artifact; never submit the backup
   wrapper as a Config. Validate the original and every proposed temporary
   artifact with unchanged `.venv/bin/python tools/glyph_serial_config_tool.py
   --dry-run --artifact <reviewed-artifact.json>`.
   Dry-run alone does not establish nanopb/source safety. Independently review
   every populated fixed-array count against the actual generated capacity,
   each enum/string/range, button domain, source-defined 1-based profile and RGB
   reference/default index (including legitimate source sentinel rules), and
   finite modifier arithmetic against exact F sources and resolved schema.
   Resolve any failure before menu selection or Config mutation. Do not relax
   a validator, infer valid counts from JSON length alone, or silently reset
   unrelated fields. RGB per-button references and fixed mapping arrays need
   this source-domain check, even when a generic encoder accepts the artifact.
   The existing explicit authorized owner-operated write is
   `.venv/bin/python tools/glyph_serial_config_tool.py --write
   --artifact <reviewed-artifact.json> --port <owner-selected-port>
   --backup-out <fresh-prewrite-backup.json>`.
   Each write requires explicit success and independent stored raw-byte equality
   against its reviewed encoded bytes, then owner reboot before gameplay.
   Independently repeat stored readback after reboot; restoration still requires
   exact original byte count and SHA-256 immediately and after reboot.
   These are existing owner-operated routes, not executor actions or a new writer.
   GET_CONFIG gives stored bytes, not proof of active RAM. Last accepted restoration
   was4201bytes/SHA-256`f589317b59b3ab7543cad563e2e0877dc5f491227e6e35777bc732d402bb1480`;
   that historical value does not replace a fresh backup. Require byte-exact
   decode/re-encode and the original's unchanged dry-run validation before changes.
4. Establish actual valid static, SHIFT and XWAVE profiles and their applicable
   backend,1-based rgb_config references, current global brightness, speed and
   button mappings from fresh decoded owner Config. Record concrete profile/index,
   mode, RGB record/index, names and expected lit/unlit buttons before changing Config.
   `GlyphConfigMenu.cpp` filters by actual backend and chooses existing profiles;
   `DefaultConfigMenu.cpp::SetDefaultMode` records the 1-based selection in
   watchdog scratch state, deliberately disconnects USB and reboots.
   `backend_init.cpp` then applies the override and saves the default mode for
   a non-Configurator backend. Treat menu profile selection as a Config mutation:
   finish this fresh byte-exact backup/restoration gate first, and record the
   resulting default indexes and stored readback. Observe
   that expected transition separately from an unexpected disconnect. Existing menu RGB brightness is an
   ordinary supported setting; it does not add an animation editor. Default source
   `glyph_overrides.hpp` has static entries and does not establish owner dynamic
   profiles. Missing safe dynamic profiles remain a gap. Any proposed temporary
   artifact must be separately reviewed, valid under the unchanged generic manual
   tool, and preserve all unrelated owner fields and byte-exact restoration.
   No new RGB writer, reset, fallback or forced unsupported state is authorized.
5. Derive expected RGB from exact F source: static maps configured button colors;
   dynamic mapped buttons use white-or-higher (`color >=0x00FFFFFF`) eligibility,
   SHIFT starts with shared hue and XWAVE uses source starter hues. Brightness
   uses the stored global setting and hue advance uses elapsed time and speed.
   Do not promise exact photographic colors from the synthetic host conversion.
   Match the accepted-firmware ordinary observations for the same actual valid profiles.
6. Review ordinary accepted Ultimate/X1 remaps and unchanged tables against the
   fresh owner Config. Record binding, physical input, expected digital/analog
   output and clean release in Mk6 GC and ordinary supported USB contexts.
   No new game semantics or untested-platform/official Configurator compatibility claim.
7. Rehash the preserved C017 UF2 immediately before the owner's manual update;
   compare full F/SHA-256/size/locator above. Use those exact bytes, never a rebuild.
   Owner performs the update and every Config write through the established
   manual workflow; this executor performs no device write or flashing automation.

## Required observation rows

Every row records concrete configuration, expected and observed behavior,
PASS/FAIL/PARTIAL and anomalies. These rows organize evidence, not batch actions.

| Row | Owner action after prerequisites | Required observation |
| --- | --- | --- |
| identity | Open About after exact manual update | Explicit expected build prefix `5994f165` confirmation or actual displayed text; do not invent text |
| static RGB | Select the established valid static profile and exercise mapped controls | Existing mapped colors/global brightness; controller controls usable, no unexpected blanking/disconnect |
| dynamic RGB | Select established SHIFT then XWAVE profiles, one at a time; observe several updates | Both supported ordinary animations/global brightness, mapped and excluded buttons; missing safe profile stays a gap |
| mode changes | Switch between established static/dynamic profiles via existing menu | Selected ordinary RGB behavior, usable controls and clean release; record default-index changes |
| reconnect and reboot | Reconnect then normal reboot, one at a time | Reconnect, selected ordinary RGB available and controls usable |
| Ultimate and X1 | Exercise accepted Ultimate controls and actual X1 binding with releases in actual GC and supported USB contexts | Actual host/game digital/analog outputs equal concrete expected values, clean neutral; display alone insufficient |
| owner Config restoration | Restore exact backed-up original through validated manual route; read back immediately then after reboot | Exact original byte count/SHA-256 both times, explicit write success when a write was needed, ordinary original profile usable |

Record naturally observed null transitions and their exact steps separately.
Host null PASS establishes no physical crash or root cause. Required-row failure,
wrong identity, stuck input, unexpected disconnect/output, unsafe route or failed
restoration stops the test. Preserve bytes and observations, use the established
manual accepted014 rollback and Config restoration, and report the result.
Independent HEP decides acceptance only from exact F/UF2 identities and actual
owner observations for all seven required rows with no gaps.
