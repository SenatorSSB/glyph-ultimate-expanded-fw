# Exact first-beta hardware acceptance

FIRST_BETA_PHYSICAL_QUALIFICATION: **PASS**, exact selected scope only.
[Physical result](PHYSICAL_RESULT.json) · [Independent review](INDEPENDENT_REVIEW.json) ·
[Preservation replay](PRESERVATION_REPLAY.json) · [Owner observations](OWNER_OBSERVATIONS.json) ·
[Private capture hashes](PRIVATE_INPUT_MANIFEST.json) · [Source equivalence](SOURCE_EQUIVALENCE.json).

Tested production source `dcf6e29589f558a95c021bef491578f87e41750f`, tree
`a7731388430ea70dbe666298953795f4018069b0`; tested UF2 SHA-256
`2c77e2b7e50af2fd3b516d1ee7d0b8a67bcf992d6fcf0e3109a837422740cd42`, 1,325,568 bytes.
Build evidence is the distinct descendant `ebde1447f5cf348b3af82240ebd95445b44cb888`.
This acceptance is a later source-free descendant, never the UF2 build source.

X1/X2, S1/S2, G1/G2, P1/P2 and R1 PASS. D1/D2 N/A: no selected beta profile exposes
DInput. Browser Gamepad API/JoyCheck NOT_QUALIFIED; HOME-only XInput behavior remains
unresolved despite Windows identity/joy.cpl PASS. Switch USB buttons worked on that
same browser site. No proven controller defect or universal browser claim follows.
SOURCE_FIX_REQUIRED: none identified for selected first-beta required scope.

Machine evidence comprises three complete 64-exchange captures, exact368-byte Config,
ordered27-entry inventory, all wrapper bytes/revisions/digests and81 healthy profile
observations. The independent reviewer reconstructed these from raw protobuf responses
and journals, verified491 private hash-manifest files and both retained UF2 copies.
Raw Config/library and captures remain private; their exact locators/hashes are retained.
This proves API-visible preservation, not universal raw-flash equality. Final normal
reconnect/usability is owner-reported; no later raw post-reboot comparison is claimed.

Physical routes, installation and Device Manager observations are owner reports in this
chat, not machine gameplay recordings or flashed-byte attestation. The owner identifies
one continuing unit, backed by INFO and distinctive unchanged state. A unique unit ID
and exact GameCube adapter model are UNKNOWN; neither is mandatory under the approved
packet. These limit reproduction/generalization without invalidating this selected scope.
Owner profile label is Kaz5Test; saved native53 name is KazTest5. Execution behavior was
owner-observed; saved labels alone and Configurator identity do not attest gameplay.

Chronology is preserved: earlier audit found no defect; later Pico-only smoke exposed a
publication issue; source repair generalized final XInput/DInput/Switch reconnect; exact
committed source was built and retained; owner tested those bytes; required rows passed.
Initial apparent Pico-only FAIL was superseded by exact0738:4726/working driver evidence.
The first final-readback timeout is retained: owner had not entered Configurator; the
subsequent full capture passed. Earlier DInput profile-index inference was corrected.
Capture/transcription times are not precise physical action timestamps.

Host/source repair proof remains PASS within its recorded focused scope. Existing full
wrapper/aggregate and standalone failures in [original validation](../VALIDATION.json)
remain explicit framework debt; no new aggregate PASS or firmware rebuild is claimed.

Canonical integration PENDING_OWNER_AUTHORIZATION; [freeze](BETA_FREEZE_PROPOSAL.json)
PREPARED_NOT_ACTIVATED. [Exact integration procedure](INTEGRATION_PREPARATION.md) and
[Senscope handoff](SENSCOPE_HANDOFF.md) are preparation only. No canonical publication,
beta tag, public release, flash or source/build-input edit occurred in this review.

[Exact committed packet review](PACKET_REVIEW.json) approves acceptance record
`2d64e75a1f020d1f7564d3a15db63cb7fcffe96a`. Later review-only descendants preserve
the tested-source distinction. The final published tip is pinned in the owner handoff;
canonical integration remains UNKNOWN/pending and freeze remains unactivated.
