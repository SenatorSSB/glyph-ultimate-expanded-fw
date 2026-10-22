# Stage A recovery — 2026-10-23

Owner approved Stage A only and connected the previously recorded Mk6.
Independent review: PASS_WITH_SCOPE_QUALIFICATION. No unexpected stored state.
All 23 original and 20 fixture canonical API wrappers and directory metadata
match the retained baseline exactly, including revisions. Config API snapshot
retains GameCube and SEL01 (ID28), byte-exact to baseline plus the three expected
selector fields. All 50 status responses have recovery_flags=0; store fences
remain incarnation1/generation197. The captured Config is277bytes, SHA256
`65ecdcf32ecc4d0ce99edbc9a6b29aa99186ce1cd0c217d626764659d54e71dd`.

Executed reads: one neutral Configurator identity, one Config GET, 50 STATUS,
6 LIST pages and43 READs;52 serial opens. Zero mutations, retries or flashes.
Execution tools/schema match committed candidate8b2c75e3 and failed48989519.
Raw device identifiers, Config/profile bodies and wire journals remain private.

Scope: GET_CONFIG checks saved Config then streams LoadConfigRaw. This proves
an API snapshot, not an independent raw filesystem image. Publication timing
relative to freeze/reconnect, GameCube active runtime identity, and installed
firmware Git identity remain UNKNOWN. Original sealed evidence used broader
“durable” wording; additive qualifications explicitly supersede that wording.
All371 original sealed files were independently checked unchanged.

Private original manifest SHA256:
`db4bca49575f9f4a173871ce295c8b096bf127271414c800ab594a0b6d9cbfa8`.
Private final manifest (379 files) SHA256:
`68aeca566c79462fe64c4411404c549a34ffe9e54718da0660a9c033651e882f`.
Independent review SHA256:
`9fdc5be2a9f4ea7617ec13b74f3c265af2d447398d182f4f45f2fa80a0f5bf3e`.

Owner reports Switch through GC adapter; controller cannot connect to Mac
simultaneously. Normal GameCube observations must therefore be owner-reported,
with Mac readback in a separate connection. No powered/no-poll method is
established. This does not authorize adapter unplug/replug or infer no polling
from Switch UI state. Stage B exact manual installation and normal physical
rows still need separate approval. The no-poll row remains separately gated;
acceptance remains incomplete until required hardware evidence is resolved.
Root cause UNPROVEN; Nunchuk NOT_TESTED. No HEP, integration, DONE or queue change.
