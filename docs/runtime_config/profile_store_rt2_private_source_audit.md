# Private DCD source/build integration audit

Scope: repository-owned diagnostic-only pinned RP2040 TinyUSB 0.16 TU. No installed package changes, endpoint repair, workaround enablement, status rescan, device action, canonical action or Git mutation performed by this specialist. Runtime actual status/clock/cause remains UNKNOWN/UNPROVEN absent hardware evidence.

## Source custody

- Original absolute source: `/Users/rasmus.pekkarinen/.platformio/packages/framework-arduinopico/libraries/Adafruit_TinyUSB_Arduino/src/portable/raspberrypi/rp2040/dcd_rp2040.c`
- Original SHA-256: `92a74cc04eef498a9523b3980c4b6b704990bff40531e23bb7ca490dd3358b12`
- Pristine repository copy: `vendor/diagnostics/tinyusb-0.16.0/rp2040/dcd_rp2040.c`
- Pristine SHA-256: `92a74cc04eef498a9523b3980c4b6b704990bff40531e23bb7ca490dd3358b12`
- Original/copied length: 18095 bytes, CRLF retained, original MIT copyright/permission notice unchanged.
- Deterministic patched candidate path: `.pio/rt2-private-dcd/dcd_rp2040.c`
- Patched SHA-256: `88e5af8b24e18895bceba246f7759b66bd7eaa6352b49fd03b02b43a9f9b1d77`
- Patched length: 18971 bytes (+876).

## Exact intentional deltas

One include of `core/RecoveryPrivateDcdMarkers.h`, thirteen direct C marker calls; all other source bytes identical. Removing those fourteen inserted lines reproduces the pinned pristine SHA-256 exactly. The source checker also regenerates the patch to enforce positions/arguments, not merely an inverse-strip hash. Includes/defines are not altered. E5/E15/E16 workaround configuration is not enabled. The original one `usb_hw->ints` read, status local, SOF→BUFF_STATUS→SETUP→later branch order, pointer declaration, PID reset, event call, clear, endpoint paths and panic paths remain byte-identical after removal.

Marker order/numeric IDs: ENTRY0 first statement; STATUS1 immediately after original local status read, passing `status`; SOF_DONE2 inside SOF after dcd_event_sof; BUFF_DONE3 inside BUFF_STATUS after hw_handle_buff_status; SETUP_TEST4 evaluates actual local status mask as boolean before original branch; SETUP_ENTERED5 first statement inside original branch; SETUP_POINTER_ACQUIRED6 after original setup pointer declaration; PID_DONE7 after original reset_ep0_pid call; BEFORE_EVENT8; AFTER_EVENT9; BEFORE_CLEAR10; AFTER_CLEAR11; RETURN12 just before original normal function end. Non-status/test values are literal zero. A pointer-acquisition marker does not establish DPRAM payload copy; that copy remains inside original inline event construction.

## Build routing

`builder_scripts/rt2_private_dcd.py` acts only when strict candidate define equals1. It checks both installed bytes and repository pristine pin immediately, generates a deterministic candidate TU under `.pio`, then installs a PlatformIO source middleware. At the exact resolved installed source node it returns SCons NodeList containing one explicit private object built by a clone of the actual library environment. It appends only the original RP2040 source-parent include path (required for quoted rp2040_usb.h). The source node is replaced, not added. Duplicate callbacks raise; before final ELF link, missing/duplicate routing raises and source pins are rechecked. The actual link dependency graph must contain exactly the expected private DCD object and no other original DCD object; missing candidate/extra original objects stop before link.

Active private object: `$BUILD_DIR/rt2-private-dcd/dcd_rp2040.c.o`. The object compile preaction records the actual full compiler command to `$BUILD_DIR/rt2-private-dcd/compile-command.json`. Final map is `$BUILD_DIR/firmware.map`.

`tools/rt2_private_dcd_assembly.py` reads the actual command and compiles only pristine comparison TU by swapping the source and output arguments. All compiler/architecture/optimization/define/include flags remain identical. It emits frozen-original, patched-object and final-ELF disassembly, and requires exactly one private handler defined in final ELF and exactly one DCD object path in final map, all under rt2-private-dcd. Structural assembly review is explicitly REQUIRED_SEPARATELY until performed against those outputs. Initial source readiness does not establish final-link or hardware acceptance.

## Focused controls

`python3 tools/check_glyph_rt2_private_integration.py`: PASS. Deterministic transform/inverse source custody; thirteen separate missing-marker controls; sixteen other controls (changed pristine pin, invented MMIO snapshot, endpoint mutation, nonzero marker argument, constant SETUP-test, displaced entry, missing marker header, changed installed pin, missing/duplicate source replacement, original-object-present, unexpected source path, duplicate real middleware call, real-preaction missing private object and foreign original object, bare object File re-compilation rejection). The actual pre-script middleware is exercised with an isolated mock graph; a distinct unmodified source node survives, original DCD source node is replaced by candidate object. The mock graph is not substituted for final real ELF/map proof.

## Perturbation and residuals

Every direct marker call adds call/return overhead, register pressure and observer stores. The actual count depends on branches:4 markers for no SOF/BUFF/SETUP on normal return;11 for SETUP-only normal return;12 with either SOF or BUFF;13 with both. ENTRY/STATUS/SETUP_TEST/RETURN are unconditional along normal flow. SETUP has7 more boundaries. No timing/frequency measurement is claimed from source alone. Compile-time/disassembly instruction deltas and runtime hardware latency remain separate. Source guard proves insertion-only original source semantics, not absence of latency effects, corruption, missing downstream runtime evidence or interrupt scheduling effects. Host fixtures can test source-grounded flow but cannot establish physical causality.

## Owned tracked paths

- builder_scripts/rt2_private_dcd.py
- tools/rt2_private_dcd.py
- tools/check_glyph_rt2_private_integration.py
- tools/rt2_private_dcd_assembly.py
- vendor/diagnostics/tinyusb-0.16.0/rp2040/dcd_rp2040.c

The main agent owns config registration, build, schema/docs, final custody and publication; observer agent owns marker header/runtime and source-faithful host harness. No edits outside owned paths except this ignored audit.

## Real PlatformIO graph correction and verification

Initial preliminary compiledb FAILED: middleware returned the bare `.o` File extracted from `env.Object(...)[0]`; installed PlatformIO piobuild.BuildSources line377 invokes env.Object again on FS.File middleware results, which cannot compile `.o`. The initial mock did not model that branch, so its apparent integration-readiness result was insufficient and is superseded. The failure is preserved in root's preliminary-compiledb.log.

Correction: return the complete SCons NodeList from `private_env.Object(...)`, which actual BuildSources passes through because it is not FS.File; SCons accepts/flattens these builder result lists normally. The focused mock now exactly models this BuildSources dispatch and explicitly fails on the former bare-object result.

Actual corrected `pio run -e glyph_mk6 -t compiledb` PASS,32.88s, log corrected-compiledb-network-enabled.log. Default attempt's sandbox cache-write failure is separately preserved in corrected-compiledb.log; the permitted escalated retry only allowed normal PlatformIO cache/metadata access. No installed source modifications. Database inspected: exactly one dcd_rp2040.c input, `.pio/rt2-private-dcd/dcd_rp2040.c`, output `.pio/build/glyph_mk6/rt2-private-dcd/dcd_rp2040.c.o`. Actual compile args contain original rp2040 parent include and inherited target C17/O3/Thumb/M0+ flags and strict defines.

Five tracked integration paths re-frozen after this realgraphPASS. Patched TU bytes/hash unchanged. Actual object compilation/link/map/ELF inspection still pending root final build; compiledb does not prove target compilation or final uniqueness.
