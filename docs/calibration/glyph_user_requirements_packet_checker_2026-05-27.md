# Glyph User Requirements Packet Checker - 2026-05-27

Purpose: define the structural-only validation contract for `tools/check_glyph_user_requirements_packet.py`.

## What It Validates

- required headings/section anchors exist in `docs/calibration/glyph_user_requirements_input_packet_2026-05-27.md`
- required current prefilled fact anchors are present
- blocker language is present (`blank/unfilled fields are blockers, not defaults`)
- unchecked completion boxes are present and pre-checked completion boxes are rejected
- output text explicitly states PASS is structure/presence only and not runtime readiness

## What It Intentionally Does Not Validate

- it does not resolve user requirements
- it does not approve runtime changes
- it does not approve hardware claims
- it does not choose omitted activates vs BTN_UNSPECIFIED policy
- it does not promote both-held behavior
- it does not infer defaults from blank fields
- it does not decide whether the packet is semantically complete for implementation

## Interpretation Rule

A PASS from this checker means structure/presence constraints passed only.
A PASS from this checker does not imply runtime readiness, preservation readiness, or implementation approval.
