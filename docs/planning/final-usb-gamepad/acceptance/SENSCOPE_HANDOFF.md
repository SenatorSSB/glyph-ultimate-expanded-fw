# Senscope handoff — prepared, target not frozen

Tested Glyph production source: `dcf6e29589f558a95c021bef491578f87e41750f`.
Tested tree: `a7731388430ea70dbe666298953795f4018069b0`.
Tested UF2 SHA-256: `2c77e2b7e50af2fd3b516d1ee7d0b8a67bcf992d6fcf0e3109a837422740cd42`,
1,325,568 bytes. [Freeze proposal](BETA_FREEZE_PROPOSAL.json) is not activated;
canonical integration commit UNKNOWN. The source-free acceptance branch is
`codex/final-usb-gamepad-hardware-acceptance`; its published tip must never replace the
tested build-source identity. [Correspondence proof](SOURCE_EQUIVALENCE.json).

Required selected-scope Windows XInput, original Switch USB/Ultimate, GameCube through
actual adapter to original Switch/Ultimate, preservation and reconnect PASS. All27
profiles and368-byte Config match preflight at final API readback. Unit continuity is
owner-attested; unique unit identifier and exact adapter model UNKNOWN.

DInput physical was N/A under the completed packet/profile. Separately, before public
Senscope complete-profile/device release, perform physical DInput acceptance using a
frozen beta firmware and an actual supported Senscope-authored profile exposing DInput.
This future complete-path acceptance does not retroactively expand firmware qualification.

Keyboard physical remains deferred. Switch2 is not qualified. Browser Gamepad API is
not qualified; JoyCheck XInput discrepancy unresolved. No universal raw-flash preservation
or Fresh Install recovery claim. Senscope retains game semantics/dataset/solver authority.

Senscope must not repin until the beta target is explicitly frozen/accepted by the owner.
Then perform fresh source correspondence and separate complete-package physical
acceptance against that exact target. This task made no Senscope repository changes.
