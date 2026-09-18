# Project-owner decision — official configurator retirement and X1 authority pilot

Decision identity: `owner-decision-2026-08-27-x1-overlay-pilot`

Date: 2026-08-27

Authority: `project_owner_user_authority`

## Official Glyph configurator lane

The official Glyph configurator interoperability lane is retired as an active product/development dependency for the custom Glyph/Senscope firmware path. `GP-CONFIG-002` is invalidated and must not be treated as executable or effective gated runway. No official-configurator operator capture is required or awaited unless the project owner explicitly reopens that research lane later.

Historical documentation and evidence remain historical provenance; this decision does not delete or rewrite them as if the prior research never existed.

## Source-authority mode

`GP-AUTH-001` uses `overlay_preserve`. `full_replacement` is not authorized.

## Initial owned table

The sole initially owned source-owned production table is canonical `kX1Table` (table id 2 in the current 28-table baseline). No second table is authorized by this decision.

## Initial production content

The authorized replacement is exactly the current canonical baseline-equivalent `kX1Table` raw content, ordered by `direction_key` 1 through 9:

| direction_key | x | y |
|---:|---:|---:|
| 1 | 93 | 51 |
| 2 | 128 | 51 |
| 3 | 163 | 51 |
| 4 | 93 | 128 |
| 5 | 128 | 128 |
| 6 | 163 | 128 |
| 7 | 93 | 205 |
| 8 | 128 | 205 |
| 9 | 163 | 205 |

The current canonical baseline supplies these bytes; this project-owner decision supplies production authority for those exact bytes. This is deliberately behavior preserving and is not evidence that Senscope originally generated the values.

## Explicit limits

This decision does not authorize different X1 coordinates, ownership of another table, all-28 replacement, active table-byte changes, new modifier/gameplay semantics, runtime-loaded or persistent configuration, WebSerial/device/protobuf writes, flashing automation, alternative active publication views, RAM-backed active publication, or Nunchuk behavior claims.

Any later active X1 value change is a separate behavior-changing candidate and must follow the then-current H2/H3 exact-candidate hardware lifecycle. Future expansion of Senscope/user authority remains roadmap direction only and requires later explicit authorization.
