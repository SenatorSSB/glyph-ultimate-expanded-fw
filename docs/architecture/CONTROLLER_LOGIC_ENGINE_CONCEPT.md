# Controller Logic Engine Concept

The controller logic engine should be able to express:

- exact directional modifier tables
- flipper transforms
- pre-SOCD output override rules
- force-UpB rule concept
- dynamic button layers
- button chord rules
- priority and suppression semantics

## Semantics

- Exact directional modifier tables map a current direction and active modifier state to an exact output.
- Flipper transforms are explicit safe transforms, not overflow tricks.
- Pre-SOCD overrides run before any SOCD resolution step.
- Force-UpB is a rule concept, not a hardcoded gameplay assumption.
- Dynamic button layers change the active mapping set as inputs or states change.
- Chord rules describe combinations of buttons that trigger distinct outputs.
- Priority and suppression determine which rule wins when multiple rules match.

This document defines concepts only. It does not prescribe implementation details.
