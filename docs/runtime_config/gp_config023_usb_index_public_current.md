# Current C023 USB-index host proof

Status label: CURRENT. Contract: `C023_PUBLIC_CURRENT_1`.

The current check extracts durable GP-CONFIG-023 invariants from the exact
current production and host bytes named in the [sealed public fixture](fixtures/gp_config023_usb_index_public_current.v1.json).
Run `python3 tools/check_glyph_gp_config023_usb_index_public_current.py`.
It does not read Git history, use historical refs, fetch project commits or
interpret a missing historical object as authorization.

The current schema is generated from checked source with Nanopb and grpcio-tools.
The checker executes 4,096 count/index cases (120 accepted; extent 15), oversized
count rejection, five pre-selector refusals and one selector-created refusal,
GameCube/XInput/Keyboard-DInput/watchdog routes, current semantic validation,
actual nanopb omitted/zero/out-of-range/overflow decoding, current persistence
load stages and valid stored publication. Invalid load preserves caller and
stored bytes and never saves. Both default and short enum ABIs use ASan/UBSan.

Current SET, startup and secondary-core ordering assertions follow the current
accepted split phase functions. Current backend and persistence bodies execute,
and their actual source-body semantic hashes are sealed alongside all compiler
reported repository dependencies and schema bytes. Each source and host hash has
a byte-mismatch negative; missing host material and semantic receipt drift fail.
An undeclared repository header dependency discovered by compilation fails closed.

The current source has accepted package/storage and backend phase changes since
C023. This fixture binds those current bytes explicitly. It does not substitute
old implementations or assert historical ancestry. Original transition replay
command `python3 tools/check_glyph_c023_proof_replay.py` remains historical evidence
in the development fork. The original fixture/report remain byte-exact there;
their paths and SHA-256 identities are inert provenance in this public receipt.
No historical private locator or hardware payload is copied.

This is host-only proof. Callback backends, filename/file/header and display
recorders are doubles. CRC/header authenticity, real flash/filesystem behavior,
full packet transport, complete setup, second-core scheduling and physical display
are outside this checker. See the fixture's exact coverage limits.
Hardware acceptance: **NOT_CLAIMED**. Nunchuk: **NOT_TESTED**.
Root cause: **UNPROVEN**. A synthetic PASS cannot become hardware acceptance.
