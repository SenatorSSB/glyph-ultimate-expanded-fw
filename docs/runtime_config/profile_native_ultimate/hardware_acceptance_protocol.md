# Profile-native Ultimate hardware acceptance protocol

Protocol: `GP_NATIVE_001_HW_V1`. Status: proposed acceptance contract for M1
review; not a device packet, device authorization, executed test, or PASS.
Authority: [owner directive](owner_directive_20261020.md), M5–M7 and completion
contract. Existing hardware-evidence/custody contracts and Revision 3 apply.

## Candidate packet and approval gate

Before requesting device action, prepare one independently reviewed packet that
binds the final base/candidate/tree, source review, exact generated descriptors,
Mk6 build RAM/flash, UF2 byte count/SHA-256, preserved content-addressed custody,
controller/backend/host context, exact approved scripts and all input/output
fixtures. Pin its protocol and script/fixture hashes. The packet must supply
concrete source-derived raw coordinates and complete expected OutputState and
backend report observations for each stimulus; table-selection names alone
cannot establish acceptance. No guessed coordinates or backend equivalence.

The owner must approve that concrete packet before flashing or profile mutation.
This protocol does not authorize either action. Do not open a device to improvise
missing fixtures, replace the tested bytes with a rebuild, or widen the packet.
Stop on uncertain writes or any device/candidate/artifact identity mismatch.

## Preservation and restoration preflight

Use only the actual candidate-supported Config/ProfileStore/Configurator paths.
The current source exposes Config read/backup in `glyph_serial_config_tool.py`
and ProfileStore status/list/read in `glyph_profile_store_production_tool.py`.
The final approved packet must bind its exact commands and native-aware scripts;
these source entrypoints do not imply a raw filesystem-export capability.

Capture fresh original Config bytes and checksum, complete available store
directory/identity/revision/payload readbacks, active references, runtime identity
where supported, baseline ordinary controller observations, and known-good
restoration firmware custody. Validate backup readback and custody before any
write. Keep all original profile IDs/payloads untouched during test preparation.
Use distinct test IDs. The packet must explicitly describe cleanup, persistent
monotonic transaction/ID changes, and anything the public interfaces cannot
restore byte-for-byte; never call a logical restoration a raw store snapshot.
Any inability to preserve the original ordinary state stops device mutation.

Verify the source-supported manual restoration and recovery route before the
first change. Preserve the existing RT2 deferral and recovery restrictions;
this protocol does not authorize RT2 investigation or a factory artifact.

## Required observation matrix

The final packet groups inputs into one economical matrix. Source-derived
expected outputs and exact stimulus identities are filled and reviewed at M6.
Every required row is PASS, FAIL, PARTIAL, NOT_TESTED, or another accurately
defined limitation; HOST_ONLY/N/A never becomes physical PASS.

| Row | Required physical observations |
| --- | --- |
| H1 | Baseline ordinary controls, both sticks, neutral, digital buttons/triggers and reconnect on each affected supported route. |
| H2 | Representative X1, X2, Y1, Y2, Tilt1, Tilt2, Tilt3, Mode and both source-supported sublayers; include meaningful singleton/pair/higher-order conflicts selected from the independent correspondence matrix. |
| H3 | All nine direction entries across the packet's representative tables, including non-center neutral and asymmetry; verify full outputs and explicit winning priorities/default behavior. |
| H4 | Genuine remapped SOCD-aware Down plus independent A: Up conflict and release/history sequences under each supported policy; A survives direction cancellation. Include duplicate physical directional sources. |
| H5 | Forced Down plus A through an ordinary table: forced table wins, loses, and optional explicit winner gating; unselected coordinates never leak and independent A persists. |
| H6 | One input activates digital L+R and another case combines a direction with A. Two inputs OR into the same output. Observe actual backend bits and analogue trigger relationships. GameCube L/R are `triggerLDigital`/`triggerRDigital`; `buttonR` is Z. |
| H7 | Historical LT6 compatibility and RF5/RF6/RF7 interactions, relevant RS diagonal/axis effects, null, D-pad and LS-to-D-pad. Apply honest observer limitations to indistinguishable outputs. |
| H8 | Multiple X/Y/Tilt modifier rebindings across eligible physical controls; original slots lose their old intrinsic native functions, while intentional independent bindings still operate. |
| H9 | Create independently complete native profiles with different tables/modifiers/bindings. Switch selected persistent reference by checked commit then reboot/reinitialize, verify persistence, outputs and correct active identity. Host capacity proof covers at least twenty complete profiles; the packet states which physical profiles are sampled. |
| H10 | Actual current-session XInput runtime attestation matches the active native engine/program/payload and bound preprocessing context; stored updates do not falsely attest a new active program before reinitialization. Configurator readback never proves an earlier gameplay session. |
| H11 | Approved negative/recovery observations for invalid or mismatched native selection without legacy-slot fallback; use only independently preflighted, safely reversible stimuli. No ad hoc corrupting write. |
| H12 | Restore original ordinary Config/references and profile payloads, perform approved test-profile cleanup, verify readbacks/checksums and ordinary output after reboot/reconnect. Record every permitted monotonic metadata difference and any anomaly. |

XInput observations do not establish GameCube PASS. The GameCube portion must
record its own applicable output observations; no GameCube runtime-attestation
capability is implied. Nunchuk remains NOT_TESTED unless the owner actually
executes and reports its separately specified physical rows. Keyboard behavior,
unrelated modes and UI systems are outside the chapter.

## Evidence and integration

Keep full expected and observed outputs, context, timestamps, anomalies,
restoration records, and exact candidate/UF2 tuple. A hardware failure preserves
the failed candidate and evidence and requires source-grounded repair authority;
do not iterate blindly or transfer partial acceptance.

After exact human observations, independent HEP validates the candidate-specific
packet, tuple and complete required rows. Preserve source-free R → E → I,
fresh source/integration correspondence and tested-source review. Only the exact
accepted source may integrate. Publish strict DONE separately after verified
live integration and all twelve owner completion criteria. A build, host test,
selection readback or this protocol alone cannot satisfy that contract.
