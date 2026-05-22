# Glyph Config Export Notes

The current Glyph configurator JSON appears to be a HayBox-proto `Config` projection.

Observed coverage:

- game modes
- SOCD configuration
- button remapping
- backend configs
- keyboard modes
- RGB configs
- dashboard / menu metadata

Observed limitation:

- The public model does not appear sufficient for full exact 9-way modifier tables, flipper modifiers, pre-SOCD force-UpB overrides, or dynamic button-layer switching.

This export is still valuable as a base profile import/export artifact and as a stable adapter boundary.

Raw reference copy:

- `docs/sources/raw/GlyphUserProfiles.json`
