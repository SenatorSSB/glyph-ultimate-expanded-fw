# Approved Mac preflight — actual access facts

[Result](preflight_result.json), [owner approval](owner_approval.txt), [approval receipt](approval_receipt.json) and [archive](manifest.json) preserve the exact bounded session. One registry inspection found one owner-identified USB XInput target0738/4726 at0x100000. The one capture stopped before interface open, with zero reports: [actual stderr](xinput_capture_stderr.txt), [session-only output](xinput_preflight.jsonl). No retry or fallback occurred. Interface candidate count and failure mechanism are unproven; no OS/driver/firmware/hardware root cause is inferred.

The owner reports WUP-on-Mac unavailable. WUP inspection/capture/init13 counts are all zero. USB Switch was not inspected or captured; no already reachable route was confirmed. No Config/ProfileStore/identity read or write, menu entry, reset or candidate installation occurred. Current firmware remains UNKNOWN; the host source label never attests candidate installation or physical acceptance.

[Independent manual-console finding](../manual_console_review_20261022/REPORT.md) confirms raw WUP on Mac is optional equipment. Manual GC-adapter-to-Switch observations remain relevant; invisible required fields remain gaps. [Known-menu backup-entry packet](../configurator_entry_backup_20261022/ENTRY_PACKET.md) is the next separate owner approval. It includes the menu's real firmware restart and a bounded CDC metadata lookup, while keeping the original read limits and every write/installation/campaign exclusion.

This is host access evidence, not candidate HEP PASS or FAIL. Candidate334f/UF241305/source/resource evidence and all18/H1–H12 remain unchanged. The generic packer qualification describes archival only.
