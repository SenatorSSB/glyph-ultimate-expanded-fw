#!/usr/bin/env python3
"""Offline, source-owned generator-mode contracts.

This module deliberately stops at complete inert artifacts and manifests.  It
does not select a RuntimeConfigView, write device state, build, or flash.
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any, Iterable

if str(Path(__file__).resolve().parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parent))

try:
    from generate_source_owned_runtime_config import parse_source_owned_baseline_contract
except ModuleNotFoundError:  # pragma: no cover - package-style imports
    from tools.generate_source_owned_runtime_config import parse_source_owned_baseline_contract


INPUT_SCHEMA_VERSION = 2
ARTIFACT_SCHEMA_VERSION = 1
MANIFEST_SCHEMA_VERSION = 1
PREPARED_SCHEMA_VERSION = 1
TABLE_COUNT = 28
POINTS_PER_TABLE = 9
AXES_PER_POINT = 2
GENERATOR_VERSION = "1.0.0"
MODES = {"full_replacement", "overlay_preserve", "reject_partial"}
PROVENANCE = {
    "production_authorized",
    "source_baseline_derived",
    "synthetic_test",
    "example_only",
    "migrated_legacy",
    "unknown",
}
PRODUCTION_ALLOWED = {"production_authorized", "source_baseline_derived"}
EXIT_CODES = {
    "success": 0,
    "invalid_input": 2,
    "source_authority": 3,
    "baseline_mismatch": 4,
    "unsafe_unowned_change": 5,
    "candidate_ineligible": 6,
    "integrity": 7,
    "invariant": 8,
}


class GeneratorModesError(ValueError):
    """Expected contract failure with a stable error category."""

    def __init__(self, message: str, category: str = "invalid_input") -> None:
        super().__init__(message)
        self.category = category


def _fail(message: str, category: str = "invalid_input") -> None:
    raise GeneratorModesError(message, category)


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":"))


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _object_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            _fail(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_object_pairs)
    except (OSError, json.JSONDecodeError) as exc:
        _fail(f"cannot read JSON {path}: {exc}", "integrity")
    if not isinstance(value, dict):
        _fail("JSON root must be an object")
    return value


def _str(label: str, value: Any) -> str:
    if not isinstance(value, str) or not value:
        _fail(f"{label} must be a non-empty string")
    return value


def _int(label: str, value: Any, low: int = 0, high: int = 255) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or not low <= value <= high:
        _fail(f"{label} must be an integer in [{low}, {high}]")
    return value


def _baseline_tables() -> list[dict[str, Any]]:
    raw = parse_source_owned_baseline_contract()
    tables = raw["tables"]
    if len(tables) != TABLE_COUNT:
        _fail(f"authoritative baseline has {len(tables)} tables, expected {TABLE_COUNT}", "integrity")
    return [
        {
            "table_id": i,
            "table_symbol": _str(f"baseline.tables[{i}].table_symbol", table["table_symbol"]),
            "table_name": _str(f"baseline.tables[{i}].table_name", table["table_name"]),
            "points": [{"x": _int("x", p["x"]), "y": _int("y", p["y"])} for p in table["points"]],
        }
        for i, table in enumerate(tables)
    ]


def table_digest(table: dict[str, Any]) -> str:
    return digest({"table_id": table["table_id"], "table_symbol": table["table_symbol"], "points": table["points"]})


def tables_digest(tables: Iterable[dict[str, Any]]) -> str:
    return digest([
        {"table_id": t["table_id"], "table_symbol": t["table_symbol"], "points": t["points"]}
        for t in tables
    ])


def baseline_identity() -> dict[str, Any]:
    tables = _baseline_tables()
    return {
        "baseline_id": "current_source_owned_baseline",
        "source_path": "src/modes/UltimateIdentityRuntimeTables.hpp",
        "source_interpreter": "src/modes/UltimateRuntimeConfigInterpreter.hpp",
        "semantic_digest": tables_digest(tables),
        "table_count": TABLE_COUNT,
        "table_order": [t["table_symbol"] for t in tables],
        "artifact_format_version": ARTIFACT_SCHEMA_VERSION,
    }


def _validate_table(label: str, raw: Any, expected_id: int | None = None) -> dict[str, Any]:
    if not isinstance(raw, dict):
        _fail(f"{label} must be an object")
    required = {"table_id", "table_symbol", "points"}
    missing = sorted(required - set(raw))
    if missing:
        _fail(f"{label} missing: {', '.join(missing)}")
    extra = sorted(set(raw) - required - {"table_name"})
    if extra:
        _fail(f"{label} has unexpected keys: {', '.join(extra)}")
    table_id = _int(f"{label}.table_id", raw["table_id"], 0, TABLE_COUNT - 1)
    if expected_id is not None and table_id != expected_id:
        _fail(f"{label}.table_id must be {expected_id}")
    symbol = _str(f"{label}.table_symbol", raw["table_symbol"])
    points = raw["points"]
    if not isinstance(points, list) or len(points) != POINTS_PER_TABLE:
        _fail(f"{label}.points must contain exactly {POINTS_PER_TABLE} entries")
    normalized = []
    for i, point in enumerate(points):
        if not isinstance(point, dict) or set(point) != {"x", "y"}:
            _fail(f"{label}.points[{i}] must contain x and y only")
        normalized.append({"x": _int(f"{label}.points[{i}].x", point["x"]), "y": _int(f"{label}.points[{i}].y", point["y"])})
    return {"table_id": table_id, "table_symbol": symbol, "table_name": raw.get("table_name", symbol.removeprefix("k").removesuffix("Table")), "points": normalized}


def validate_baseline_reference(reference: Any, actual: dict[str, Any]) -> None:
    if not isinstance(reference, dict):
        _fail("baseline identity is required", "baseline_mismatch")
    for key in ("baseline_id", "source_path", "semantic_digest", "table_count"):
        if reference.get(key) != actual[key]:
            _fail(f"baseline {key} does not match authoritative source", "baseline_mismatch")


def validate_input(payload: dict[str, Any], *, allow_legacy: bool = False) -> dict[str, Any]:
    if allow_legacy and payload.get("schema_version") == 1 and "owned_tables" not in payload:
        _fail("legacy input without explicit ownership is SOURCE_AUTHORITY_BLOCKER", "source_authority")
    required = {"schema_version", "profile_id", "profile_name", "provenance_class", "generation_mode", "tables"}
    missing = sorted(required - set(payload))
    if missing:
        if "generation_mode" in missing:
            _fail("generation_mode is mandatory")
        if "provenance_class" in missing:
            _fail("provenance_class is mandatory")
        _fail(f"input missing: {', '.join(missing)}")
    version = payload["schema_version"]
    if version != INPUT_SCHEMA_VERSION:
        if allow_legacy and version == 1:
            _fail("legacy input without explicit ownership is SOURCE_AUTHORITY_BLOCKER", "source_authority")
        _fail(f"unsupported input schema_version: {version}")
    profile_id = _str("profile_id", payload["profile_id"])
    profile_name = _str("profile_name", payload["profile_name"])
    provenance = _str("provenance_class", payload["provenance_class"])
    if provenance not in PROVENANCE:
        _fail(f"unknown provenance_class: {provenance}")
    mode = _str("generation_mode", payload["generation_mode"])
    if mode not in MODES:
        _fail(f"unknown generation_mode: {mode}")
    tables_raw = payload["tables"]
    if not isinstance(tables_raw, list):
        _fail("tables must be a list")
    if mode in {"full_replacement", "reject_partial"} and len(tables_raw) != TABLE_COUNT:
        missing_ids = sorted(set(range(TABLE_COUNT)) - {t.get("table_id") for t in tables_raw if isinstance(t, dict)})
        if mode == "reject_partial":
            _fail("reject_partial rejected partial input; missing table IDs: " + ", ".join(map(str, missing_ids)))
        _fail("full_replacement requires exactly 28 tables; missing table IDs: " + ", ".join(map(str, missing_ids)))
    tables = [_validate_table(f"tables[{i}]", table) for i, table in enumerate(tables_raw)]
    ids = [t["table_id"] for t in tables]
    if len(set(ids)) != len(ids):
        _fail("duplicate table ID")
    symbols = [t["table_symbol"] for t in tables]
    if len(set(symbols)) != len(symbols):
        _fail("duplicate table symbol")
    actual_baseline = baseline_identity()
    expected_by_id = {i: symbol for i, symbol in enumerate(actual_baseline["table_order"])}
    for table in tables:
        if table["table_symbol"] != expected_by_id[table["table_id"]]:
            _fail(
                f"table_id {table['table_id']} must identify {expected_by_id[table['table_id']]!r}, "
                f"not {table['table_symbol']!r}"
            )
    if mode == "overlay_preserve":
        if "baseline" not in payload:
            _fail("overlay_preserve requires baseline identity", "baseline_mismatch")
        validate_baseline_reference(payload["baseline"], actual_baseline)
        if "owned_tables" not in payload or not isinstance(payload["owned_tables"], list):
            _fail("overlay_preserve requires explicit owned_tables")
        owned = payload["owned_tables"]
        if len(set(owned)) != len(owned):
            _fail("duplicate ownership entry")
        unknown = sorted(set(owned) - set(actual_baseline["table_order"]))
        if unknown:
            _fail("unknown owned table: " + ", ".join(unknown))
        supplied = set(symbols)
        if supplied - set(owned):
            _fail("table data present but not explicitly owned", "unsafe_unowned_change")
        if set(owned) - supplied:
            _fail("owned table missing data: " + ", ".join(sorted(set(owned) - supplied)))
    elif mode == "full_replacement":
        if "owned_tables" in payload and payload["owned_tables"]:
            _fail("full_replacement owns all tables implicitly; owned_tables is not allowed")
        if symbols != actual_baseline["table_order"]:
            _fail("full_replacement has unknown or missing table symbols")
    elif len(tables_raw) == TABLE_COUNT:
        _fail("reject_partial is validation-only; use an explicit full_replacement transition")
    return {
        "schema_version": INPUT_SCHEMA_VERSION,
        "profile_id": profile_id,
        "profile_name": profile_name,
        "provenance_class": provenance,
        "generation_mode": mode,
        "baseline": payload.get("baseline"),
        "owned_tables": list(payload.get("owned_tables", [])),
        "tables": tables,
        "metadata": payload.get("metadata", {}),
    }


def generate(payload: dict[str, Any], *, test_only: bool = False) -> tuple[dict[str, Any], dict[str, Any]]:
    value = validate_input(payload)
    mode = value["generation_mode"]
    baseline = _baseline_tables()
    base_by_symbol = {t["table_symbol"]: t for t in baseline}
    supplied = {t["table_symbol"]: t for t in value["tables"]}
    owned = set(value["owned_tables"] if mode == "overlay_preserve" else base_by_symbol)
    complete = [supplied[symbol] if symbol in supplied else base_by_symbol[symbol] for symbol in base_by_symbol]
    rows = []
    for table in complete:
        symbol = table["table_symbol"]
        changed = table["points"] != base_by_symbol[symbol]["points"]
        explicit = symbol in owned
        if mode == "full_replacement":
            action = "replace_explicit_owned"
            reason = "full replacement explicitly supplies every active table"
        elif explicit:
            action = "replace_explicit_owned"
            reason = "explicit ownership permits replacement"
        else:
            action = "preserve_source_owned_baseline"
            reason = "unowned table copied from authoritative source baseline"
        if not explicit and changed:
            _fail(f"unowned table changed from baseline: {symbol}", "unsafe_unowned_change")
        rows.append({
            "table_id": table["table_id"],
            "table_symbol": symbol,
            "action": action,
            "explicit_ownership": explicit,
            "ownership_source": "candidate_input" if explicit else "current_source_owned_baseline",
            "provenance": value["provenance_class"],
            "baseline_digest": table_digest(base_by_symbol[symbol]),
            "candidate_digest": table_digest(table),
            "changed": changed,
            "reason": reason,
        })
    changed_rows = [r for r in rows if r["changed"]]
    if not changed_rows:
        classification = "NO_OP"
    elif mode == "full_replacement":
        classification = "FULL_REPLACEMENT_CHANGESET"
    elif any(not r["explicit_ownership"] for r in changed_rows):
        classification = "UNSAFE_UNOWNED_CHANGE"
    else:
        classification = "EXPLICIT_OWNED_TABLE_CHANGESET"
    artifact = {
        "schema_version": ARTIFACT_SCHEMA_VERSION,
        "profile_id": value["profile_id"],
        "profile_name": value["profile_name"],
        "provenance_class": value["provenance_class"],
        "generation_mode": mode,
        "baseline": baseline_identity(),
        "table_shape": {"table_count": TABLE_COUNT, "points_per_table": POINTS_PER_TABLE, "axes_per_point": AXES_PER_POINT},
        "tables": complete,
        "artifact_semantic_digest": tables_digest(complete),
        "generator_version": GENERATOR_VERSION,
    }
    manifest = {
        "schema_version": MANIFEST_SCHEMA_VERSION,
        "baseline": artifact["baseline"],
        "input_profile_id": value["profile_id"],
        "input_semantic_digest": digest(value),
        "generator_version": GENERATOR_VERSION,
        "artifact_semantic_digest": artifact["artifact_semantic_digest"],
        "rows": rows,
        "changed_table_ids": [r["table_id"] for r in changed_rows],
        "preserved_table_ids": [r["table_id"] for r in rows if not r["changed"]],
        "changed_table_count": len(changed_rows),
        "preserved_table_count": len(rows) - len(changed_rows),
        "classification": classification,
    }
    manifest["manifest_semantic_digest"] = digest(manifest)
    return artifact, manifest


def validate_manifest(artifact: dict[str, Any], manifest: dict[str, Any]) -> None:
    if manifest.get("schema_version") != MANIFEST_SCHEMA_VERSION:
        _fail("unsupported manifest schema_version")
    rows = manifest.get("rows")
    if not isinstance(rows, list) or len(rows) != TABLE_COUNT:
        _fail("manifest must contain exactly 28 rows")
    if [r.get("table_id") for r in rows] != list(range(TABLE_COUNT)):
        _fail("manifest rows must be stable and ordered 0..27")
    if len({r.get("table_symbol") for r in rows}) != TABLE_COUNT:
        _fail("manifest has duplicate table rows")
    if manifest.get("artifact_semantic_digest") != artifact.get("artifact_semantic_digest"):
        _fail("manifest/artifact digest mismatch", "integrity")
    for row in rows:
        if row.get("changed") and not row.get("explicit_ownership"):
            _fail("changed manifest row is not explicitly owned", "unsafe_unowned_change")
        if not row.get("changed") and row.get("candidate_digest") != row.get("baseline_digest"):
            _fail("preserved manifest row differs from baseline", "unsafe_unowned_change")
    if manifest.get("changed_table_count") != sum(bool(r.get("changed")) for r in rows):
        _fail("manifest changed count mismatch")
    if manifest.get("preserved_table_count") != TABLE_COUNT - manifest["changed_table_count"]:
        _fail("manifest preserved count mismatch")


def production_gate(artifact: dict[str, Any], manifest: dict[str, Any], *, hardware_candidate: bool = False) -> None:
    validate_manifest(artifact, manifest)
    if artifact.get("provenance_class") not in PRODUCTION_ALLOWED:
        _fail("provenance is not allowed for production preparation/install", "source_authority")
    if artifact.get("provenance_class") == "source_baseline_derived" and manifest.get("classification") != "NO_OP":
        _fail("source_baseline_derived changes require explicit production authorization", "source_authority")
    if manifest.get("classification") in {"SOURCE_AUTHORITY_BLOCKER", "UNSAFE_UNOWNED_CHANGE"}:
        _fail("candidate classification is not eligible", "source_authority")
    if hardware_candidate and manifest.get("classification") == "NO_OP":
        _fail("NO_OP cannot be prepared as a hardware candidate", "candidate_ineligible")


def prepare(artifact: dict[str, Any], manifest: dict[str, Any], *, hardware_candidate: bool = False) -> dict[str, Any]:
    production_gate(artifact, manifest, hardware_candidate=hardware_candidate)
    packet = {
        "schema_version": PREPARED_SCHEMA_VERSION,
        "artifact": artifact,
        "manifest": manifest,
        "target": "inert_source_owned_artifact_only",
        "source_mutation": False,
    }
    packet["prepared_semantic_digest"] = digest(packet)
    return packet


def install_prepared(packet: dict[str, Any], target: Path, *, dry_run: bool = False) -> list[str]:
    if packet.get("schema_version") != PREPARED_SCHEMA_VERSION:
        _fail("unsupported prepared packet schema_version")
    artifact, manifest = packet.get("artifact"), packet.get("manifest")
    if not isinstance(artifact, dict) or not isinstance(manifest, dict):
        _fail("prepared packet requires artifact and manifest")
    production_gate(artifact, manifest)
    if packet.get("target") != "inert_source_owned_artifact_only":
        _fail("forbidden publication target", "source_authority")
    if "candidate.view" in str(target) or "active_storage.view" in str(target) or "RuntimeConfigView" in str(target):
        _fail("forbidden publication path", "source_authority")
    if not target.is_absolute():
        _fail("install target must be absolute")
    text = json.dumps(artifact, indent=2, sort_keys=True) + "\n"
    if dry_run:
        return [f"would write {target} ({len(text.encode('utf-8'))} bytes)"]
    target.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{target.name}.", dir=str(target.parent), text=True)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, target)
    except OSError as exc:
        try:
            os.unlink(temp_name)
        except OSError:
            pass
        _fail(f"atomic install failed: {exc}", "integrity")
    return [f"wrote {target}", f"artifact digest {artifact['artifact_semantic_digest']}"]
