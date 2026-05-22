# Neutral Profile to Glyph Realization

Pipeline concept:

1. Senscope defines neutral profile intent.
2. Glyph capability constraints describe what the device can realize.
3. The realization layer evaluates whether each desired output is legal.
4. The adapter layer exports or imports the config representation.
5. An inverse-search layer can later search for realizable controller behavior that matches a profile.

## Key rule

Neutral output is first-class and may be non-center.

## Key separation

- Controller semantics describe how a device should behave.
- Game semantics describe why a profile is desirable in-game.

The two must stay separate so the firmware workstream can remain a realization target instead of becoming the semantic source of truth.
