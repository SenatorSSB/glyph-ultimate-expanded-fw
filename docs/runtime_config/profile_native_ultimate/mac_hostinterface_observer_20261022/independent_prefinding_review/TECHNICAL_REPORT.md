# Independent host-interface source safety review

**Bounded technical PASS: no concrete safety defect found in the frozen host-only source and affected offline scope. Final operator/owner-packet correspondence remains pending.** No live operation or physical approval is implied.

Reviewed source is `/private/tmp/glyph-native-Mac-hostinterface-observer-20261022/mac_hostinterface_observer.mm`, SHA f525991c7f43e59b1f0711c41edabe5937e4e03a882d7b653eb41be362823108; core SHA e96339c53c098a1d500e71a950b62171be0bce01ac4776e3a7f141046de3efe1; binary SHA ee26c84cb19eb40017329297732ee504774211941aa5067620cd6a5fb4b5e1a7; technical hold SHA b6d3003dc810fd096cbc86431359d741f579fee56ed25de19460e3d5ae60994c. All14 held files and15 external SDK/source pins independently rehashed. Source/index/excerpts and independent commands/results are retained beside this report.

## API and identity boundary

The installed primary SDK supports direct IOUSBHostInterface construction with optionsNone and a supplied serial queue; all asynchronous I/O is serviced on that queue. This is ordinary exclusive ownership of the selected interface, and may fail when unavailable/busy. It is not a guarantee that access is granted. The implementation does not use a legacy interface alias, device-level open, seize, driver/privilege workaround, explicit OUT/control/configuration/reset/alternate change or endpoint-recovery fallback.

Registry-only inspect is a separate command and never constructs an IOUSBHostInterface or automatically captures. It matches the fixed device VID0738/PID4726/location0x100000; requires one valid anchor; traverses at most32 descendants and depth3 with duplicate/unknown/invalid identity refusal; selects one interface number0/classFF/subclass5D/protocol1/alt0/config1. Capture requires separately supplied nonzero distinct fresh anchor/interface entry IDs and rechecks the same bounded ancestry and numerical identity before opening. Missing inherited vendor/product/location on a child is permitted only under the verified anchor; conflicting or invalid values refuse. Interface identity fields must be present and valid. Location/VID/PID/ancestry alone do not uniquely attest a private physical unit or installed firmware; fresh same-connection IDs and separate private-unit custody remain required.

Only associated configuration/interface descriptor getters are used. Their bytes are journaled and validated for bounded little-endian total length, configuration1, unique interface/alternate pairs and interface count, selected exact associated interface, and exactly one IN plus one OUT interrupt endpoint. Packet size32, IN interval1 and OUT interval8 are checked. The actual IN endpoint address comes from the associated descriptor rather than template0x81; the pipe's host association, endpoint and original/current descriptors must correspond. The OUT endpoint is validated but never opened/submitted. The source accepts only actual completed20-byte XInput frames from the32-byte backing buffer and parses all fields with the unchanged frozen decoder. Unsupported frame/status/count/parser cases stop without retry.

These API choices establish the source call boundary. The SDK does not promise that associated getter/pipe/abort implementations contain no internal bus traffic, nor that abort or other framework calls return within a finite time. Operator prose must preserve these limits rather than promise electrically passive or transaction-free observation.

## Dispatch, lifetime, cancellation and custody

State is a single intentionally process-lifetime allocation, retaining the dispatch queue/semaphore/timer, strong ARC host/pipe/data objects, inline engine and journal. There is no destructor or stack-backed callback context. All I/O/timer/cleanup logic runs on its serial queue; the main thread observes completion through the semaphore. A pending engine allows one asynchronous abort; grace is armed before fallible abort/logging. Undrained or exception-uncertain state retains every resource until _Exit. Late completion after finished returns without reading/releasing data or journal.

Settled cleanup is dispatched behind the current completion block, retaining data/pipe/interface through callback epilogue; it cancels the timer, releases pipe/data and destroys the host once. A third valid timely report succeeds; no callback after deadline/draining can make success true. Errors, count mismatch, parse failure, custody exceptions, submission rejection, initialization/descriptor/identity failure and Objective-C exceptions fail closed. Uncertain logs and process deadline are not success evidence.

The file is newly created O_EXCL with private permissions and raw status/count/bytes/decoded fields are synchronously flushed. Successful exit requires healthy custody and three accepted preflight reports. Failed flush/close changes the exit status; incomplete or failed journals cannot support acceptance. Five seconds bounds the observation engine; it does not prove synchronous framework calls finish then. The independent eight-second main-thread wait ends via _Exit without freeing callback state. The proposed external ten-second caller deadline must likewise be described as a process bound, not guaranteed completed USB cancellation or restoration. A killed/timed-out process is STOP/uncertain, with no automatic retry or fallback.

## Independent execution

All execution was private, offline or mocked. No live inspect/capture/query/plugin/init/descriptor/pipe/read/cancel or serial API was invoked; no firmware build/change, Git/worktree/publication, install, network or owner contact occurred.

- Independently rebuilt and ran all157 core descriptor/identity/lifecycle checks with ASan/UBSan.
- Independently rebuilt and ran all24 actual-source mock scenarios with ASan/UBSan. Every registry and IOUSBHost type/API entry used by the included actual source is overridden by the inspected mock harness. Real Foundation/CF/dispatch operate only on in-process mock state.
- Added three focused actual-source mocked exception cases: journal fsync failure during completion, Objective-C exception after retaining a pending enqueue callback, and journal fsync failure after interface acquisition. The first two retain complete uncertain state and ignore late completion; the last settles/cleans once. All pass sanitizers. Only the private mock harness changed.
- Independently rebuilt the full host executable byte-identically to ee26... and executed only --self-test and --decode-xinput on a synthetic20-byte frame. Its live argument/registry/capture paths never ran.

The larger frozen1002/48 decoder and334+9 native pure XInput evidence was inspected as unchanged context, not broadly repeated. No sanitizer/host-mock result establishes actual SDK/driver access, real cancellation behavior, controller acceptance, latency or stack highwater. Initial reviewer SDK excerpt-range correction is preserved explicitly; held inputs were untouched.

## Carried boundaries and pending final binding

F334fbd06/tree0483dbb0 and previously sealed ELF/UF2/resource proof remain unchanged and outside this review. The exact334-row packet remains dfd4ab5c81c24e1380095fa637ff0d51de83b478f66641c53d1a69d9f76be744. No console acceptance transfer, backend identity attestation, new profile/config capability or physical result is claimed. Actual host access remains UNVERIFIED; hardware/Nunchuk remain NOT_TESTED and timing/highwater NOT_MEASURED.

This is the finite technical result. Final author report/operator/PINS and root's exact owner MD/JSON must still be bound by this same reviewer for scope/correspondence. New exact owner approval is mandatory before any live inspect or capture; the current installed device remains STOP in Configurator. Root is the sole publisher and owner-contact authority.
