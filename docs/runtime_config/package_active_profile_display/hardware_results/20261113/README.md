# Display hardware episode: terminal Stage A stop

**INCONCLUSIVE / HARDWARE_TEST_REQUIRED — episode terminal; no retry.**

Exact approved packet `GLYPH-DISPLAY-9E69188D-HW-v1` at
[3cc98ae4](https://github.com/SenatorSSB/glyph-ultimate-expanded-fw/tree/3cc98ae42092ac249d0183919c3ed1091dcd0f13/docs/runtime_config/package_active_profile_display/hardware).
[summary.json](summary.json) binds the complete approved source/packet/artifact tuple,
actual operations, observed values and limitations. The [owner approval](owner-approval.json)
is an external record; frozen packet/proposal bytes remain unchanged.

Stage A issued exactly10 read-only exchanges: one Configurator Runtime Identity,
one protocol3 PACKAGE_STATUS, one GET_CONFIG, four LIST pages and READ IDs1/3/4.
Identity/health, raw Config and all27 directory metadata entries matched admission.
ID4 READ returned OK/revision1 with a valid legacy schema3 raw wrapper, while its
directory payload_version was1. The host orchestration required schema equality
for every READ and stopped at that comparison. That additional all-record equality
was not independently established as a universal firmware invariant. Its suitability
and the observed disagreement remain for inspection; no firmware defect or repair
is selected by this evidence record.

All10 requests and replies were captured and settled. The sole serial session was
closed; no PASS stage result exists. Only raw wrappers1/3 were saved as standalone
files; ID4's exact raw wrapper remains inside its captured response. The remaining24 READs, including native53,
were not attempted. No flash/install, bootloader entry, profile
mutation, reference rewrite, managed activation, retry, reconnect, recovery, rollback
or firmware rebuild occurred. StagesB–E and every new display observation remain
NOT_TESTED. Complete before/after preservation was not reached.

The owner corrected that normal Configurator entry is through the menu, while
confirming the approved heldRT2 entry was used for this Stage A. This report retains
that distinction without changing the approved packet.

Original TX/RX/COBS, intents/transport records, OS/unit admission, private port-owner
checks, exact scripts/host-only tests, owner readiness and close settlement remain
in owner-held private custody. [The inventory](private-originals-inventory.json)
publishes names/sizes/hashes only; raw serial/USB details and profile payloads are
not uploaded. Public branch is source-free relative to canonical d31a5edd; candidate
3cc98ae4 and canonical/configurator are unchanged.

Stop for owner inspection. This episode cannot resume; no repair, retest, source
integration or source-authority promotion is authorized by this result.
