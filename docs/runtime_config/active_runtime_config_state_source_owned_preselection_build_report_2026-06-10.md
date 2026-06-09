# Active Runtime Config State Source-Owned Preselection Build Report

status: scaffold_ready

branch: `runtime-active-config-state-source-owned-preselection`

baseline branch: `configurator`

build command: `pio run -e glyph_mk6`

build note: canonical user command recorded; fallback may be used only if platform tooling fails in this environment.

## Build artifacts

| field | value |
| --- | --- |
| `firmware artifact path` | unknown |
| `firmware artifact sha256` | unknown |
| `build exit status` | not_recorded |
| `build environment` | glyph_mk6 |

## Scope and behavior notes

- Source-owned active config preselection scaffold added in firmware source.
- Hot-path resolution now binds through `ResolveActiveRuntimeConfig()`.
- No parsed table materialization, parser calls, storage, WebSerial/device write,
  or flashing automation added.
- RF5/RF6/LT6 expression logic and `UpdateDigitalOutputs(...)` behavior are intended
  to remain unchanged relative to `configurator` baseline.
