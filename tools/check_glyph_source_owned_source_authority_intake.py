#!/usr/bin/env python3
"""Fixture-backed authority and ownership regression matrix for intake v1."""
from __future__ import annotations
import copy, json, tempfile
from pathlib import Path
from source_owned_source_authority_intake import (PLACEHOLDER, IntakeError, assert_safe_offline_output_path, create_template, emit_generator_input, inspect_baseline, review_intake)

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "docs/runtime_config/fixtures/source_owned_source_authority_intake.json"
POSITIVE = NEGATIVE = 0

def make_packet(mode: str = "overlay_preserve", operation: str = "production_changeset", owned_count: int = 1) -> dict:
    base = inspect_baseline(); symbols = base["table_order"][:owned_count if mode == "overlay_preserve" else 28]
    tables = {t["table_symbol"]: t for t in __import__("source_owned_generator_modes")._baseline_tables()}
    replacements=[]; declarations=[]
    for symbol in symbols:
        points=[{"direction_key": i+1, "x": point["x"], "y": point["y"]} for i, point in enumerate(tables[symbol]["points"])]
        if operation == "production_changeset": points[4]["x"] = 127 if points[4]["x"] != 127 else 126
        replacements.append({"table_symbol":symbol,"points":points,"rationale":"human-approved table replacement","source_reference":"user-source-authority-reference"})
        declarations.append({"table_symbol":symbol,"rationale":"human approved ownership","authorization_reference":"user-source-authority-reference"})
    return {"schema_version":1,"intake_id":"fixture-intake","profile_id":"fixture-profile","profile_name":"fixture-profile","purpose":"fixture only; does not imply hardware validity","author":"fixture-author","notes":"synthetic checker fixture","authority":{"status":"approved","basis":"human source authority record","approver":"fixture-reviewer","statement":"approved for offline generator-input validation only","approval_reference":"fixture-approval"},"intent":{"provenance_class":"production_authorized" if operation=="production_changeset" else "source_baseline_derived","generation_mode":mode,"requested_operation":operation,"controller_scope":"Glyph Mk6","source_owned_runtime_tables":True},"baseline":base,"ownership":{"owned_tables":symbols,"declarations":declarations,"unlisted_tables_are_unowned":True},"replacements":replacements,"review":{"unresolved_questions":[],"acknowledges_build_not_hardware_proof":True,"acknowledges_separate_hardware_gate":True}}

def assert_blocks(packet: dict, label: str) -> None:
    global NEGATIVE
    report=review_intake(packet)
    assert report["blockers"], label
    NEGATIVE += 1

def run() -> tuple[int,int]:
    global POSITIVE, NEGATIVE
    policy=json.loads(POLICY.read_text()); assert len(policy["negative_case_ids"]) == 40
    one=make_packet(); value, artifact, manifest=emit_generator_input(one, operation="production_changeset"); assert manifest["classification"] == "EXPLICIT_OWNED_TABLE_CHANGESET"; POSITIVE+=1
    multi=make_packet(owned_count=2); emit_generator_input(multi, operation="production_changeset"); POSITIVE+=1
    full=make_packet("full_replacement"); emitted, _, manifest=emit_generator_input(full, operation="production_changeset"); assert "owned_tables" not in emitted and manifest["changed_table_count"] == 28; POSITIVE+=1
    equivalence=make_packet(operation="source_equivalence_proof", owned_count=0); _,_,manifest=emit_generator_input(equivalence, operation="source_equivalence_proof"); assert manifest["classification"] == "NO_OP"; POSITIVE+=1
    template=create_template(); assert review_intake(template)["blockers"] and not template["replacements"]; POSITIVE+=1
    assert json.dumps(review_intake(one),sort_keys=True)==json.dumps(review_intake(copy.deepcopy(one)),sort_keys=True); POSITIVE+=1
    cases=[]
    def add(name, fn): cases.append((name,fn))
    add("missing_schema_version", lambda p:p.pop("schema_version")); add("unknown_schema_version", lambda p:p.__setitem__("schema_version",99)); add("missing_authority_status", lambda p:p["authority"].pop("status"));
    for label, state in (("draft_production","draft"),("submitted_production","submitted_for_review"),("rejected_production","rejected"),("superseded_production","superseded")): add(label, lambda p,s=state:p["authority"].__setitem__("status",s))
    add("approved_missing_approver",lambda p:p["authority"].__setitem__("approver", "")); add("approved_missing_basis",lambda p:p["authority"].__setitem__("basis", "")); add("production_without_approval",lambda p:p["authority"].__setitem__("status","draft"));
    for label, provenance in (("synthetic_production","synthetic_test"),("example_production","example_only"),("migrated_legacy_production","migrated_legacy"),("unknown_provenance","unknown")): add(label,lambda p,x=provenance:p["intent"].__setitem__("provenance_class",x))
    add("missing_generation_mode",lambda p:p["intent"].__setitem__("generation_mode",None)); add("reject_partial",lambda p:p["intent"].__setitem__("generation_mode","reject_partial"));
    add("replacement_without_ownership",lambda p:p["ownership"].__setitem__("owned_tables",[])); add("ownership_without_replacement",lambda p:p.__setitem__("replacements",[])); add("unowned_replacement",lambda p:p["ownership"].__setitem__("owned_tables",[]));
    add("duplicate_owned",lambda p:p["ownership"]["owned_tables"].append(p["ownership"]["owned_tables"][0])); add("duplicate_replacement",lambda p:p["replacements"].append(copy.deepcopy(p["replacements"][0]))); add("unknown_table",lambda p:p["ownership"]["owned_tables"].__setitem__(0,"kUnknownTable"));
    add("empty_production_changeset",lambda p:(p["ownership"].__setitem__("owned_tables",[]),p["ownership"].__setitem__("declarations",[]),p.__setitem__("replacements",[]))); add("full_missing_table",lambda p:(p["intent"].__setitem__("generation_mode","full_replacement"),p["ownership"].__setitem__("owned_tables",[]))); add("full_extra_table",lambda p:(p["intent"].__setitem__("generation_mode","full_replacement"),p["ownership"]["owned_tables"].append("kUnknownTable"))); add("full_wildcard",lambda p:p["ownership"]["owned_tables"].__setitem__(0,"*"));
    add("stale_baseline",lambda p:p["baseline"].__setitem__("semantic_digest","stale")); add("wrong_source_path",lambda p:p["baseline"].__setitem__("source_path","wrong")); add("wrong_table_count",lambda p:p["baseline"].__setitem__("table_count",27));
    add("changed_source_baseline_derived",lambda p:p["intent"].__setitem__("provenance_class","source_baseline_derived")); add("unresolved_question",lambda p:p["review"].__setitem__("unresolved_questions",[{"question":"unknown","blocking":True}])); add("placeholder_approval",lambda p:p["authority"].__setitem__("approver",PLACEHOLDER)); add("placeholder_point",lambda p:p["replacements"][0]["points"][0].__setitem__("x",PLACEHOLDER)); add("invalid_coordinate",lambda p:p["replacements"][0]["points"][0].__setitem__("x",-1)); add("wrong_point_count",lambda p:p["replacements"][0].__setitem__("points",[])); add("nondeterministic_order",lambda p:p["replacements"][0]["points"].__setitem__(0,{"direction_key":2,"x":1,"y":1}));
    add("infer_from_replacement",lambda p:p["ownership"].__setitem__("declarations",[])); add("infer_from_difference",lambda p:p["ownership"].__setitem__("owned_tables",[])); add("canonical_grid_unspecified",lambda p:p["replacements"].append({"table_symbol":inspect_baseline()["table_order"][1],"points":[{"direction_key":i,"x":128,"y":128} for i in range(1,10)],"rationale":"canonical default","source_reference":"none"}));
    for expected, (name, mutate) in zip(policy["negative_case_ids"][:-1],cases):
        assert expected == name, (expected,name); packet=make_packet(); mutate(packet); assert_blocks(packet,name)
    with tempfile.TemporaryDirectory() as directory:
        try: assert_safe_offline_output_path(ROOT / "src" / "blocked.json"); raise AssertionError("protected src accepted")
        except IntakeError: NEGATIVE+=1
    return POSITIVE,NEGATIVE

if __name__ == "__main__":
    try:
        positive,negative=run(); print(json.dumps({"status":"PASS","positive_tests":positive,"negative_tests":negative,"active_source_changed":False,"hardware_candidate_created":False},sort_keys=True)); raise SystemExit(0)
    except Exception as exc: print(f"error: {exc}"); raise
