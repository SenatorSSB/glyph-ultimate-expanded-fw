# Glyph documentation

## Choose your route

| Reader | Start here |
| --- | --- |
| Players / users | [Usage](USAGE.md), then [capabilities](CAPABILITIES.md) |
| Profile authors | [Native Ultimate authoring v1](../profiles/README.md) |
| Developers | [Repository instructions](../AGENTS.md) and [workflow](WORKFLOW.md) |
| Coding agents | [AGENTS.md](../AGENTS.md), then [agent context](AGENT_CONTEXT.md) |
| Historical/evidence research | [Acceptance evidence](planning/final-usb-gamepad/acceptance/README.md), [maintenance audit](maintenance/README.md), [calibration index](calibration/README.md) |

[Current state](CURRENT_STATE.md) owns present qualification;
[roadmap](ROADMAP.md) owns forward intent. Their legacy journals preserve earlier
states and decisions pending consolidation. Historical pending statements describe
their own time. The public entry points above do not require that archaeology.

## Compact glossary

| Term | Meaning |
| --- | --- |
| Mode engine | Firmware logic translating inputs into controller outputs; distinct from a stock row label. |
| Communication backend | Transport/output implementation used by a mode, such as XInput or Switch USB. |
| Profile row | One `GameModeConfig` entry in Config's shared 30-row budget. |
| Native Ultimate profile | Finite tables, conditions, bindings and effects interpreted by the native Ultimate evaluator. |
| Complete package | One logical managed profile owning a dedicated Ultimate row and native ProfileStore record, with package metadata, plate and RGB. |
| Config | Device configuration containing mode rows, backend destinations and global settings. |
| ProfileStore | Persistent native-profile record/directory storage, separate from Config rows. |
| Coordinate table | Nine raw stick coordinates indexed by direction, including no-direction key 5. |
| Condition | A finite combination of supported input observations used by rules and gates. |
| Direction source | Explicit left/right/down/up tokens used to resolve a direction. |
| Digital binding | A token-driven output button bit, optionally filtered by the winning table. |
| Analogue effect | A gated rule supplying stick coordinates or trigger values. |
| Subsystem / sublayer | Player shorthand for coordinated conditions, table rules, bindings and effects; not a scripting engine. |

See [capabilities](CAPABILITIES.md) for implementation versus workflow and hardware
scope, and [authoring](../profiles/README.md) for precise native semantics.
