# Glyph Backend Layering

The intended layering for this workstream is:

1. Neutral profile layer
2. Controller capability layer
3. Realization / evaluation layer
4. Adapter / export layer
5. Future inverse-search layer

## Layer responsibilities

- Neutral profile layer: stores neutral intent, including non-center neutral.
- Controller capability layer: describes what the device can actually realize.
- Realization / evaluation layer: turns profile intent into device-legal outputs.
- Adapter / export layer: converts between external config formats and the internal model.
- Future inverse-search layer: searches controller realizations that satisfy a semantic target.

## Design boundary

Controller semantics and game semantics must remain separate across these layers.
