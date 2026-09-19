# GP-CONFIG-007 host transaction result contract

Status: CURRENT, host-only, schema version 2.

New mechanical results from `tools/gp_config_005_hw_test.py` must use integer
`schema_version: 2`. Schema version 1 is historical GP-CONFIG-005 input and is
refused for new validation; historical files are not migrated or reinterpreted.

The transaction stages are an exact duplicate-free prefix, in this order:

1. `prewrite_read_attempted`
2. `prewrite_read_completed`
3. `prewrite_baseline_matched`
4. `write_attempted`
5. `full_host_write_completed`
6. `awaiting_response`
7. `response_received`
8. `response_decoded`
9. `followup_read_attempted`
10. `followup_read_completed`

`transaction_stage` is the final stage or `not_started`; every named boolean
equals stage presence; `sent` equals `full_host_write_completed`; and
`partial_write_ambiguous` is true only after a write attempt without complete
host-write progress. Each stage timestamp is ISO-8601 UTC. The mechanical
outcome must agree with the observed prefix, including baseline drift,
transport/follow-up stops, unexpected response, persisted readback mismatch,
and complete success.

This contract does not change COBS bytes, command order, retries, firmware,
device behavior, persistence guarantees, or hardware evidence. The existing
GP-CONFIG-005 capture and plan schemas remain version 1.
