#!/usr/bin/env python3
"""Generate the deterministic, static census of Glyph checker scripts.

This deliberately never imports or executes a discovered checker.  Signals are
AST/text observations only; they are prompts for curated review, not claims
about a checker's runtime behaviour.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "docs/runtime_config/fixtures/glyph_checker_census.json"
SCHEMA_VERSION = 1

REFERENCE_PATTERNS = {
    "runtime_config": r"runtime[_-]?config",
    "source_owned": r"source[_-]?owned",
    "coordinate_native": r"coordinate[_-]?native",
    "identity_runtime_tables": r"UltimateIdentityRuntimeTables",
    "generated_source_owned_artifacts": r"GeneratedRuntimeConfigBaseline|generated[_-]?source[_-]?owned",
    "y2_tilt3": r"(?:\bY2\b|\bTilt3\b|kY2Table|kTilt3Table)",
    "candidate_generation": r"candidate[_ -]?(?:generation|diff|prepare)|prepare[_-]?source[_-]?owned[_-]?candidate",
    "hardware_results": r"hardware[_ -]?(?:result|pass|fail)|HARDWARE_(?:PASS|FAIL)",
    "docs_navigation": r"docs[_ -]?navigation|docs/",
    "agent_framework": r"agent[_ -]?(?:framework|surface|sequence)|docs/agent_framework",
}
STRONG_RELEVANCE = {
    "runtime_config_docs": r"docs/runtime_config",
    "identity_runtime_tables": r"UltimateIdentityRuntimeTables",
    "runtime_config_interpreter": r"UltimateRuntimeConfigInterpreter",
    "generated_baseline": r"GeneratedRuntimeConfigBaseline\.current\.hpp",
    "source_owned_generator_modes": r"source_owned_generator_modes",
    "source_authority_intake": r"source_owned_source_authority_intake",
    "coordinate_native_profile": r"coordinate_native_runtime_profile",
    "generated_source_owned": r"generated_source_owned",
    "candidate_generation": r"candidate[_ -]?(?:generation|diff)",
    "current_y2_layout": r"latest_y2_layout_source_owned_port|kY2Table|kTilt3Table",
    "activation_alternatives": r"runtime_config_activation_alternatives",
}
PATH_PREFIX = re.compile(r"(?:docs|src|include|HAL|hal|backend|lib|tools)/[A-Za-z0-9_./-]+")
BRANCH = re.compile(r"(?:origin/)?(?:configurator|[A-Za-z0-9._-]*(?:branch|candidate|evidence)[A-Za-z0-9._/-]*)")


def call_name(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        parent = call_name(node.value)
        return f"{parent}.{node.attr}" if parent else node.attr
    return None


class Facts(ast.NodeVisitor):
    def __init__(self) -> None:
        self.imports: set[str] = set()
        self.calls: set[str] = set()
        self.has_main = False
        self.imports_argparse = False

    def visit_Import(self, node: ast.Import) -> None:
        for item in node.names:
            self.imports.add(item.name)
            self.imports_argparse |= item.name == "argparse"

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        if node.module:
            self.imports.add(node.module)
            self.imports_argparse |= node.module == "argparse"

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self.has_main |= node.name == "main"
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self.has_main |= node.name == "main"
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        name = call_name(node.func)
        if name:
            self.calls.add(name)
        self.generic_visit(node)


def duplicate_pairs(items: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in items:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def entry(path: Path) -> dict[str, object]:
    relative = path.relative_to(ROOT).as_posix()
    raw = path.read_bytes()
    text = raw.decode("utf-8", errors="replace")
    parse_error = None
    facts = Facts()
    try:
        facts.visit(ast.parse(text, filename=relative))
    except SyntaxError as exc:
        parse_error = f"{exc.msg} (line {exc.lineno}, column {exc.offset})"
    calls = facts.calls
    local_modules = sorted(name for name in facts.imports if name == "glyph_checker_context" or name.startswith("tools."))
    mutation_calls = {"Path.write_text", "Path.write_bytes", "Path.unlink", "Path.rename", "Path.replace", "os.remove", "os.rename", "shutil.rmtree", "subprocess.run", "subprocess.check_call", "subprocess.check_output"}
    mutation = sorted(call for call in calls if call in mutation_calls)
    lowered = text.lower()
    if re.search(r"\bgit\s+(?:add|commit|checkout|switch|merge|push|reset|clean|stash|rebase|revert)\b", text):
        mutation.append("git_mutating_command_literal")
    static = {key: bool(re.search(pattern, text, re.IGNORECASE)) for key, pattern in REFERENCE_PATTERNS.items()}
    relevance = sorted(key for key, pattern in STRONG_RELEVANCE.items() if re.search(pattern, text, re.IGNORECASE))
    return {
        "checker_id": path.stem.removeprefix("check_glyph_"),
        "path": relative,
        "sha256": hashlib.sha256(raw).hexdigest(),
        "python_module": relative.removesuffix(".py").replace("/", "."),
        "file_size_bytes": len(raw),
        "line_count": len(text.splitlines()),
        "defines_main": facts.has_main,
        "imports_argparse": facts.imports_argparse,
        "invokes_subprocess": any(call.startswith("subprocess.") for call in calls),
        "invokes_git": bool(re.search(r"\bgit\b", text)),
        "imports_glyph_checker_context": "glyph_checker_context" in facts.imports or "tools.glyph_checker_context" in facts.imports,
        "imported_local_modules": local_modules,
        "referenced_repository_path_prefixes": sorted(set(PATH_PREFIX.findall(text))),
        "hard_coded_branch_like_strings": sorted(set(BRANCH.findall(text))),
        "static_signals": static,
        "potential_mutation_signals": sorted(set(mutation)),
        "potential_branch_identity_signals": sorted(set(BRANCH.findall(text))),
        "argument_requirement_signals": {"imports_argparse": facts.imports_argparse, "parser_add_argument_calls": sum(1 for call in calls if call.endswith("add_argument"))},
        "runtime_config_relevance_signals": relevance,
        "parse_error": parse_error,
    }


def generate() -> dict[str, object]:
    paths = sorted((ROOT / "tools").glob("check_glyph_*.py"), key=lambda item: item.relative_to(ROOT).as_posix())
    entries = [entry(path) for path in paths]
    ids = [item["checker_id"] for item in entries]
    names = [item["path"] for item in entries]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate checker IDs discovered")
    if len(names) != len(set(names)):
        raise ValueError("duplicate checker paths discovered")
    return {"schema_version": SCHEMA_VERSION, "generated_by": "tools/generate_glyph_checker_census.py", "entries": entries}


def rendered(value: dict[str, object]) -> str:
    return json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail if the committed artifact differs")
    args = parser.parse_args()
    output = rendered(generate())
    if args.check:
        if not ARTIFACT.is_file() or ARTIFACT.read_text(encoding="utf-8") != output:
            print("glyph_checker_census: FAIL: artifact drift; run tools/generate_glyph_checker_census.py")
            return 1
        print(f"glyph_checker_census: PASS; entries={len(generate()['entries'])}")
        return 0
    ARTIFACT.write_text(output, encoding="utf-8")
    print(f"glyph_checker_census: generated {ARTIFACT.relative_to(ROOT)}; entries={len(generate()['entries'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
