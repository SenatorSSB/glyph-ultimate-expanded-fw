# Recorded metadata stop and backup-only exception — focused ACK

Result: **PASS — exact recorded evidence and new bounded owner packet correspond; no concrete scope/protocol/safety defect found.** The recorded metadata result remains `INCOMPLETE_STOP`, not a successful enumeration or output capture. The new packet remains `OWNER_APPROVAL_REQUIRED_NOT_EXECUTED`; its owner approval and hardware result are null. This finite review performed no live query, lookup/open/request, reset, write, diagnostic retry, firmware/source change, compilation or new test/reviewer layer.

The reviewed new packet is `GP_NATIVE_001_BACKUP_AFTER_METADATA_STOP_V1`. It explicitly requests owner authority to proceed only with the unchanged known-menu/original-preservation phase B after the recorded metadata stop. It does not inherit continuation authority from the previous Choice A approval. Root's previous stop was required by that packet and has been preserved.

## Exact held inputs and custody

| Input | SHA-256 |
| --- | --- |
| New BACKUP_PACKET.md (3,789 bytes) | `80c4a92a8e4e94e4325feaaad29bad3c2ef8ba6f26dcdd8e3655d21327468229` |
| New BACKUP_PACKET.json (3,256 bytes) | `a864c67394b9d5c857a1489401dcfd387031f9476bced27ea6eca5b33617dd85` |
| Recorded metadata stdout (12,472 bytes;125 JSON records) | `10038e4ab3f82dbe4765f1d531868ef64a96b581c649a32eaaa01069586f0259` |
| Immutable seven-file stopped-session manifest | `221ab6e17094d6197dfe811f24d504c5d457ff05b904affcd8c02edc9b5500e7` |
| Exact held child source | `506011f496ae3e9593f625b5c2635f140da4bc49a1a5566fc94e62397f5d0962` |
| Exact held/live-command binary | `a7323004747c86bd7fada4e3f4e0b9dc9d1ed620bfd1c1233e1a367d124648eb` |
| Installed SDK IOKitLib.h | `553869588e8c0b162b232e294dea2579cfd739d83e772a0b8a79e2be91a5816e` |

All seven stopped-session files match the new immutable manifest. The command record binds one exact binary invocation with the exact owner flag, real/effective UID502, external10-second timeout and zero retries. The invoked content-addressed binary and held source rehash to the same reviewed bytes. Process custody records rc2, no timeout, no retry and empty stderr; the actual0.238158-second host elapsed value is explicitly not target execution timing. Stdout/stderr hashes match their process record. The prior exact extension remains Markdown19c7fd88… and JSONe8b4a8cd…. Its accepted Choice A owner record is preserved; no new B-only owner approval is inferred.

Private session files, original Config/profile data and unit-identifying serial data are not copied into this public review. `recorded_metadata_facts.json` contains only the recorded numeric/class/count facts needed for this adjudication. PINS uses hash-only private input references for the stopped session.

## Supported facts from the actual run

The anchor query returned status0. The retained registry entry4295237137 was unique and directly verified as VID0738/PID4726/location0x100000. Its finite inventory recorded ten descendants at depths1–3, all class lookups successful, and the anchor summary states `identity_verified=true`, `inventory_complete=true`, `multiple=false`. The total inventory is11 nodes including the anchor,99 whitelisted registry-property records and11 child-iterator status records. No cap overflow or topology error was recorded during this anchor inventory.

Three inventoried descendants are named `IOUSBHostInterface`. One depth1 descendant, entry4295237143, has direct registry properties VID0738/PID4726/location0x100000, interface classFF/subclass5D/protocol1, number0, alternate0 and configuration1. The other two show CDC control/data class tuples2/2/0 and10/0/0. These are registry properties and class names, not successful interface300 getter values, descriptor bytes, opened report transport or observed controller outputs. Their numerical correspondence to the held predicate is useful metadata only. No class inheritance/equivalence or user-client compatibility follows merely from the displayed class name.

The subsequent original `IOUSBInterface` VID/PID query returned status0, followed by zero enumerated services. The final summary records `iterator_valid=false`, `outcome=INCOMPLETE_STOP`, zero plugin attempts/successes, zero interface300 successes, zero accepted candidates and zero reports. There are no original-query-service/plugin/QI/getter records. Exact source control flow therefore performs zero user-client metadata getters and no interface/endpoint/report operation in this run. The earlier anchor inventory did read numeric registry properties; the zero-getter claim refers specifically to the nine interface300 getters.

The wrapper preserved its `AssertionError()` stop, `no_retry=true`, `all_further_actions_stopped=true`. The stopped session records exactly one metadata invocation and zero owner Menu→Configurator entries, CDC metadata lookups, Configurator identities, GET_CONFIG backups, STATUS/LIST/READ operations, Config/profile writes, firmware copies, target metrics, raw retries or Switch/WUP actions. Nothing in this review turns that stop into physical PASS or authorizes continuation under the old packet.

## What the source and SDK prove, and what they do not

The exact probe source lines61–75 creates the original matching query, checks its return code, then unconditionally calls `IOIteratorNext(iter.v)` and later `IOIteratorIsValid(iter.v)`. Zero from Next breaks enumeration; false from IsValid makes `incomplete=true`, giving `INCOMPLETE_STOP` and rc2. The returned iterator handle is initialized to0 but is never logged. Consequently the journal proves the observed return values and the conservative classification, not the underlying handle or cause.

The installed `IOKitLib.h`434–446 explicitly documents that `IOServiceGetMatchingServices` can succeed with a NULL iterator when no matching services exist. Lines385–411 document that Next returns zero for either exhaustion or an invalid iterator, that validity should then be checked, and that some iterators may become invalid after structural changes. Those are separate permitted possibilities. Thus a successful NULL/no-match result is a source-grounded possible explanation of this host classification; a nonnull iterator that was invalid is another case the present records cannot distinguish. The SDK header is an API contract, not a record of which branch occurred on this machine. It does not prove a topology change, controller/firmware failure, OS iterator bug, or a universal rule that an empty iterator is invalid.

The anchor inventory's completion cannot certify validity of the separately returned original-query iterator. A syntactically complete captured JSON journal also does not make its `INCOMPLETE_STOP` a complete valid enumeration. The former packet allowed B after only specific complete diagnostic zero/multiple/refusal results and stopped all on incomplete topology/query/iterator uncertainty. Root correctly stopped all here. A new explicit B-only owner exception is therefore a real authority change, not a retrospective relabeling or an automatic fallback.

Actual iterator/root cause remains **UNPROVEN**. No extra query, handle-logging source change, reset/restart, different interface class or raw reader is needed or authorized to review the B-only preservation request. No raw-report access or backend-output acceptance follows from these data.

## Exact new packet correspondence and limits

The new JSON `preservation_readback` object equals the prior reviewed extension's phase B object exactly as decoded JSON, including every expected identity field, all22 original IDs, legacy-version qualification and request bounds. Markdown agrees. The packet binds F `334fbd06e4541c120b0db423e5be7e112eb1f6f6`, UF2 SHA `41305f260d42e8206bf4a2fb06c88912416e49cd8a68bc13ce3d3c7605306982`, both prior packet hashes and the exact stopped stdout/manifest above. No source/build/resource/protocol change is introduced.

The only proposed stop exception permits one owner-known Menu→Configurator selection including its normal firmware restart and confirmation; then one standard same-private-unit/location CDC metadata lookup at2E8A/1092 with no port opened during lookup. It permits one unchanged F Configurator identity request, requiring status/configurator/backend8, row/reference/incarnation/ID/revision/schema0 and null digest. Recovery or any unexpected identity stops. This current neutral identity does not attest earlier gameplay. Existing source qualification of the menu and read-only tools remains applicable; no guessed startup/backend/recovery chord,1200-baud command or host reset is added.

After positive identification, bounds remain one raw GET_CONFIG backup, one explicit normal STATUS, at most three LIST pages of8 and one READ per original ID `[1,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,24]`. LIST/READ already include preflight STATUS, so total STATUS is1+3+22=26. There is no added wrapper preflight, unlisted ID request or retry. Existing115200,16/72-byte identity framing, protocol2 ProfileStore tools and real/effective UID502 execution context remain bound.

The packet requires fresh normal incarnation1 and stable Config/store fences; exact original Config user fields/references and complete decoded profile bodies/revisions are compared to immutable private preinstallation custody. Monotonic firmware bookkeeping is separate; unexplained changes stop. Directory legacy1 and body3 stay two observed values; no normalization, repair, raw filesystem export, byte rollback or unobserved history claim is introduced. Each counter and exclusive output is reserved in a new private session before launch; both previous stopped sessions stay immutable.

Any new access refusal, unexpected/partial/invalid/error response, timeout, recovery, identity/fence difference or uncertainty stops all without retry or alternative discovery/access/driver/OS/UID route. Metadata invocations, report attempts, firmware copies, Config/ProfileStore/native mutations, target metrics and Switch/WUP actions are explicitly zero. No route adapter or H1–H12 campaign is authorized. After readbacks, preserve results and STOP.

All18 behavior families, missing backend outputs, human HEP, tested-source integration and strict DONE remain gated. Nunchuk NOT_TESTED, RT2 DEFERRED/UNRESOLVED, root cause UNPROVEN and target timing/highwater NOT_MEASURED remain honest. The new owner's exact B-only approval is the next authority gate; this ACK does not supply it. No additional build, source repair or review layer is justified by the finite evidence examined here.
