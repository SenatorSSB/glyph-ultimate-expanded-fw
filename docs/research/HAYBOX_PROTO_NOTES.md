# HayBox Proto Notes

HayBox-proto appears to define the config boundary that Glyph configurator exports project into.

Relevant schema areas:

- `GameModeConfig`
- `CommunicationBackendConfig`
- `CustomModeConfig`
- `KeyboardModeConfig`
- `RgbConfig`
- `ButtonRemap`
- `SocdPair`
- `AnalogTriggerMapping`
- `AnalogModifier`
- `ButtonComboMapping`

Practical takeaway:

- The schema supports important baseline controller config concepts.
- It does not appear to fully express all future Senscope/Glyph controller logic concepts on its own.
- Additional realization layers are still needed for exact tables, flipper transforms, and priority/suppression rules.
