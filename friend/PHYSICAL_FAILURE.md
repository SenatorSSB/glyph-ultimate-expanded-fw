# Owner-reported physical failure — immutable artifact identity

FRIEND_SINGLE_UF2_PROVISIONING: FAIL

Owner reports that the friend flashed the exact packaged UF2 through RPI-RP2
and saw **"Config storage failure"** on first boot. No Config push was reported.

- Failed private source: `8b8d829d79810d5b4597255aabce036c6970d208`
- Failed UF2 size: 800,768 bytes
- Failed UF2 SHA-256: `3f7c074bc92e3683af5aa3525b96e8f5dd75296c247b349da4ad6c5384da1bf8`
- Preserved original package: `../package/` relative to source-worktree.
- Preserved failed artifact: `../package/firmware.uf2` (DO NOT DISTRIBUTE).

The original package, manifest, checksums and original verification evidence
are retained unchanged. Their pre-hardware READY/NOT_TESTED text is historical
and superseded by this failure record. The new repair uses the separate
`../storage-recovery-v2/` directory; it does not replace this failed artifact.

No device mount result, filesystem dump, serial stage log, hardware model or
exact failing operation was supplied. Device root cause remains UNPROVEN.
The screen alone cannot distinguish constructor mount failure from save,
readback, equality, marker, or ordinary stored-load failure. Source-backed
findings and real-library reproductions are recorded in STORAGE_RECOVERY_REPORT.
