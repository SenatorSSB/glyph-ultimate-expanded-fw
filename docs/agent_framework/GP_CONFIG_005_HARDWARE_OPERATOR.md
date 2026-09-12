# GP-CONFIG-005 Hardware Operator Utility

Status: OPERATOR TOOLING ONLY.

Protocol version: `GP_CONFIG_005_HW_V1`.

This runbook is for the project owner performing the physical acceptance of
candidate `437f87e8086a50f0dfbd834176b80d245c1ed307`. The utility uses the
existing custom Glyph/HayBox USB serial configurator backend. It does not use
the retired official configurator, flash firmware, manipulate `config.bin`,
inject persistence faults, or create canonical hardware evidence.

The utility's JSON is operator evidence input. Human observations still must
be reported to the Hardware Evidence Processor. A mechanically expected
response is not an automatic hardware PASS.

## Before starting

1. Preserve the current accepted firmware and config using the owner's normal
   rollback process. Do this before changing the controller.
2. Manually flash exactly:

   ```text
   local_backups/hardware-artifacts/437f87e8086a50f0dfbd834176b80d245c1ed307/650b90961e170e6d88221ffe610545f43d880c9334c4d28ab613ad380418af44/firmware.uf2
   ```

3. Verify the preserved bytes immediately before the manual flash:

   ```bash
   shasum -a 256 local_backups/hardware-artifacts/437f87e8086a50f0dfbd834176b80d245c1ed307/650b90961e170e6d88221ffe610545f43d880c9334c4d28ab613ad380418af44/firmware.uf2
   ```

   The output must be exactly:

   ```text
   650b90961e170e6d88221ffe610545f43d880c9334c4d28ab613ad380418af44
   ```

4. Reconnect normally into the existing Configurator backend. The current
   Glyph config source binds that backend to `BTN_RT2` held on plugin. This is
   the schema button identifier; do not infer a physical label from this doc.
5. From the repository root, verify the pinned repository/candidate/artifact
   identity and list plausible serial ports:

   ```bash
   .venv/bin/python tools/gp_config_005_hw_test.py identity
   .venv/bin/python tools/gp_config_005_hw_test.py list
   ```

   `list` only enumerates paths. It does not open or auto-select a device.
   Choose the exact controller path yourself and pass it as `--port` to every
   live command. `/dev/cu.usbmodem2101` is an example, not a universal path.

## Preferred complete run

Replace `/dev/cu.usbmodemXXXX` with the path you explicitly selected:

```bash
.venv/bin/python tools/gp_config_005_hw_test.py status \
  --port /dev/cu.usbmodemXXXX

.venv/bin/python tools/gp_config_005_hw_test.py run \
  --port /dev/cu.usbmodemXXXX \
  --output-dir local_backups/gp-config-005-operator/physical-run
```

`run` performs this bounded sequence:

1. Reads device info and captures the persisted config through the existing
   `CMD_GET_CONFIG` path.
2. Writes `captured-config.json` with raw payload length/hash/base64 and decoded
   protobuf JSON. It labels the copy as host-side and non-authoritative.
3. Writes `payload-plan.json` before mutations.
4. Sends each rejection case separately from the captured baseline.
5. Requires exact `CMD_ERROR` text and sends existing `CMD_GET_DEVICE_INFO`
   after every rejection. Any wrong response, unexpected `CMD_SUCCESS`, or
   responsiveness failure stops the run before the valid update.
6. Displays the exact one-field `rgb_brightness` before/after diff. It sends no
   valid `CMD_SET_CONFIG` unless you type the exact generated confirmation
   token.
7. Requires `CMD_SUCCESS`, then uses `CMD_GET_CONFIG` as a persisted readback
   and writes `operator-result.json` with human-only observations left null.

`Config.rgb_brightness` is the valid-update field because the pinned schema
defines it as the overall RGB-lighting brightness modifier, the Glyph
brightness menu exposes the source-supported values `0`, `10`, `20`, `30`,
and `255`, and the NeoPixel backend passes it to LED brightness. The utility
chooses `20`, or `30` when the captured value is already `20`. It changes no
game mode, mapping, backend, or controller-output field.

After a mechanically successful valid update, manually reboot the controller
once and run the non-mutating status request again:

```bash
.venv/bin/python tools/gp_config_005_hw_test.py status \
  --port /dev/cu.usbmodemXXXX
```

Then perform the ordinary controller and display smoke check relevant to the
pre-test configuration. The reboot/readback observation does not prove atomic
persistence or power-loss safety.

## Rejection matrix

The current production handler has six bounded validation families plus the
malformed decode case, for seven rejection cases total. The phrase "seven
bounded validation rejections" would require an eighth production branch that
does not exist; the utility does not invent one.

| Case | Minimal mutation | Expected response | Follow-up |
| --- | --- | --- | --- |
| Malformed decode | Valid `CMD_SET_CONFIG`/COBS packet with protobuf payload `00` (illegal zero tag) | `CMD_ERROR`: `Failed to decode config: zero tag` | `CMD_GET_DEVICE_INFO` -> `CMD_SET_DEVICE_INFO` |
| Invalid default backend | `default_backend_config = communication_backend_configs_count + 1` | Exact existing default-backend error | Same |
| Invalid backend default mode | First backend `default_mode_config = game_mode_configs_count + 1` | Exact existing backend default-mode error | Same |
| Invalid keyboard reference/type | First suitable non-keyboard mode gets `keyboard_mode_config = 1` | Exact existing keyboard-type error | Same |
| Invalid custom reference/type | First suitable non-custom mode gets `custom_mode_config = 1` | Exact existing custom-type error | Same |
| Keyboard index out of range | Prefer an existing keyboard mode; otherwise minimally set a suitable mode to `MODE_KEYBOARD`; set its reference to `keyboard_modes_count + 1` | Exact existing keyboard-bound error | Same |
| Custom index out of range | Prefer an existing custom mode; otherwise minimally set a suitable mode to `MODE_CUSTOM`; set its reference to `custom_modes_count + 1` | Exact existing custom-bound error | Same |

Each case starts from an independent protobuf clone of the captured payload.
The plan/result records the exact leaf-field diff, deterministic protobuf
payload, SHA-256, base64/hex, and complete COBS-framed packet.

## Separate preparation and debugging commands

Capture without mutation:

```bash
.venv/bin/python tools/gp_config_005_hw_test.py capture-current \
  --port /dev/cu.usbmodemXXXX \
  --capture-out local_backups/gp-config-005-operator/captured-config.json
```

Inspect every exact payload without opening any device:

```bash
.venv/bin/python tools/gp_config_005_hw_test.py dry-run \
  --baseline local_backups/gp-config-005-operator/captured-config.json \
  --plan-out local_backups/gp-config-005-operator/payload-plan.json
```

Run only the rejection suite:

```bash
.venv/bin/python tools/gp_config_005_hw_test.py rejection-suite \
  --port /dev/cu.usbmodemXXXX \
  --baseline local_backups/gp-config-005-operator/captured-config.json \
  --result-out local_backups/gp-config-005-operator/rejection-result.json
```

The dry-run output prints the exact valid-update confirmation token. Review
the diff, then run the valid update only if intended:

```bash
.venv/bin/python tools/gp_config_005_hw_test.py valid-update \
  --port /dev/cu.usbmodemXXXX \
  --baseline local_backups/gp-config-005-operator/captured-config.json \
  --rejection-result local_backups/gp-config-005-operator/rejection-result.json \
  --result-out local_backups/gp-config-005-operator/valid-update-result.json \
  --rejection-observation-ack-token ACK_REJECTIONS_OBSERVED_NO_ANOMALY \
  --confirm-token SET_RGB_BRIGHTNESS_CURRENT_TO_NEW
```

An absent or inexact token prevents the serial device from being opened and
prevents `CMD_SET_CONFIG`. Both the one-field confirmation token and the
post-rejection observation acknowledgement token are required. An exact pair
still requires the completed seven-case rejection result tied to the same
capture. The acknowledgement permits the next operation but does not
auto-populate a human PASS. The valid-update path prints the diff again
immediately before opening the selected device, then rereads the persisted
payload before sending and stops on baseline drift.

## During test

Observe and report:

- malformed decode;
- all six bounded validation rejections (seven rejection cases total);
- the normal device-info responsiveness check after every rejection;
- absence of operational exposure of rejected values;
- the confirmed valid benign update;
- one reboot and persisted config read;
- the ordinary controller/display smoke check.

Do not infer live-RAM equality from `GET_CONFIG`: current source reads the
persisted `config.bin` body. Byte-level rejected-live-state preservation is
covered by the production host harness. Do not attempt a real `SaveConfig()`
failure, fill storage, corrupt `config.bin`, interrupt power during a write,
manipulate a filesystem, or add a fault command.

## Stop immediately if

- the device disconnects unexpectedly;
- any response differs from the expected command or text;
- any invalid payload returns `CMD_SUCCESS`;
- rejected values become operationally visible;
- controller or display behavior regresses;
- the protocol, candidate, artifact, baseline, or hash identity mismatches.

Stop before further mutation. Restore the prior firmware/config through the
owner-controlled rollback path and report `FAIL`, `PARTIAL`, or `INCONCLUSIVE`
with the generated files and observations. Do not edit the generated
`operator_assessment` to `PASS` and treat it as canonical evidence; submit the
operator result through the Hardware Evidence Processor.
