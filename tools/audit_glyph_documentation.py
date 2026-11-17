#!/usr/bin/env python3
"""One-shot, read-only Git-tree audit; exhaustive output belongs outside the checkout.

No discovered code is imported/executed. Classifications and scanner matches are
review candidates, never semantic review, deletion authority, or privacy clearance.
"""
from __future__ import annotations

import argparse
import ast
from collections import Counter
import gzip
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import zipfile

DIMENSIONS = ("content", "relevance", "machine_role", "protection", "privacy",
              "destination", "extraction", "review")
IDENTITY = ("path", "mode", "type", "oid", "size")
LIMIT = 8 * 1024 * 1024
SHA = re.compile(r"[0-9a-f]{40}")
PATH_TOKEN = re.compile(r"(?<![\w/])(?:docs|tools|src|include|config|HAL|lib|profiles|schema|schemas|scripts|\.github|builder_scripts)/[\w./@+-]+")
LINK = re.compile(r"\[[^\]\n]*\]\(([^)\s]+)(?:\s+[^)]*)?\)")
PRIVATE = {
    "local_path": re.compile(r"(?:/Users/|/home/|/private/|/tmp/|[A-Za-z]:\\Users\\)[^\s\"'`<>]+"),
    "email": re.compile(r"(?<![\w.+-])[\w.+-]{1,64}@[\w.-]{1,253}\.[A-Za-z]{2,24}(?![A-Za-z])"),
    "credential_candidate": re.compile(r"(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----|AKIA[A-Z0-9]{16})"),
}


def git(repo, *args, input=None):
    return subprocess.run(["git", "-C", str(repo), *args], input=input,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True).stdout


def strict_json(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError("duplicate JSON key")
            result[key] = value
        return result
    def constant(_):
        raise ValueError("non-finite JSON number")
    return json.loads(raw, object_pairs_hook=pairs, parse_constant=constant)


def render(value):
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True,
                       allow_nan=False) + "\n").encode()


def tree(repo, baseline):
    if not SHA.fullmatch(baseline):
        raise ValueError("baseline must be a full immutable SHA-1")
    if git(repo, "rev-parse", "--verify", baseline + "^{commit}").decode().strip() != baseline:
        raise ValueError("baseline must name a commit")
    records = []
    for entry in git(repo, "ls-tree", "-r", "-t", "-l", "-z", baseline).split(b"\0"):
        if not entry:
            continue
        meta, path = entry.split(b"\t", 1)
        mode, kind, oid, size = meta.decode("ascii").split()
        records.append(dict(path=os.fsdecode(path), mode=mode, type=kind, oid=oid,
                            size=None if size == "-" else int(size)))
    return sorted(records, key=lambda r: os.fsencode(r["path"]))


def classify(record):
    path = record["path"]
    suffix = PurePosixPath(path).suffix.lower()
    content = ("tree" if record["type"] == "tree" else "gitlink" if record["type"] == "commit"
               else "symlink" if record["mode"] == "120000" else
               {".md": "prose", ".py": "tool", ".json": "structured", ".gz": "compressed",
                ".zip": "compressed", ".cpp": "source", ".hpp": "source", ".h": "source",
                ".c": "source", ".proto": "schema"}.get(suffix, "other"))
    return dict(content=content, relevance="UNREVIEWED", machine_role="UNRESOLVED",
                protection="PRESERVE_PENDING_REVIEW", privacy="UNREVIEWED",
                destination="RETAIN_PENDING_DEPENDENCY_AND_FACT_REVIEW",
                extraction="UNREVIEWED", review="UNREVIEWED")


def inventory(repo, baseline):
    return dict(schema=1, baseline=baseline,
                tree=git(repo, "rev-parse", baseline + "^{tree}").decode().strip(),
                records=[dict(r, classification=classify(r)) for r in tree(repo, baseline)])


def validate(repo, baseline, value):
    expected = inventory(repo, baseline)
    if set(value) != set(expected) or value["schema"] != 1 or value["baseline"] != baseline or value["tree"] != expected["tree"]:
        raise ValueError("inventory header mismatch")
    rows = value["records"]
    if not isinstance(rows, list) or len(rows) != len(expected["records"]):
        raise ValueError("inventory coverage mismatch")
    seen = set()
    for actual, wanted in zip(rows, expected["records"]):
        if not isinstance(actual, dict) or set(actual) != set(wanted):
            raise ValueError("inventory record shape mismatch")
        if actual["path"] in seen:
            raise ValueError("duplicate inventory path")
        seen.add(actual["path"])
        if any(actual[k] != wanted[k] for k in IDENTITY):
            raise ValueError("inventory identity/order mismatch")
        dimensions = actual["classification"]
        if not isinstance(dimensions, dict) or set(dimensions) != set(DIMENSIONS) or any(not isinstance(v, str) or not v for v in dimensions.values()):
            raise ValueError("invalid classification dimensions")
    return True


def blobs(repo, records):
    # One immutable object stream. No filesystem traversal, symlink following or checkout reads.
    ids = sorted({r["oid"] for r in records if r["type"] == "blob"})
    raw = git(repo, "cat-file", "--batch", input=("\n".join(ids) + "\n").encode())
    pos = 0
    result = {}
    for oid in ids:
        end = raw.index(b"\n", pos)
        got, kind, size = raw[pos:end].decode().split()
        if got != oid or kind != "blob":
            raise ValueError("unexpected object response")
        pos = end + 1
        size = int(size)
        result[oid] = raw[pos:pos + size]
        if len(result[oid]) != size or raw[pos + size:pos + size + 1] != b"\n":
            raise ValueError("truncated object stream")
        pos += size + 1
    if pos != len(raw):
        raise ValueError("unexpected trailing object data")
    return result


def privacy_hits(text):
    return [dict(category=kind, line=text.count("\n", 0, m.start()) + 1, value=m.group())
            for kind, pattern in PRIVATE.items() for m in pattern.finditer(text)]


def resolve(source, token, paths):
    token = token.split("#", 1)[0].split("?", 1)[0]
    if not token:
        return source
    # Normalize relative Markdown/import paths without accessing the filesystem.
    for candidate in (token, str(PurePosixPath(source).parent / token)):
        parts = []
        for part in candidate.split("/"):
            if part == "..":
                if not parts:
                    break
                parts.pop()
            elif part not in ("", "."):
                parts.append(part)
        else:
            normalized = "/".join(parts)
            if normalized in paths:
                return normalized
    return None


def scan(repo, inv):
    records = inv["records"]
    paths = {r["path"] for r in records}
    objects = blobs(repo, records)
    dependencies, privacy, coverage, sections, containers = [], [], [], [], []
    expanded_total = 0
    expansion_budget = 256 * 1024 * 1024

    def inspect(source, raw, oid, container=False):
        if len(raw) > LIMIT:
            coverage.append(dict(path=source, status="OVERSIZE_UNREVIEWED", oid=oid))
            return
        try:
            text = raw.decode("utf-8")
            if "\0" in text:
                raise UnicodeError()
        except UnicodeError:
            coverage.append(dict(path=source, status="BINARY_METADATA_UNREVIEWED", oid=oid))
            return
        coverage.append(dict(path=source, status="SCANNED_NOT_SEMANTICALLY_REVIEWED", oid=oid))
        privacy.extend(dict(path=source, oid=oid, **v) for v in privacy_hits(text))
        if source.endswith(".json"):
            try:
                strict_json(text)
            except (ValueError, TypeError):
                coverage[-1]["json_status"] = "INVALID_OR_DUPLICATE_KEYS"
            else:
                coverage[-1]["json_status"] = "STRICT_PARSE_PASS"
        lines = text.splitlines()
        headings = [(n, line) for n, line in enumerate(lines, 1) if re.match(r"^#{1,6} ", line)]
        if source.endswith(".md"):
            starts = [(1, "preamble")] + headings if not headings or headings[0][0] != 1 else headings
            for index, (start, heading) in enumerate(starts):
                end = starts[index + 1][0] - 1 if index + 1 < len(starts) else len(lines)
                sections.append(dict(path=source, oid=oid, start=start, end=end,
                                     heading=heading, extraction="UNREVIEWED", review="UNREVIEWED"))
        for n, line in enumerate(lines, 1):
            candidates = [("prose_or_code_path", m.group()) for m in PATH_TOKEN.finditer(line)]
            candidates += [("markdown_link", m.group(1)) for m in LINK.finditer(line)]
            candidates += [("private_locator", m.group()) for m in re.finditer(r"(?:local_backups/|/Users/|/private/|/tmp/)[^\s\"\'`<>]+", line)]
            candidates += [("external_url", m.group()) for m in re.finditer(r"https?://[^\s\"\'`<>]+", line)]
            candidates += [("git_ref_candidate", m.group()) for m in re.finditer(r"(?:refs/[\w./-]+|origin/configurator|codex/[\w./-]+)", line)]
            candidates += [("git_object_reference", m.group()) for m in re.finditer(r"(?<![0-9a-f])[0-9a-f]{40}(?![0-9a-f])", line)]
            for kind, token in candidates:
                external = token.startswith(("http:", "https:", "mailto:", "plugin:"))
                private = token.startswith(("/Users/", "/private/", "/tmp/", "local_backups/"))
                target = None if external or kind in ("git_object_reference", "git_ref_candidate") else resolve(source.split("!", 1)[0], token, paths)
                dependencies.append(dict(source=source, oid=oid, line=n, kind=kind, token=token,
                    target=target, anchor=token.split("#", 1)[1] if "#" in token else None,
                    classification="EXTERNAL_SOURCE" if external else "PRIVATE_LOCATOR" if private else
                    "RESOLVED_CANDIDATE_NOT_ACTIVE_PROOF" if target else "UNRESOLVED_CANDIDATE",
                    review="UNREVIEWED"))
        if source.endswith(".py"):
            try:
                module = ast.parse(text)
            except (SyntaxError, ValueError):
                coverage[-1]["ast_status"] = "PARSE_FAILED"
            else:
                for node in ast.walk(module):
                    names = []
                    if isinstance(node, ast.Import):
                        names = [v.name for v in node.names]
                    elif isinstance(node, ast.ImportFrom):
                        names = [node.module or ""]
                    for name in names:
                        target = resolve(source, "tools/" + name.replace(".", "/") + ".py", paths)
                        dependencies.append(dict(source=source, oid=oid, line=node.lineno,
                            kind="python_import", token=name, target=target,
                            classification="RESOLVED_CANDIDATE_NOT_ACTIVE_PROOF" if target else "EXTERNAL_OR_UNRESOLVED_IMPORT", review="UNREVIEWED"))
                    if isinstance(node, (ast.JoinedStr, ast.BinOp)):
                        segment = "\n".join(lines[node.lineno - 1:min(getattr(node, "end_lineno", node.lineno), node.lineno + 8)])
                        if "/" in segment or "Path" in segment:
                            dependencies.append(dict(source=source, oid=oid, line=node.lineno,
                                kind="constructed_expression", token=segment[:500], target=None,
                                classification="UNRESOLVED_CANDIDATE", review="UNREVIEWED"))

    for record in records:
        if record["type"] != "blob":
            continue
        source, oid = record["path"], record["oid"]
        raw = objects[oid]
        privacy.extend(dict(path=source, oid=oid, surface="filename", **v) for v in privacy_hits(source))
        inspect(source, raw, oid)
        if source.endswith((".gz", ".zip")) and expanded_total + LIMIT + 1 > expansion_budget:
            containers.append(dict(path=source, status="TOTAL_EXPANSION_BUDGET_UNREVIEWED"))
            continue
        if source.endswith(".gz"):
            try:
                with gzip.GzipFile(fileobj=io.BytesIO(raw)) as stream:
                    expanded = stream.read(LIMIT + 1)
                expanded_total += len(expanded)
                inspect(source + "!gzip", expanded, oid, True)
                containers.append(dict(path=source, status="BOUNDED_GZIP_SCAN", expanded_bytes=len(expanded)))
            except (OSError, EOFError, ValueError):
                containers.append(dict(path=source, status="INVALID_GZIP"))
        elif source.endswith(".zip"):
            try:
                with zipfile.ZipFile(io.BytesIO(raw)) as archive:
                    total = 0
                    for member in archive.infolist():
                        if member.is_dir():
                            continue
                        if member.file_size > LIMIT or total + member.file_size > LIMIT or expanded_total + member.file_size > expansion_budget:
                            containers.append(dict(path=source, member=member.filename, status="SIZE_LIMIT_UNREVIEWED"))
                            continue
                        with archive.open(member) as stream:
                            expanded = stream.read(LIMIT + 1)
                        total += len(expanded)
                        expanded_total += len(expanded)
                        inspect(source + "!" + member.filename, expanded, oid, True)
                        containers.append(dict(path=source, member=member.filename, status="BOUNDED_ZIP_SCAN"))
            except (OSError, RuntimeError, zipfile.BadZipFile, NotImplementedError):
                containers.append(dict(path=source, status="UNAVAILABLE_ZIP_SCAN"))
    return dict(schema=1, baseline=inv["baseline"], dependencies=dependencies,
                privacy_candidates=privacy, scan_coverage=coverage, sections=sections,
                containers=containers, limitations=[
                    "All automated classifications are candidates, not semantic review or active dependency proof.",
                    "Only full Git-tree blobs; no untracked/private originals, remote discussions, LFS payloads or device bytes.",
                    "UTF-8 text <=8MiB; gzip <=8MiB; zip <=8MiB per archive; expansion <=256MiB per run; no execution/extraction.",
                    "No general C++/shell dataflow, transitive import evaluation, branch reachability or constructed-path resolution.",
                    "Markdown targets resolved lexically; anchors recorded but not validated; escaped/reference/HTML links may be missed.",
                    "Credential/path/email patterns are incomplete; binaries/media metadata and compressed opaque formats need later inspection.",
                    "JSON parse failures recorded, not repaired; duplicate blobs remain individually inventoried; no deletion inference."])


def write_private(path, value):
    # No overwrites/symlink traversal of existing output files.
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "wb") as stream:
        stream.write(render(value))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--baseline", required=True)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--output", type=Path, help="new private output directory outside checkout")
    action.add_argument("--validate", type=Path, help="validate an existing inventory against Git")
    args = parser.parse_args()
    try:
        repo = Path(os.fsdecode(git(args.repo, "rev-parse", "--show-toplevel")).strip()).resolve()
        if args.validate:
            validate(repo, args.baseline, strict_json(args.validate.read_bytes()))
            print("inventory validation: PASS")
            return 0
        output = args.output.absolute()
        resolved = output.resolve()
        if resolved == repo or repo in resolved.parents or output.is_symlink():
            raise ValueError("output must be outside checkout and not a symlink")
        output.mkdir(mode=0o700, parents=False, exist_ok=False)
        inv = inventory(repo, args.baseline)
        validate(repo, args.baseline, inv)
        result = scan(repo, inv)
        write_private(output / "inventory.json", inv)
        write_private(output / "scan.json", result)
        summary = dict(schema=1, baseline=args.baseline, paths=len(inv["records"]),
                       types=dict(Counter(r["type"] for r in inv["records"])),
                       blob_bytes=sum(r["size"] or 0 for r in inv["records"] if r["type"] == "blob"),
                       sections=len(result["sections"]), semantic_reviewed_by_tool=0,
                       dependency_candidates=len(result["dependencies"]),
                       privacy_candidate_categories=dict(Counter(r["category"] for r in result["privacy_candidates"])),
                       inventory_sha256=hashlib.sha256(render(inv)).hexdigest(),
                       scan_sha256=hashlib.sha256(render(result)).hexdigest())
        write_private(output / "summary.json", summary)
        # Fixed stdout; paths, sensitive matches and exception text are never printed.
        print("private audit generated; semantic review and privacy clearance remain outstanding")
        return 0
    except (ValueError, OSError, subprocess.CalledProcessError, KeyError, TypeError):
        print("audit: FAIL; inspect inputs privately")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
