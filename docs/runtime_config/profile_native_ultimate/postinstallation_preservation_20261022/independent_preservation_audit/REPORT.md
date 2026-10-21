# Exact postinstallation original-preservation data audit

Result: **PASS — original Config, all22 decoded profile wrappers, directory metadata, immutable custody and approved request counts match the retained evidence.** This is a finite offline audit of newly completed physical read results. It is not another source-review layer, a controller read or a native hardware acceptance result.

The associated held candidate is F `334fbd06e4541c120b0db423e5be7e112eb1f6f6`, UF2 SHA `41305f260d42e8206bf4a2fb06c88912416e49cd8a68bc13ce3d3c7605306982`. The audit performed zero live device queries, serial lookups/opens/requests or mutations. It did not run a production CLI, build firmware, modify frozen source or start a test/reviewer campaign. The offline decoder imported only the already reviewed schema/codec/validator; its serial-port constructor was replaced in memory with a rejecting sentinel and was never called.

## Custody and original equality

The new private manifest SHA `e47d58f59688955cd39788317ab30f33c41eeed04fd5794ba62c42c51cb0bb40` binds227 session files. Every size and SHA-256 matches. The actual directory contains exactly those227 files plus the manifest itself. The public hash-reference file SHA `83c9dae88856082328602a22489127b78b302ee844239ff3477a4d37d6cbc5c3` contains exactly the same file metadata and manifest SHA; it exposes no raw original payload or serial data.

The original private manifest remains SHA `f528431ccc4e23efdfe5fe19056a7cd2056bdfb458765c870a4db18a52d6fb3d`. All251 of its recorded original files were independently rehashed at their correct preflight-parent root and match. This includes every original canonical wrapper and original Config comparison input. No original content was rewritten.

The postinstallation Config API payload is252 bytes, SHA `54fda3988c30e03b653153ec23d0623674da3649492caa75da8aa08fbce6b460`, byte-for-byte equal to the original base64-decoded API payload and new binary custody. Full protobuf decoding and strict saved-JSON reconstruction agree for both the original and postinstallation Config; all four complete decoded messages are equal. This proves Config API content preservation including user fields/references and observed bookkeeping, not raw filesystem export or a byte-level filesystem rollback.

Three complete directory pages at cursors0/8/16 contain8/8/6 entries and next cursors8/16/0. Every entry message, field, revision and order equals the original page. The combined IDs are exactly `[1,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,24]`.

For each of those22 IDs, the received READ identity/revision matches its original directory entry. The complete deterministic decoded profile-wrapper bytes reconstructed from the retained wire response equal both the original canonical file and new postinstallation canonical file exactly. The current bodies are supported legacy1–3 with no native payload. Directory payload metadata and decoded body version remain separate: ID4 retains directory1/body3,3047 bytes/SHA `b8583459651f42bfbb108e4558627ce0a192be89bae229cbb5a74fb0e7dcd8d4`. No version normalization, profile repair or storage-history inference occurred. `audit_facts.json` records all22 IDs/revisions/version pairs/byte lengths/hashes without any raw profile body.

The public aggregate SHA `039ce84ab390d33c72abc075ec362c699e93c6f73897db7242c94d2c2e25a3fa` agrees with the actual private results, original comparisons, per-profile metadata and final counters. The audit derives those facts from the retained files and wire journals, rather than accepting the aggregate PASS flag alone.

## Actual wire journals and bounds

All26 saved production-tool invocations were replayed offline using the exact reviewed validator SHA `670a34e42f7dd910db9e3782b5d23b8eeda9dd96854f6f09639c543a81c3a264` and frozen F schema/codec. Every stderr file is exactly its mirrored normal JSON journal. Process results are rc0/no timeout/no retry with matching stdout/stderr hashes. Every normal event sequence, fixed read-only request, request-wire SHA/length, reconstructed response chunks/rolling SHA/frame/delimiter, full response protobuf and saved JSON corresponds. Complete preflight admission and response checks remain satisfied; no invalid/error/recovery/fault/liveness event is hidden by this audit.

The actual transmit events are exactly STATUS26, LIST3 and READ22:51 ProfileStore transmissions. The one standalone STATUS is the already consumed original explicit request; the other25 STATUS requests are the existing one-per-LIST/READ preflights. No second explicit STATUS command exists. LIST command files are exactly0/8/16, READ command files are exactly the22 approved IDs, and every command receipt binds the expected wrapper, source tool, normal UID502 and no retry. Journal phases are correctly ordered and timestamps show sequential operations. Fresh fences remain incarnation1/store generation172/Config generation1156314366 in all phases.

The corrected child remains SHA `74fdcb1d9a8335f8f8f943da86ccc774337978dd72955211f3939f2fb4c00e3f`; the fixed sequential batch remains SHA `78a162ef3f5ed49eaccde3293bdd5fd4bdd0128cf31a89215bdba9e4c4695253`. The original STATUS wrapper SHA `78ffb25a59d4d8eac0705a0a91fa337dfa617c3bb8cf099e2c1d9f42697cc5e7` is unchanged. No executed request came from the unexecuted child with the earlier module-shadowing defect.

Final recorded counts are menu confirmation1, CDC metadata lookup1, Configurator identity1, Config backup1, STATUS26, LIST3 and READ22. Metadata invocations, report capture attempts, firmware copies, Config/profile writes, target metric requests and Switch/WUP actions are all zero in this B-only session. The current normal Configurator identity agrees with its expected backend8 and zero row/reference/active-profile fields; it does not attest an earlier gameplay session.

## Stops and negative evidence retained

The original host empty-stderr stop remains SHA `b557c22bd15bc3261237dc0a47b57c2276c543780847bac2a68c50a216c917ce`. Its immutable stopped-state snapshot remains SHA `9adf5988757f241981a20891435ca94e1492489db5d28b69f2f84ca669766b47`. The source-grounded offline correction, original error and consumed STATUS1 were preserved; STATUS was not retried. The initial unexecuted361e2fac… child and its corrected final source remain separate evidence.

The prior anchored metadata session manifest remains SHA `221ab6e17094d6197dfe811f24d504c5d457ff05b904affcd8c02edc9b5500e7`, and all seven files still match. Its INCOMPLETE_STOP/zero-report result is not converted to success or retried here. Earlier raw-selection failures remain separate preserved evidence.

The audit's first execution resolved the original251-file manifest against the Configurator-entry directory and stopped on the parent-level approval receipt path. The original manifest is actually rooted at the enclosing preflight directory. The initial auditor and failure record are retained, then the root resolution was corrected with relative-path safety checks. The corrected audit passed. This was a reviewer path error, not missing original evidence or a new device/storage failure; no live action occurred in either execution.

## Final state and claim limits

The actual final session state has `stop=true`, `original_preservation_complete=true`, stage `POSTINSTALL_CONFIG_AND_ALL22_ORIGINAL_PRESERVATION_PASS_STOP`, and exact verified ID lists/counts26/3/22. No additional device action is authorized by this audit. Root remains the sole canonical publisher.

This closes the bounded postinstallation API-preservation readback. It does not prove raw filesystem internals/history, a new native active program, physical native evaluator/engine behavior, target timing/highwater, controller report values, GameCube/Switch outputs, all18/H1–H12, HEP, tested-source integration or strict DONE. The held source/artifact association is custody evidence; Configurator identity is not installed-program byte attestation. No native Config/ProfileStore mutation, report/metadata retry, metrics or physical campaign permission follows from preservation PASS.
