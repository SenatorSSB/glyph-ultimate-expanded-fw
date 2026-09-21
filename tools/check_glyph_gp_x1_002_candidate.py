#!/usr/bin/env python3
"""Fail-closed source and scope check for the GP-X1-002 H2 candidate."""
from __future__ import annotations
import copy, json, subprocess
from pathlib import Path
from extract_glyph_identity_runtime_tables import TABLE_SYMBOL_TO_NAME, _parse_generated_raw_tables
from source_owned_generator_modes import table_digest, tables_digest

ROOT=Path(__file__).resolve().parents[1]
BASE="34a6c1bc9a9e13dcdf412c8b56a5c53011383503"
TABLE="src/modes/runtime_config/generated_source_owned/GeneratedRuntimeConfigBaseline.current.hpp"
INTAKE="docs/runtime_config/intakes/x1_normal_restoration_overlay_hardware_candidate.intake.json"
PROTOCOL="docs/agent_framework/GP_X1_002_HARDWARE_PROTOCOL.md"
EXPECTED=((93,51),(128,51),(163,51),(93,128),(128,128),(163,128),(93,205),(128,205),(163,205))
OLD=((87,87),(128,87),(169,87),(87,128),(128,128),(169,128),(87,169),(128,169),(169,169))
ALLOWED={
 "docs/agent_framework/GP_X1_002_HARDWARE_PROTOCOL.md",
 "docs/agent_framework/SUBAGENT_CONTRACTS.md",
 "docs/runtime_config/current_x1_regression_subset.md",
 "docs/runtime_config/fixtures/current_x1_regression_subset.json",
 "docs/runtime_config/fixtures/glyph_checker_census.json",
 "docs/runtime_config/fixtures/runtime_config_validation_health.json",
 "docs/runtime_config/fixtures/runtime_config_validation_manifest.json",
 "docs/runtime_config/intakes/x1_normal_restoration_overlay_hardware_candidate.intake.json",
 "docs/runtime_config/runtime_config_validation_health.md",
 "docs/runtime_config/source_authority_intake_workflow.md",
 TABLE,
 "tools/check_glyph_current_x1_regression_subset.py",
 "tools/check_glyph_gp_x1_002_candidate.py",
 "tools/check_glyph_source_owned_source_authority_intake.py",
 "tools/check_glyph_runtime_config_source_sync.py",
 "tools/check_glyph_runtime_config_validation_health.py",
 "tools/source_owned_source_authority_intake.py",
}
def run(*args:str)->str:
 return subprocess.check_output(args,cwd=ROOT,text=True)
def fail(msg:str)->None: raise AssertionError(msg)

def validate_intake(intake:dict, base_tables:dict)->None:
 if intake.get("intake_id")!="x1-normal-restoration-overlay-hardware-candidate-2026-09-21": fail("intake identity mismatch")
 if intake.get("profile_id")!="glyph_x1_normal_restoration_overlay_hardware_candidate": fail("profile identity mismatch")
 if intake.get("authority",{}).get("approval_reference")!="docs/agent_framework/USER_DIRECTION.md#glyph-ud-018": fail("authority locator mismatch")
 if intake.get("intent")!={"controller_scope":"Glyph Mk6","generation_mode":"overlay_preserve","provenance_class":"production_authorized","requested_operation":"production_changeset","source_owned_runtime_tables":True}: fail("intake intent mismatch")
 ownership=intake.get("ownership",{})
 if ownership.get("owned_tables")!=["kX1Table"] or ownership.get("unlisted_tables_are_unowned") is not True: fail("ownership expanded")
 declarations=ownership.get("declarations")
 if not isinstance(declarations,list) or len(declarations)!=1 or declarations[0].get("table_symbol")!="kX1Table" or declarations[0].get("authorization_reference")!="docs/agent_framework/USER_DIRECTION.md#glyph-ud-018": fail("ownership declaration mismatch")
 replacements=intake.get("replacements")
 if not isinstance(replacements,list) or len(replacements)!=1 or replacements[0].get("table_symbol")!="kX1Table" or replacements[0].get("source_reference")!="docs/agent_framework/USER_DIRECTION.md#glyph-ud-018": fail("replacement authority mismatch")
 points=replacements[0].get("points",[])
 if [p.get("direction_key") for p in points]!=list(range(1,10)): fail("direction ordering mismatch")
 if tuple((p.get("x"),p.get("y")) for p in points)!=EXPECTED: fail("intake rows mismatch")
 ordered=[]
 for table_id,(symbol,name) in enumerate(TABLE_SYMBOL_TO_NAME):
  ordered.append({"table_id":table_id,"table_symbol":symbol,"table_name":name,"points":[{"x":x,"y":y} for x,y in base_tables[name]]})
 expected_inventory=[{"table_id":t["table_id"],"table_symbol":t["table_symbol"],"table_digest":table_digest(t)} for t in ordered]
 baseline=intake.get("baseline",{})
 if baseline.get("semantic_digest")!=tables_digest(ordered): fail("stale baseline digest")
 if baseline.get("table_count")!=28 or baseline.get("table_inventory")!=expected_inventory: fail("baseline inventory mismatch")
 if baseline.get("table_order")!=[s for s,_ in TABLE_SYMBOL_TO_NAME]: fail("baseline order mismatch")

def adversarial(intake:dict,base_tables:dict)->None:
 cases=[]
 for label,change in (
  ("offset41",lambda p:p["replacements"][0].update(points=[{"direction_key":i,"x":x,"y":y} for i,(x,y) in enumerate(OLD,1)])),
  ("expanded",lambda p:p["ownership"]["owned_tables"].append("kMX1Table")),
  ("locator",lambda p:p["authority"].update(approval_reference="external")),
  ("stale",lambda p:p["baseline"].update(semantic_digest="0"*64)),
 ):
  q=copy.deepcopy(intake); change(q); cases.append((label,q))
 q=copy.deepcopy(intake); q["replacements"][0]["points"][0]["x"]=94; cases.append(("tampered",q))
 q=copy.deepcopy(intake); q["replacements"][0]["points"][0],q["replacements"][0]["points"][1]=q["replacements"][0]["points"][1],q["replacements"][0]["points"][0]; cases.append(("reordered",q))
 q=copy.deepcopy(intake); q["replacements"][0]["points"][0]["x"]=87; cases.append(("mixed",q))
 for label,q in cases:
  try: validate_intake(q,base_tables)
  except AssertionError: continue
  fail("adversarial intake accepted: "+label)

def main()->int:
 if run("git","merge-base",BASE,"HEAD").strip()!=BASE: fail("candidate base ancestry mismatch")
 changed=set(run("git","diff","--name-only",BASE,"--").splitlines())
 if changed-ALLOWED: fail("unexpected changed paths: "+", ".join(sorted(changed-ALLOWED)))
 base_text=run("git","show",f"{BASE}:{TABLE}")
 current=(ROOT/TABLE).read_text()
 base_tables=_parse_generated_raw_tables(base_text)
 current_tables=_parse_generated_raw_tables(current)
 if base_tables["X1"]!=OLD: fail("base kX1Table identity drift")
 if current_tables["X1"]!=EXPECTED: fail("restored kX1Table mismatch")
 for symbol,points in base_tables.items():
  if symbol!="X1" and current_tables.get(symbol)!=points: fail(f"unowned table changed: {symbol}")
 for path in ("src/modes/Ultimate.cpp","src/modes/UltimateRuntimeConfigInterpreter.hpp","src/modes/UltimateIdentityRuntimeTables.hpp","platformio.ini","config/glyph/env.ini"):
  if run("git","show",f"{BASE}:{path}")!=(ROOT/path).read_text(): fail(f"protected route/build input changed: {path}")
 intake=json.loads((ROOT/INTAKE).read_text())
 validate_intake(intake,base_tables)
 adversarial(intake,base_tables)
 protocol=(ROOT/PROTOCOL).read_text()
 for required in ("GP_X1_002_HW_V1","logical input `LT5`","Mode+X1/`kMX1Table`","Nunchuk"):
  if required not in protocol: fail("protocol contract missing: "+required)
 print("glyph_gp_x1_002_candidate: PASS")
 return 0
if __name__=="__main__": raise SystemExit(main())
