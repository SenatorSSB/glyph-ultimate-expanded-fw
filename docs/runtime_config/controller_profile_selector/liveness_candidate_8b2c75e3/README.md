# GameCube selector liveness repair — exact candidate

Prepared2026-10-23 (Europe/Helsinki). Source, host regressions, fresh independent
source review, exact Mk6 build, linked resource proof and artifact custody PASS.
**Stage A read-only recovery PASS within API scope; repaired hardware acceptance
remains NOT_TESTED. No flash or source merge.**

Exact candidate `8b2c75e35bb990aee06de3165e5780082c4f08ad`, tree
`cd5d280e3b04a3b4e9d9a1bc760917406175b988`, is published on
`codex/gp-native-002-gc-liveness`. Failed48989519 and its artifacts/evidence stay
unchanged. Canonical failure publication3a7a8174 remains unchanged; this branch
contains only the source-free proposal, with no queue promotion, HEP or DONE.
The later [owner objective](OWNER_OBJECTIVE.md) authorizes the named bounded
repair after the historical failure stop. Device approval remains separate.

- [Completed Stage A recovery and limits](recovery_20261023/SUMMARY.md).
- [Owner approval packet](OWNER_PACKET.md): Stage A read-only recovery first;
  Stage B exact installation/physical test requires its own explicit approval.
- [Read-only recovery/preflight](RECOVERY_PREFLIGHT.md): current unit, Config,
  identity where supported, all original records and retained fixtures28–47.
- [Exact audit and review chronology](AUDIT.md).
- [Implementation and verification result](RESULT.md).
- [Fresh linked resource proof](resource/REPORT.md), [result](resource/result.json),
  [sealed pins](resource/PINS.json), [compressed object map](resource/manifest.json),
  [independent supervisor arithmetic replay](resource/root_arithmetic.json).
- [Independent final handoff review](evidence/handoff_review.json).
- [Exact source review](evidence/source_review.json), [build/custody](evidence/build_custody.json),
  [dependency identities](evidence/dependency_identities.json),
  [actual259 compilation recipes](evidence/compile_commands.json),
  [actual production composition](evidence/production.json),
  [both-ABI layout](evidence/abi-layout.json), [run telemetry](telemetry.json).

UF2:1046016bytes, SHA256
`ca0bb9e800f196ea2a233c42cb921cfd2fecc80b8a9c285340684f1db38fc760`.
Owner-held content-addressed custody is recorded in build_custody.json;
ELF→BIN exact objcopy and every UF2 block/padding match. No rebuild substitution.

Static198288/199632; core0 conservative2048/2048; core1 composition1060 within
retained1152; layout506/510 within512. All140 old/39 selector/14 newGC routes
fit unchanged limits. New initialized RAM code352bytes; new mutable object
state0bytes; one extra PIO instruction and per-SM marker flags explicitly charged.
Target timing/highwater NOT_MEASURED. Root cause of physical failure UNPROVEN.
Nunchuk NOT_TESTED.
