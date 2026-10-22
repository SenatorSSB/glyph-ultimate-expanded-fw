# GP-NATIVE-002 implementation checkpoint

Canonical READY adoption47d4f00a751a77f0d4de930c993813209c0998e0 was
independently reviewed and live-read back before source mutation. Source parent
is exact334f; no canonical firmware changes were merged into this lineage.

The original Profile list/rendering/navigation now uses a virtual item accessor
and heap-owned compact targets (up to94 ×8 target bytes on target ABI; actual
allocation and complete linked heap/stack proof still pending). Native metadata
uses stored names, rank and stable32bit IDs; eligible ordinary rows retain their
existing action. Native templates do not appear as generic duplicate entries.
Both base and Glyph menu use the same eligibility policy. Configurator startup
never enumerates directory metadata on core1 while its core0 writer can run.

Native selection posts one atomic32bit ID from menu/core1. The ID remains
occupied while core0 loads durable Config into the existing candidate, reads
one selected body into its otherwise-unused embedded slot, validates a matching
eligible native template and publishes reference plus backend destination with
one checked generation save. Only Saved writes the committed reboot marker.
The selected record is activated by the existing boot path. No body/revision
write or hot activation is performed by selection. Context mismatch/fenced,
read-only, migration, corrupt/missing and publication failures refuse safely.

Evidence in /private/tmp/glyph-native-selector-results (not final sealed build):
- selector.log: production menu/control/rendering/mailbox with current generated
  ABI,0/1/11/20/64 records and actual Persistence.cpp tests; both enum ABIs PASS.
- native-short-with-selector.log/native-default-with-selector.log: full native
  checks and literal NOR/LittleFS A->B->A selector/reference/boot tests PASS;
  original legacy comparisons/oracles retained.
- selection-recovery-repaired.log: PASS after adapting the existing startup-only
  extraction for the new separately tested service call. Initial compile failure
  is retained in selection-recovery.log.
- persistence-regression.log:37 existing actual persistence cases PASS.

Exploratory build chronology: pio absent from PATH; a mistakenly linked old
6.1.19 venv was removed from this isolated worktree, leaving the existing6.2.0
runtime/copy of the exact base dependency cache. Restricted attempts were
inconclusive in dependency setup. Network-enabled fallback reached the required
clean-committed-source diagnostic guard and correctly refused dirty source.
No guard, dependency pin, resource limit or diagnostic flag was changed.

This commit is a source candidate for exact target resource analysis and fresh
independent review. No resource PASS, hardware-ready artifact, device action,
physical acceptance, integration or DONE is claimed. New linked proof must
transfer all140 old routes and31classes and add selector/menu paths under
unchanged caps, including both enum component obligations. One atomic4byte
owner avoids the earlier proposed two-word mailbox's no-short layout overflow;
actual symbol alignment/charge remains to be measured.

Fresh independent source review of cce6e9d96804d25274822297d7cf59f6160c9dbd
found one concrete P2: asynchronous selection left other menu reset actions
reachable while core0 persisted. The repaired DefaultConfigMenu control override
blocks all input while the request remains occupied; repaint remains unchanged.
The dedicated both-ABI host test now retains a pending request while attempting
all top-level actions, verifies zero disconnect/firmware/bootloader calls, and
executes the literal core0 service with actual Persistence for successful,
read-only and uncertain-save cases. Independent repaired-scope review and the
new exact target/resource proof remain required. The cce6 clean build was
interrupted before compilation to make this material source repair; no artifact
or acceptance is attributed to that incomplete attempt.

The old config-menu characterization checker currently stops at the previously
recorded C024 authentication failure before it can evaluate source. This is an
actual FAIL, preserved in menu-historical-checker.log; no historical fixture,
assertion, source fingerprint or framework scope was weakened. Current menu
properties have direct production-body sanitizer tests. Native ABI layout probe
passes both representations; target whole stack remains NOT_MEASURED by that
component probe and requires the separate linked proof.
