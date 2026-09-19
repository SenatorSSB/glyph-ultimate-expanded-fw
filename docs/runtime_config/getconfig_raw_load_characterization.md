# CMD_GET_CONFIG raw-load characterization

Status: `SOURCE_CHARACTERIZED_IMPLEMENTATION_NOT_AUTHORIZED`.

GP-PERSIST-002 compiles the exact current `HandleGetConfig` and
`LoadConfigRaw` production bodies against host-only doubles. It records that
`HandleGetConfig` validates first, writes `CMD_SET_CONFIG`, ignores the
`LoadConfigRaw` `size_t` result, and returns packet-end status. `LoadConfigRaw`
returns `0` on open/seek/optional-validation failure and `1` after its loop,
ignores each `Print::write` result, and cannot distinguish EOF from a read-error
`-1` sentinel.

This is source characterization only. It makes no claim about device delivery,
filesystem correctness, persistence integrity, recovery, atomicity, protocol
correction, or hardware acceptance. The host doubles do not access `config.bin`,
LittleFS, a controller, USB, or a device.

<!-- getconfig-raw-coverage:start -->
| Case | Observed current behavior |
| --- | --- |
| invalid check | error packet; no raw load |
| open/seek failure | `size_t` false/zero; caller does not expose raw failure |
| empty/payload | loop emits bytes after `CMD_SET_CONFIG`; completion returns one |
| zero/partial output write | write result ignored; loop completion still returns one |
| EOF/read-error sentinel | both terminate the loop identically |
| validate=false | optional validation is bypassed |
| packet end | `_out.end()` determines `HandleGetConfig` result, including failure |
<!-- getconfig-raw-coverage:end -->
