#!/usr/bin/env python3
"""Guarded production ProfileStore acceptance operator.

This is deliberately not the strict-candidate/fault operator.  It implements
only STATUS, LIST, READ, and owner-authorized CREATE/UPDATE/RENAME/checked-reference/DELETE acceptance
workflow.  It never retries, resets, flashes, queries transactions, or writes
whole Configs.
"""
from pathlib import Path
import argparse, hashlib, json, os, sys
import glyph_serial_config_tool as transport
import glyph_profile_store_candidate_tool as candidate_transport

ROOT = Path(__file__).resolve().parents[1]
MUTATIONS = {"create": 4, "update": 5, "rename": 7, "set-reference": 10, "delete": 9}

def parse_uint(text): return int(text, 0)

def parse_args(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--port", required=True); p.add_argument("--timeout", type=float, default=5)
    p.add_argument("--journal-out", type=Path, required=True,
                   help="new host-only JSONL receipt; distinct from firmware --trace")
    p.add_argument("action", choices=("status", "list", "read", *MUTATIONS))
    p.add_argument("--profile-id", type=parse_uint); p.add_argument("--page", type=parse_uint, default=0)
    p.add_argument("--page-size", type=int, default=8); p.add_argument("--token", type=parse_uint, default=0)
    p.add_argument("--incarnation", type=parse_uint); p.add_argument("--store-generation", type=parse_uint)
    p.add_argument("--mode-index", type=parse_uint); p.add_argument("--config-generation", type=parse_uint)
    p.add_argument("--profile-revision", type=parse_uint); p.add_argument("--name"); p.add_argument("--rank", type=parse_uint)
    p.add_argument("--profile-json", type=Path); p.add_argument("--request-out", type=Path); p.add_argument("--output", type=Path)
    a = p.parse_args(argv)
    if not 0 < a.timeout <= 10: p.error("timeout must be within (0,10] seconds")
    if not 0 <= a.page <= 64 or not 1 <= a.page_size <= 8: p.error("page must be 0..64 and page-size 1..8")
    if a.output and a.output.resolve() == a.journal_out.resolve(): p.error("output and journal must differ")
    if a.action in ("read", "update", "rename", "delete") and not (a.profile_id is not None and 0 < a.profile_id <= 0xffffffff): p.error("requires nonzero uint32 --profile-id")
    if a.action in MUTATIONS:
        if not (0 < a.token <= 0xffffffffffffffff): p.error("mutation requires full nonzero uint64 --token")
        if a.incarnation is None or a.store_generation is None or not (0 < a.incarnation <= 0xffffffff and 0 <= a.store_generation <= 0xffffffff): p.error("mutation requires explicit valid --incarnation and --store-generation")
        if not a.request_out: p.error("mutation requires new --request-out receipt")
        if a.action in ("create", "update") and not a.profile_json: p.error("CREATE/UPDATE require --profile-json")
        if a.action in ("set-reference", "delete", "rename") and a.profile_json: p.error("reference/delete/rename never accept a payload")
        if a.action == "set-reference":
            if a.profile_id is None or not 0 <= a.profile_id <= 0xffffffff: p.error("reference requires explicit uint32 --profile-id (zero clears)")
            if a.mode_index is None or not 0 <= a.mode_index < 30: p.error("reference requires --mode-index within0..29")
            if a.config_generation is None or not 0 <= a.config_generation <= 0xffffffff: p.error("reference requires explicit uint32 --config-generation")
        elif a.mode_index is not None or a.config_generation is not None: p.error("mode/config fences apply only to set-reference")
        if a.action == "rename":
            if a.name is None: p.error("RENAME requires explicit --name")
            if a.rank is not None or a.profile_revision is not None: p.error("RENAME preserves rank/revision; only store-generation fencing applies")
        if a.action == "create" and (a.name is None or a.rank is None): p.error("CREATE requires --name and --rank")
        if a.action == "update" and not (a.profile_revision and a.profile_revision <= 0xffffffff): p.error("UPDATE requires positive --profile-revision")
        if a.name is not None and ("\0" in a.name or len(a.name.encode()) > 32): p.error("name must be <=32 UTF-8 bytes without NUL")
    return a

def emit(sink, phase, event, **fields):
    row = {"phase": phase, "event": event, **fields}
    line = json.dumps(row, sort_keys=True) + "\n"; sink.write(line); sink.flush(); os.fsync(sink.fileno())

def build_message(a, pb, json_format):
    operation = {"status": pb.PROFILE_STORE_STATUS, "list": pb.PROFILE_STORE_LIST,
                 "read": pb.PROFILE_STORE_READ, **{k: v for k, v in MUTATIONS.items()}}[a.action]
    m = pb.ProfileStoreRequest(protocol_version=2, operation=operation, request_token=a.token)
    m.profile_id = a.profile_id or 0
    if a.action == "list": m.page_cursor, m.page_size = a.page, a.page_size
    if a.action in MUTATIONS:
        m.expected_store_incarnation, m.expected_store_generation = a.incarnation, a.store_generation
        if a.action == "update": m.expected_profile_revision = a.profile_revision
        if a.name is not None: m.name = a.name
        if a.rank is not None: m.display_rank = a.rank
        if a.action == "set-reference":
            m.mode_config_index = a.mode_index; m.expected_config_generation = a.config_generation
        if a.action not in ("create", "update"): return m
        source = a.profile_json.read_bytes(); data = json.loads(source)
        data = data.get("response", data); data = data.get("profile", data)
        json_format.ParseDict(data, m.profile, ignore_unknown_fields=False)
        if m.profile.schema_version in (1,2,3) and ('nativePayload' in data or 'native_payload' in data):
            raise transport.ToolError('native payload field is forbidden in legacy profile source')
        from convert_glyph_native_ultimate_profile import validate_standalone_profile
        try:validate_standalone_profile(m.profile,pb)
        except ValueError as error:raise transport.ToolError(str(error)) from error
    return m

def verify_production_status(a, pb, s):
    if s.status != pb.PROFILE_STORE_OK: raise transport.ToolError("STATUS was not OK; no mutation sent")
    if s.protocol_version != 2: raise transport.ToolError("STATUS protocol is not production protocol 2; no mutation sent")
    retired = (s.core0_stack_min_free_bytes, s.core1_stack_min_free_bytes, s.heap_arena_peak_bytes,
               s.heap_arena_current_bytes, s.heap_arena_capacity_bytes, s.resource_diagnostics_enabled,
               s.strict_hardening_candidate, s.storage_fault_armed, s.storage_fault_triggered,
               s.storage_fault_operation, s.storage_fault_capable, s.storage_fault_ticket,
               s.storage_fault_pending, s.fault_control_version, s.liveness_stage, s.liveness_value,
               s.rx_phase, s.rx_raw_bytes, s.rx_decoded_bytes, s.rx_elapsed_ms, s.rx_task_passes,
               s.rx_last_progress_ms, s.rx_fetched_bytes, s.rx_flags)
    if any(retired):
        raise transport.ToolError("target advertises instrumented candidate controls; production admission refused")
    if s.mutation_protocol_version != 2: raise transport.ToolError("target does not advertise production mutation protocol 2")
    if a.action in MUTATIONS:
        if s.store_incarnation != a.incarnation or s.store_generation != a.store_generation:
            raise transport.ToolError("explicit incarnation/generation differs from target; no mutation sent")
        if a.action == "set-reference" and a.config_generation != s.config_generation:
            raise transport.ToolError("explicit Config generation differs from current target; no mutation sent")
        if a.token <= s.transaction_token_high_water or a.token == 0xffffffffffffffff:
            raise transport.ToolError("token is stale or exhausted; no mutation sent")
        if s.recovery_flags or not s.mutation_feasible:
            raise transport.ToolError("target is not mutation-admissible; no mutation sent")

def validate_result(a, pb, r):
    if r.request_token != a.token: raise transport.ToolError("response token mismatch; operation unresolved")
    if r.status != pb.PROFILE_STORE_OK: raise transport.ToolError("device returned non-OK status; operation outcome is device-reported")
    if a.action == "create" and not r.profile_id: raise transport.ToolError("CREATE response lacks allocated stable ID")
    if a.action in ("update", "rename", "set-reference", "delete") and r.profile_id != a.profile_id: raise transport.ToolError("response profile identity mismatch")

def main(argv=None):
    a = parse_args(argv); port = transport.PosixSerialPort(a.port, 115200, a.timeout)
    try:
        pb, jf, _ = transport.load_runtime_proto_modules(ROOT)
        with a.journal_out.open("x", encoding="utf-8") as journal:
            port.open(); port.flush_input()
            status_request = pb.ProfileStoreRequest(protocol_version=2, operation=pb.PROFILE_STORE_STATUS)
            old_sink = candidate_transport.TRACE_SINK; candidate_transport.TRACE_SINK = journal
            try:
                status = candidate_transport.request(port, pb, status_request, phase="status_preflight")
                verify_production_status(a, pb, status)
                if a.action == "status": response = status
                else:
                    message = build_message(a, pb, jf); payload = message.SerializeToString(deterministic=True)
                    if a.action in MUTATIONS:
                        receipt = {"receipt_format": 1, "mode": "production_acceptance", "request_hex": payload.hex(),
                                   "request_sha256": hashlib.sha256(payload).hexdigest(), "incarnation": a.incarnation,
                                   "decoded_request": jf.MessageToDict(message, preserving_proto_field_name=True)}
                        with a.request_out.open("x", encoding="utf-8") as out:
                            json.dump(receipt, out, sort_keys=True, indent=2); out.write("\n"); out.flush(); os.fsync(out.fileno())
                        directory_fd = os.open(str(a.request_out.parent), os.O_RDONLY)
                        try: os.fsync(directory_fd)
                        finally: os.close(directory_fd)
                        emit(journal, a.action, "immutable_receipt_persisted", request_sha256=receipt["request_sha256"])
                    response = candidate_transport.request(port, pb, message, exact_payload=payload, phase=a.action)
                    if a.action in MUTATIONS: validate_result(a, pb, response)
            finally: candidate_transport.TRACE_SINK = old_sink
            result = {"response": jf.MessageToDict(response, preserving_proto_field_name=True)}
            text = json.dumps(result, sort_keys=True, indent=2) + "\n"
            if a.output:
                with a.output.open("x", encoding="utf-8") as out: out.write(text); out.flush(); os.fsync(out.fileno())
            print(text, end="")
        return 0
    except Exception as e:
        print("production ProfileStore tool: " + str(e)); return 1
    finally: port.close()

if __name__ == "__main__": raise SystemExit(main())
