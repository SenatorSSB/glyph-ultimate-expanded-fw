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
