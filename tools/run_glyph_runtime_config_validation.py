#!/usr/bin/env python3
"""Read-only deterministic aggregate runner for current runtime-config checks."""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import re
import selectors
import stat
import signal
import subprocess
import sys
import tempfile
from pathlib import Path
from pathlib import PurePosixPath
from time import monotonic, sleep

ROOT = Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT / "tools"))
from generate_glyph_checker_census import generate as generate_census, rendered as render_census  # noqa: E402

MANIFEST = ROOT / "docs/runtime_config/fixtures/runtime_config_validation_manifest.json"
CENSUS = ROOT / "docs/runtime_config/fixtures/glyph_checker_census.json"
REQUIRED = {"id", "path", "command", "category", "applicability", "branch_policy", "required_arguments", "mutation_risk", "source_dependencies", "load_bearing", "historical", "reason"}
BRANCH_POLICIES = {"content_only", "content_and_scope", "named_evidence_branch", "not_run"}
APPLICABILITIES = {"current", "historical_only", "unsafe_or_mutating"}
EXCLUSION_REQUIRED = {"id", "path", "reason", "detail"}
EXCLUSION_REASONS = {"HISTORICAL_BRANCH_EVIDENCE", "HARDWARE_RESULT_EVIDENCE", "SUPERSEDED_CONTRACT", "REQUIRES_NONCANONICAL_ARGUMENT", "UNSAFE_OR_MUTATING", "DUPLICATE_COVERAGE", "NOT_CURRENT_RUNTIME_CONFIG_LANE"}
CHECKER_TIMEOUT_SECONDS = 120.0
AGGREGATE_TIMEOUT_SECONDS = 300.0
TERM_GRACE_SECONDS = 2.0


def pairs(items: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in items:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def tracked_regular_stage_zero(path: str) -> bool:
    if not path or path.startswith("/") or "\\" in path:
        return False
    pure = PurePosixPath(path)
    if pure.as_posix() != path or any(part in {"", ".", ".."} for part in pure.parts):
        return False
    result = git("ls-files", "--stage", "--", path)
    records = [line.split("\t", 1)[0].split() for line in result.stdout.splitlines() if "\t" in line]
    return len(records) == 1 and records[0][0] in {"100644", "100755"} and (ROOT / path).is_file() and not (ROOT / path).is_symlink()


def validate_checker_command(entry: dict[str, object]) -> None:
    checker_id = entry["id"]
    path = entry["path"]
    required_arguments = entry["required_arguments"]
    command = entry["command"]
    if not isinstance(path, str) or not tracked_regular_stage_zero(path):
        raise ValueError(f"invalid checker path: {checker_id}")
    if not isinstance(required_arguments, list) or not all(isinstance(argument, str) for argument in required_arguments):
        raise ValueError(f"invalid required_arguments: {checker_id}")
    expected = ["python3", path, *required_arguments]
    if command != expected:
        raise ValueError(f"command does not match path/required_arguments: {checker_id}")


def direct_local_helpers(checker_path: str) -> set[str]:
    source = (ROOT / checker_path).read_text(encoding="utf-8")
    tree = ast.parse(source, filename=checker_path)
    found: set[str] = set()
    for node in ast.walk(tree):
        module = None
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.startswith("tools.") and alias.name.count(".") == 1:
                    candidate = f"{alias.name.replace('.', '/')}.py"
                    if tracked_regular_stage_zero(candidate):
                        found.add(candidate)
                elif "." not in alias.name and tracked_regular_stage_zero(f"tools/{alias.name}.py"):
                    found.add(f"tools/{alias.name}.py")
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            module = node.module
            if module.startswith("tools.") and module.count(".") == 1:
                candidate = f"{module.replace('.', '/')}.py"
                if tracked_regular_stage_zero(candidate):
                    found.add(candidate)
            elif "." not in module and tracked_regular_stage_zero(f"tools/{module}.py"):
                found.add(f"tools/{module}.py")
    return found


def validate_dependencies(entry: dict[str, object]) -> None:
    dependencies = entry["source_dependencies"]
    if not isinstance(dependencies, list) or not all(isinstance(path, str) for path in dependencies):
        raise ValueError(f"invalid source_dependencies: {entry['id']}")
    if len(dependencies) != len(set(dependencies)):
        raise ValueError(f"duplicate source dependency: {entry['id']}")
    for path in dependencies:
        if path == entry["path"]:
            raise ValueError(f"checker path repeated as source dependency: {entry['id']}")
        if not tracked_regular_stage_zero(path):
            raise ValueError(f"invalid source dependency path: {entry['id']}: {path}")
    required = direct_local_helpers(str(entry["path"]))
    missing = sorted(required - set(dependencies))
    if missing:
        raise ValueError(f"missing direct helper dependencies for {entry['id']}: {', '.join(missing)}")


def validate_branch_policy(entry: dict[str, object]) -> None:
    applicability, policy = entry["applicability"], entry["branch_policy"]
    if applicability not in APPLICABILITIES or policy not in BRANCH_POLICIES:
        raise ValueError(f"invalid applicability/branch_policy: {entry['id']}")
    expected = {"current": {"content_only", "content_and_scope"}, "historical_only": {"named_evidence_branch"}, "unsafe_or_mutating": {"not_run"}}[applicability]
    if policy not in expected:
        raise ValueError(f"invalid applicability/branch_policy pair: {entry['id']}")


def load() -> tuple[list[dict[str, object]], list[dict[str, object]], set[str]]:
    value = json.loads(MANIFEST.read_text(encoding="utf-8"), object_pairs_hook=pairs)
    if value.get("schema_version") != 4 or not isinstance(value.get("categories"), list) or not isinstance(value.get("entries"), list) or not isinstance(value.get("strong_signal_exclusions"), list):
        raise ValueError("invalid manifest root")
    categories = set(value["categories"])
    ids: set[str] = set()
    entries: list[dict[str, object]] = []
    for entry in value["entries"]:
        if not isinstance(entry, dict) or set(entry) != REQUIRED:
            raise ValueError(f"invalid checker entry: {entry!r}")
        checker_id = entry["id"]
        if not isinstance(checker_id, str) or checker_id in ids:
            raise ValueError(f"duplicate checker ID: {checker_id}")
        ids.add(checker_id)
        if entry["category"] not in categories:
            raise ValueError(f"invalid category: {entry['category']}")
        if not isinstance(entry["command"], list) or not all(isinstance(part, str) for part in entry["command"]):
            raise ValueError(f"invalid command: {checker_id}")
        validate_checker_command(entry)
        validate_dependencies(entry)
        validate_branch_policy(entry)
        if entry["applicability"] == "current" and (entry["historical"] or not entry["load_bearing"] or entry["required_arguments"] or entry["mutation_risk"] not in {"none", "temporary_file_only", "temporary_repository_only"}):
            raise ValueError(f"unsafe current aggregate entry: {checker_id}")
        if entry["historical"] and entry["applicability"] != "historical_only":
            raise ValueError(f"historical checker incorrectly current: {checker_id}")
        entries.append(entry)
    exclusions: list[dict[str, object]] = []
    exclusion_ids: set[str] = set()
    exclusion_paths: set[str] = set()
    entry_paths = {str(entry["path"]) for entry in entries}
    for exclusion in value["strong_signal_exclusions"]:
        if not isinstance(exclusion, dict) or set(exclusion) != EXCLUSION_REQUIRED:
            raise ValueError(f"invalid strong-signal exclusion: {exclusion!r}")
        exclusion_id, exclusion_path = exclusion["id"], exclusion["path"]
        if not isinstance(exclusion_id, str) or exclusion_id in exclusion_ids:
            raise ValueError(f"duplicate strong-signal exclusion ID: {exclusion_id}")
        if not isinstance(exclusion_path, str) or exclusion_path in exclusion_paths:
            raise ValueError(f"duplicate strong-signal exclusion path: {exclusion_path}")
        if exclusion_path in entry_paths:
            raise ValueError(f"checker appears in manifest and exclusions: {exclusion_path}")
        if exclusion["reason"] not in EXCLUSION_REASONS:
            raise ValueError(f"invalid strong-signal exclusion reason: {exclusion['reason']}")
        if not isinstance(exclusion["detail"], str) or not exclusion["detail"]:
            raise ValueError(f"invalid strong-signal exclusion detail: {exclusion_id}")
        if not exclusion_path.startswith("tools/check_glyph_") or not exclusion_path.endswith(".py") or not (ROOT / exclusion_path).is_file():
            raise ValueError(f"invalid strong-signal exclusion path: {exclusion_path}")
        exclusion_ids.add(exclusion_id)
        exclusion_paths.add(exclusion_path)
        exclusions.append(exclusion)
    census = json.loads(CENSUS.read_text(encoding="utf-8"), object_pairs_hook=pairs)
    census_entries = census.get("entries")
    if not isinstance(census_entries, list):
        raise ValueError("invalid checker census entries")
    strong_paths: set[str] = set()
    for census_entry in census_entries:
        if not isinstance(census_entry, dict) or not isinstance(census_entry.get("path"), str):
            raise ValueError("invalid checker census entry")
        signals = census_entry.get("runtime_config_relevance_signals")
        if not isinstance(signals, list) or not all(isinstance(signal, str) for signal in signals):
            raise ValueError(f"invalid checker census relevance signals: {census_entry['path']}")
        if signals:
            strong_paths.add(census_entry["path"])
    for path in sorted(strong_paths - entry_paths - exclusion_paths):
        raise ValueError(f"unclassified strong-signal checker: {path}")
    for path in sorted(exclusion_paths - strong_paths):
        raise ValueError(f"strong-signal exclusion lacks census signal: {path}")
    return entries, exclusions, categories



def census_freshness() -> dict[str, object]:
    committed = CENSUS.read_text(encoding="utf-8")
    expected = render_census(generate_census(ROOT))
    require_budget("census evaluation")
    return {
        "id": "checker_census_freshness",
        "path": "tools/check_glyph_checker_census.py",
        "category": "baseline",
        "applicability": "current",
        "load_bearing": True,
        "status": "PASS" if committed == expected else "FAIL",
    }


class AggregateTimeout(RuntimeError):
    pass


DEADLINE: float | None = None
EXECUTION_ENV: dict[str, str] | None = None
SELF_TEST_COMMANDS = {
    "checker_context": ["python3", "tools/check_glyph_checker_context.py"],
    "validation_aggregate_adversarial": ["python3", "tools/check_glyph_runtime_config_validation_aggregate.py"],
}
X1_COMMAND = ["python3", "tools/check_glyph_current_x1_regression_subset.py"]
X1_REF = "refs/heads/runtime-config-x1-offset41-hardware-candidate"
X1_CANDIDATE = "74ae24364b84520d4e0e39240beb9867653cc7b9"
X1_OBJECTS = (X1_CANDIDATE, "6b0061489cb67d345f212f75268455c181ba271f", "1597c01b416b6aa697d73efc7d2c2b3695dc3e5c")


def require_budget(label: str) -> float:
    remaining = 300.0 if DEADLINE is None else DEADLINE - monotonic()
    if remaining <= 0:
        raise AggregateTimeout(f"AGGREGATE_TIMEOUT during {label}")
    return remaining


def base_environment() -> dict[str, str]:
    # PATH is the only ambient execution input. Interpreter identity is not claimed.
    return {"PATH": os.environ.get("PATH", ""), "PYTHONHASHSEED": "0", "PYTHONNOUSERSITE": "1",
            "LC_ALL": "C", "LANG": "C", "TZ": "UTC", "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_CONFIG_GLOBAL": os.devnull, "GIT_OPTIONAL_LOCKS": "0"}


def isolated_environment(parent: Path, context_data: dict[str, object] | None = None) -> dict[str, str]:
    env = base_environment()
    for key, name in {"HOME": "home", "TMPDIR": "tmp", "TMP": "tmp", "TEMP": "tmp",
                      "XDG_CONFIG_HOME": "config", "XDG_CACHE_HOME": "cache", "PYTHONPYCACHEPREFIX": "pycache"}.items():
        path = parent / "environment" / name
        path.mkdir(parents=True, exist_ok=True)
        env[key] = str(path)
    if context_data is not None:
        env.update({"GLYPH_CHECKER_BASE": str(context_data["base"]),
                    "GLYPH_CHECKER_EXPECTED_MERGE_BASE": str(context_data["expected_merge_base"])})
    return env


def checker_environment(entry: dict[str, object], env: dict[str, str]) -> dict[str, str]:
    result = dict(env)
    if SELF_TEST_COMMANDS.get(str(entry["id"])) == entry["command"]:
        result.pop("GLYPH_CHECKER_BASE", None)
        result.pop("GLYPH_CHECKER_EXPECTED_MERGE_BASE", None)
    return result


def group_exists(pid: int) -> bool:
    try:
        os.killpg(pid, 0)
        return True
    except ProcessLookupError:
        return False


def signal_group(pid: int, signum: int) -> None:
    try:
        os.killpg(pid, signum)
    except ProcessLookupError:
        pass


def child_exec(command: list[str], cwd: Path, env: dict[str, str]) -> None:
    """Called only after the parent owns the forked child; tests may delay exec."""
    os.chdir(cwd)
    os.execvpe(command[0], command, env)


def run_checker(command: list[str], cwd: Path, env: dict[str, str], timeout: float,
                *, input_text: str | None = None, input_file=None, output_file=None) -> tuple[int, str, str, str | None, float]:
    """Own the child before exec/setup; drain pipes and reap within bounded clocks."""
    started = monotonic()
    pid = None
    exit_code = None
    failure = None
    streams = {"stdout": bytearray(), "stderr": bytearray()}
    descriptors: set[int] = set()
    selector = selectors.DefaultSelector()
    input_bytes = (input_text or "").encode()
    input_offset = 0

    def pipe():
        pair = os.pipe()
        descriptors.update(pair)
        return pair

    def close(fd):
        if fd in descriptors:
            descriptors.remove(fd)
            os.close(fd)

    def reap() -> bool:
        nonlocal exit_code
        if exit_code is None:
            mask = signal.pthread_sigmask(signal.SIG_BLOCK, {signal.SIGALRM})
            try:
                found, status = os.waitpid(pid, os.WNOHANG)
                if found:
                    exit_code = os.waitstatus_to_exitcode(status)
            finally:
                signal.pthread_sigmask(signal.SIG_SETMASK, mask)
        return exit_code is not None

    def drain(duration: float) -> None:
        nonlocal input_offset
        for key, _ in selector.select(max(0, duration)):
            fd, label = key.fd, key.data
            if label == "stdin":
                try:
                    input_offset += os.write(fd, input_bytes[input_offset:input_offset + 65536])
                except BrokenPipeError:
                    input_offset = len(input_bytes)
                if input_offset == len(input_bytes):
                    selector.unregister(fd)
                    close(fd)
            else:
                block = os.read(fd, 65536)
                if block:
                    streams[label].extend(block)
                else:
                    selector.unregister(fd)
                    close(fd)

    def terminate() -> None:
        """The operational alarm must never interrupt its separately bounded cleanup."""
        timer = signal.setitimer(signal.ITIMER_REAL, 0)
        try:
            signal_group(pid, signal.SIGTERM)
            if exit_code is None:
                try: os.kill(pid, signal.SIGTERM)  # Also covers a child not yet in setsid().
                except ProcessLookupError: pass
            grace_end = monotonic() + TERM_GRACE_SECONDS
            while monotonic() < grace_end:
                drain(min(.01, max(0, grace_end - monotonic())))
                if reap() and not group_exists(pid):
                    break
            if group_exists(pid):
                signal_group(pid, signal.SIGKILL)
            if exit_code is None:
                try: os.kill(pid, signal.SIGKILL)
                except ProcessLookupError: pass
            # Reaping uses nonblocking waitpid, never an unbounded wait/communicate.
            reap_end = monotonic() + .1
            while (exit_code is None or selector.get_map()) and monotonic() < reap_end:
                drain(min(.005, max(0, reap_end - monotonic())))
                reap()
            if exit_code is None:
                raise ValueError("process cleanup proof unavailable after KILL")
        finally:
            if timer[0] and DEADLINE is not None and DEADLINE > monotonic():
                signal.setitimer(signal.ITIMER_REAL, DEADLINE - monotonic())
            elif timer[0] and DEADLINE is None:
                signal.setitimer(signal.ITIMER_REAL, timer[0], timer[1])

    try:
        stdout_read, stdout_write = pipe() if output_file is None else (None, output_file.fileno())
        stderr_read, stderr_write = pipe()
        if input_file is not None:
            stdin_read, stdin_write = input_file.fileno(), None
        elif input_text is not None:
            stdin_read, stdin_write = pipe()
        else:
            stdin_read, stdin_write = os.open(os.devnull, os.O_RDONLY), None
            descriptors.add(stdin_read)
        # Only native fork and PID registration are masked, never Popen, exec,
        # a Python callback, a wait, or file/pipe I/O. Any delayed child setup
        # happens after this parent has a PID it can terminate and reap.
        old_mask = signal.pthread_sigmask(signal.SIG_BLOCK, {signal.SIGALRM})
        try:
            pid = os.fork()
        finally:
            if pid != 0:
                signal.pthread_sigmask(signal.SIG_SETMASK, old_mask)
        if pid == 0:
            try:
                os.setsid()
                os.dup2(stdin_read, 0)
                os.dup2(stdout_write, 1)
                os.dup2(stderr_write, 2)
                # /dev/fd lists this process's actual descriptors on POSIX;
                # avoid scanning a million unused descriptor numbers on macOS.
                try:
                    inherited_fds = [int(name) for name in os.listdir("/dev/fd")]
                except OSError:
                    os.closerange(3, os.sysconf("SC_OPEN_MAX"))
                else:
                    for descriptor in inherited_fds:
                        if descriptor > 2:
                            try: os.close(descriptor)
                            except OSError: pass
                signal.signal(signal.SIGALRM, signal.SIG_DFL)
                signal.pthread_sigmask(signal.SIG_SETMASK, old_mask)
                child_exec(command, cwd, env)
            except BaseException as exc:
                os.write(2, ("command launch failed: " + str(exc)).encode())
            os._exit(127)
        close(stdin_read)
        close(stdout_write)
        close(stderr_write)
        for fd, label, event in ((stdout_read, "stdout", selectors.EVENT_READ), (stderr_read, "stderr", selectors.EVENT_READ),
                                 (stdin_write, "stdin", selectors.EVENT_WRITE)):
            if fd is not None:
                os.set_blocking(fd, False)
                selector.register(fd, event, label)
        end = started + timeout
        try:
            while selector.get_map() or exit_code is None:
                remaining = end - monotonic()
                if remaining <= 0:
                    failure = "CHECKER_TIMEOUT"
                    break
                drain(min(.01, remaining))
                reap()
            if failure is None and group_exists(pid):
                failure = "PROCESS_GROUP_REMAINS"
        except AggregateTimeout:
            failure = "AGGREGATE_TIMEOUT"
        if failure:
            terminate()
            if DEADLINE is not None and monotonic() >= DEADLINE:
                failure = "AGGREGATE_TIMEOUT"
        return exit_code, streams["stdout"].decode(), streams["stderr"].decode(), failure, monotonic() - started
    finally:
        if pid not in (None, 0) and (exit_code is None or group_exists(pid)):
            terminate()
        selector.close()
        for fd in list(descriptors):
            close(fd)


def git(*args: str, cwd: Path | None = None, env: dict[str, str] | None = None,
        timeout: float | None = None) -> subprocess.CompletedProcess[str]:
    remaining = require_budget("git " + " ".join(args[:2]))
    command = ["git", "-c", "protocol.allow=never", *args]
    code, stdout, stderr, failure, _ = run_checker(command, cwd or ROOT,
        env if env is not None else EXECUTION_ENV or base_environment(), min(remaining, timeout) if timeout is not None else remaining)
    if failure:
        if failure in {"CHECKER_TIMEOUT", "AGGREGATE_TIMEOUT"}:
            raise AggregateTimeout("AGGREGATE_TIMEOUT during git " + " ".join(args[:2]))
        raise ValueError("Git process-group cleanup failed: " + failure)
    return subprocess.CompletedProcess(command, code, stdout, stderr)


def git_value(*args: str, cwd: Path | None = None) -> str:
    result = git(*args, cwd=cwd)
    if result.returncode:
        raise ValueError(f"git {' '.join(args)} failed: {result.stderr.strip()}")
    return result.stdout.strip()


def reject_partial_repository() -> None:
    values = git("config", "--local", "--get-regexp", r"^(extensions\.partialclone|remote\..*\.promisor)$")
    if values.returncode not in (0, 1):
        raise ValueError("could not inspect local object topology")
    if values.stdout.strip():
        raise ValueError("partial/promisor repository cannot prove offline local object completeness")


def require_clean_source() -> None:
    status = git_value("status", "--porcelain=v1", "--untracked-files=all")
    if status:
        raise ValueError("source worktree must be clean; staged, unstaged, and untracked paths are refused")
    # Index stat shortcuts (assume-unchanged/skip-worktree/core.filemode) may
    # suppress git status. Compare the physical committed content directly.
    tree = git("ls-tree", "-r", "-z", "HEAD")
    if tree.returncode:
        raise ValueError("could not enumerate committed source tree")
    for record in tree.stdout.split("\0"):
        if not record: continue
        header, relative = record.split("\t", 1)
        mode, kind, identity = header.split()
        path = ROOT / relative
        try:
            physical = path.lstat()
            if mode == "120000" and stat.S_ISLNK(physical.st_mode):
                data = os.fsencode(os.readlink(path))
            elif mode in {"100644", "100755"} and stat.S_ISREG(physical.st_mode):
                actual_mode = "100755" if physical.st_mode & stat.S_IXUSR else "100644"
                if actual_mode != mode: raise ValueError("tracked executable mode differs")
                data = path.read_bytes()
            else:
                raise ValueError("tracked path type differs or is unsupported")
            digest = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
            if kind != "blob" or digest != identity:
                raise ValueError("tracked bytes or symlink target differ")
        except (OSError, ValueError) as exc:
            raise ValueError(f"source worktree must be clean: {relative}: {exc}") from exc
        require_budget("direct committed-source correspondence")


def required_catalog(selected: list[dict[str, object]]) -> tuple[dict[str, str], set[str]]:
    """Only current source-consumed identities authorized by the closed catalog."""
    refs: dict[str, str] = {}
    roots: set[str] = set()
    def has(checker_id: str, filename: str) -> bool:
        return any(entry["id"] == checker_id and entry["command"] == ["python3", "tools/" + filename] for entry in selected)
    if has("generated_baseline_artifact", "check_glyph_generated_source_owned_baseline_artifact.py"):
        identity = git_value("rev-parse", "--verify", "refs/heads/configurator^{commit}")
        refs["refs/heads/configurator"] = identity
        roots.add(identity)
    for checker_id, filename, identities in (
        ("build_input_resolution_observations", "check_glyph_build_input_resolution_observations.py", ("8c04262c66613d46b933b1b739c01c575cb0c580", "ffc007552abc848051841362b0b0ac4c1a7d087b")),
        ("nuker_source_lineage", "check_glyph_nuker_source_lineage.py", ("a747dd54b02b207483142331d8b5be1113fc951e", "d5050847d3f850951b3f47865dc8a91aedea0834")),
    ):
        if has(checker_id, filename): roots.update(identities)
    if not has("agent_framework", "check_glyph_agent_framework_docs.py"):
        return refs, roots
    path = "docs/project/ACTIVE_AGENT_QUEUE.md"
    found = git("ls-tree", "-z", "HEAD", "--", path)
    records = [record for record in found.stdout.split("\0") if record]
    if found.returncode or len(records) != 1 or records[0].split("\t", 1)[1] != path or not records[0].startswith("100644 blob "):
        raise ValueError("committed canonical queue must be one regular 100644 blob")
    raw = git_value("show", "HEAD:" + path)
    start, end = "<!-- queue-state:start -->", "<!-- queue-state:end -->"
    if raw.count(start) != 1 or raw.count(end) != 1:
        raise ValueError("committed queue requires one queue-state marker pair")
    block = raw.split(start, 1)[1].split(end, 1)[0].strip()
    if not block.startswith("```json") or not block.endswith("```"):
        raise ValueError("committed queue-state must be fenced JSON")
    value = json.loads(block[len("```json"):-3], object_pairs_hook=pairs)
    def mapping(value, label):
        if not isinstance(value, dict): raise ValueError(label + " must be an object")
        return value
    def commit(value, label):
        if not isinstance(value, str) or not re.fullmatch(r"[a-f0-9]{40}", value):
            raise ValueError(label + " must be a full lowercase commit identity")
        roots.add(value)
    value = mapping(value, "queue")
    packet = mapping(value.get("planner_packet"), "planner_packet")
    if not isinstance(packet.get("state"), str): raise ValueError("planner packet state must be a string")
    if packet["state"] != "ABSENT":
        for field in ("base_configurator_sha", "planning_commit", "curation_commit"):
            commit(packet.get(field), "planner_packet." + field)
    policy = mapping(value.get("completion_correspondence"), "completion_correspondence")
    commit(policy.get("migration_base_configurator_sha"), "completion migration base")
    legacy = policy.get("legacy_done_ids")
    if not isinstance(legacy, list) or not all(isinstance(item, str) for item in legacy):
        raise ValueError("legacy_done_ids must be a string list")
    items = value.get("items")
    if not isinstance(items, list): raise ValueError("queue items must be a list")
    for item in items:
        item = mapping(item, "queue item")
        if not isinstance(item.get("id"), str) or not isinstance(item.get("status"), str):
            raise ValueError("queue item id/status must be strings")
        if item["status"] == "DONE" and item["id"] not in legacy:
            evidence = mapping(item.get("done_evidence"), "done_evidence")
            for field in ("implementation_base_sha", "reviewed_implementation_sha", "prior_canonical_integration_sha"):
                commit(evidence.get(field), "done_evidence." + field)
        if item["status"] in {"HARDWARE_VALIDATED", "HARDWARE_FAILED"} or (item["status"] == "LOCAL_ACCEPTANCE_PENDING" and item.get("hardware_result") is not None):
            reference = item.get("hardware_evidence_record")
            if not isinstance(reference, str): raise ValueError("hardware evidence reference must be a string")
            match = re.fullmatch(r"(?:repo-json:(docs/[^:]+\.json)|git-json:([a-f0-9]{40}):(docs/[^:]+\.json))", reference)
            if not match: raise ValueError("hardware evidence reference must be an exact repo-json/git-json identity")
            relative = match[1] or match[3]
            if any(part in {"", ".", ".."} for part in relative.split("/")) or "\\" in relative:
                raise ValueError("hardware evidence path must be normalized")
            if match[2]: commit(match[2], "hardware evidence commit")
    return refs, roots


def immutable_source_context(selected: list[dict[str, object]]) -> dict[str, object]:
    require_clean_source()
    head = git_value("rev-parse", "--verify", "HEAD^{commit}")
    branch_result = git("symbolic-ref", "--quiet", "HEAD")
    if branch_result.returncode not in (0, 1):
        raise ValueError("source symbolic HEAD could not be resolved")
    branch_ref = branch_result.stdout.strip() if branch_result.returncode == 0 else None
    if branch_ref is not None and not branch_ref.startswith("refs/heads/"):
        raise ValueError("source HEAD must name a full local branch ref")
    branch = branch_ref.removeprefix("refs/heads/") if branch_ref else None
    remote = git("rev-parse", "--verify", "refs/remotes/origin/configurator^{commit}")
    comparison_ref = remote.stdout.strip() if remote.returncode == 0 else None
    override = os.environ.get("GLYPH_CHECKER_BASE")
    base = git_value("rev-parse", "--verify", f"{override}^{{commit}}") if override else comparison_ref
    if not base:
        raise ValueError("origin/configurator must resolve to an immutable commit without GLYPH_CHECKER_BASE")
    merge_base = git_value("merge-base", head, base)
    expected_input = os.environ.get("GLYPH_CHECKER_EXPECTED_MERGE_BASE")
    expected = git_value("rev-parse", "--verify", f"{expected_input}^{{commit}}") if expected_input else merge_base
    if expected != merge_base:
        raise ValueError("unexpected feature merge base: supplied GLYPH_CHECKER_EXPECTED_MERGE_BASE differs")
    if git("merge-base", "--is-ancestor", base, head).returncode:
        raise ValueError("comparison base is not an ancestor of HEAD")
    required_refs = {}
    roots = {head, base, merge_base, expected}
    if comparison_ref:
        roots.add(comparison_ref)
    catalog_refs, catalog_roots = required_catalog(selected)
    required_refs.update(catalog_refs)
    roots.update(catalog_roots)
    if any(entry["id"] == "current_x1_regression_subset" and entry["command"] == X1_COMMAND for entry in selected):
        if git_value("rev-parse", "--verify", f"{X1_REF}^{{commit}}") != X1_CANDIDATE:
            raise ValueError("required historical X1 candidate ref does not match its immutable identity")
        required_refs[X1_REF] = X1_CANDIDATE
        roots.update(X1_OBJECTS)
    for identity in sorted(roots):
        if git_value("rev-parse", "--verify", f"{identity}^{{commit}}") != identity:
            raise ValueError("required local commit identity unavailable")
    objects = git_value("rev-list", "--objects", "--missing=print", *sorted(roots))
    if any(line.startswith("?") for line in objects.splitlines()):
        raise ValueError("required immutable Git object closure is unavailable locally")
    return {"head": head, "branch": branch, "branch_ref": branch_ref, "detached": branch is None, "base": base,
            "merge_base": merge_base, "expected_merge_base": expected,
            "comparison_ref": comparison_ref, "required_refs": required_refs, "object_roots": sorted(roots)}


def canonical_fingerprint(root: Path | None = None) -> str:
    """Read only; include tracked, untracked, and ignored file bytes plus repository metadata."""
    root = root or ROOT
    digest = hashlib.sha256()
    def add(value: bytes) -> None:
        digest.update(len(value).to_bytes(8, "big"))
        digest.update(value)
    git_dir = Path(git_value("rev-parse", "--absolute-git-dir", cwd=root))
    common = Path(git_value("rev-parse", "--git-common-dir", cwd=root))
    if not common.is_absolute():
        common = root / common
    metadata = {git_dir / "index", git_dir / "HEAD", git_dir / "config.worktree", common / "config", common / "packed-refs"}
    for path in sorted(metadata):
        require_budget("repository metadata fingerprint")
        add(str(path).encode() + b"\0")
        add(path.read_bytes() if path.exists() else b"<absent>")
    for args in (("rev-parse", "HEAD"), ("symbolic-ref", "--quiet", "HEAD"),
                 ("ls-files", "--stage", "-z"), ("for-each-ref", "--format=%(refname) %(objectname)"),
                 ("config", "--local", "--null", "--list"),
                 ("status", "--porcelain=v2", "--ignored=matching", "--untracked-files=all", "-z")):
        result = git(*args, cwd=root)
        if result.returncode and not (args[0] == "symbolic-ref" and result.returncode == 1):
            raise ValueError(f"canonical fingerprint probe failed: git {' '.join(args)}")
        add(repr(args).encode() + str(result.returncode).encode() + result.stdout.encode() + result.stderr.encode())
    for label, args in (("TRACKED", ("ls-files", "-z")),
                        ("UNTRACKED", ("ls-files", "--others", "--exclude-standard", "-z")),
                        ("IGNORED", ("ls-files", "--others", "--ignored", "--exclude-standard", "-z"))):
        path_result = git(*args, cwd=root)
        if path_result.returncode:
            raise ValueError("repository path enumeration failed")
        paths = path_result.stdout.split("\0")
        for relative in sorted(path for path in paths if path):
            require_budget("repository file fingerprint")
            path = root / relative
            add(label.encode() + b"\0" + relative.encode() + b"\0")
            try:
                stat = path.lstat()
                add(str(stat.st_mode).encode() + b"\0")
                if path.is_symlink():
                    add(os.readlink(path).encode())
                elif path.is_file():
                    with path.open("rb") as stream:
                        while block := stream.read(1024 * 1024):
                            require_budget("repository file bytes fingerprint")
                            add(block)
                else:
                    raise ValueError(f"unsupported repository path type: {relative}")
            except FileNotFoundError:
                add(b"<absent>")
    require_budget("completed repository fingerprint")
    return digest.hexdigest()


def clone_snapshot(context_data: dict[str, object], parent: Path) -> Path:
    clone = parent / "snapshot"
    completed = git("-c", "protocol.file.allow=always", "clone", "--no-local", "--no-checkout", str(ROOT), str(clone))
    if completed.returncode:
        raise ValueError(f"isolated clone failed: {completed.stderr.strip()}")
    if (clone / ".git/objects/info/alternates").exists():
        raise ValueError("isolated clone must not use object alternates")
    git_value("remote", "remove", "origin", cwd=clone)
    # Clone initially discovers refs locally; retain only the closed authorized set.
    for ref in git_value("for-each-ref", "--format=%(refname)", cwd=clone).splitlines():
        git_value("update-ref", "-d", ref, cwd=clone)
    roots = context_data["object_roots"]
    missing = any(git("cat-file", "-e", f"{identity}^{{commit}}", cwd=clone).returncode for identity in roots)
    if missing:
        pack = parent / "required-objects.pack"
        with pack.open("wb") as output:
            code, _, error, failure, _ = run_checker(["git", "-c", "protocol.allow=never", "pack-objects", "--revs", "--stdout"],
                ROOT, EXECUTION_ENV or base_environment(), require_budget("local immutable object packing"),
                input_text="\n".join(roots) + "\n", output_file=output)
        if failure:
            raise AggregateTimeout("AGGREGATE_TIMEOUT during local immutable object packing")
        if code:
            raise ValueError("local immutable object packing failed: " + error.strip())
        with pack.open("rb") as source:
            code, _, error, failure, _ = run_checker(["git", "-c", "protocol.allow=never", "index-pack", "--stdin"],
                clone, EXECUTION_ENV or base_environment(), require_budget("local immutable object import"), input_file=source)
        if failure:
            raise AggregateTimeout("AGGREGATE_TIMEOUT during local immutable object import")
        if code:
            raise ValueError("local immutable object import failed: " + error.strip())
    for identity in roots:
        if git_value("rev-parse", "--verify", f"{identity}^{{commit}}", cwd=clone) != identity:
            raise ValueError("isolated required object identity differs")
    objects = git_value("rev-list", "--objects", "--missing=print", *roots, cwd=clone)
    if any(line.startswith("?") for line in objects.splitlines()):
        raise ValueError("isolated required object closure incomplete")
    if context_data["comparison_ref"]:
        git_value("update-ref", "refs/remotes/origin/configurator", str(context_data["comparison_ref"]), cwd=clone)
    for ref, identity in context_data["required_refs"].items():
        git_value("update-ref", ref, identity, cwd=clone)
    branch = context_data["branch"]
    if branch is None:
        git_value("checkout", "--detach", str(context_data["head"]), cwd=clone)
    else:
        git_value("checkout", "-B", str(branch), str(context_data["head"]), cwd=clone)
    expected_refs = dict(context_data["required_refs"])
    if branch:
        expected_refs["refs/heads/" + str(branch)] = context_data["head"]
    if context_data["comparison_ref"]:
        expected_refs["refs/remotes/origin/configurator"] = context_data["comparison_ref"]
    refs = dict(line.split(" ", 1) for line in git_value("for-each-ref", "--format=%(refname) %(objectname)", cwd=clone).splitlines())
    actual_branch = git("symbolic-ref", "--quiet", "HEAD", cwd=clone)
    if actual_branch.returncode not in (0, 1) or (actual_branch.stdout.strip() or None) != context_data["branch_ref"]:
        raise ValueError("isolated full symbolic HEAD correspondence failed")
    if refs != expected_refs or git_value("rev-parse", "HEAD", cwd=clone) != context_data["head"]:
        raise ValueError("isolated HEAD/ref correspondence failed")
    return clone


def main() -> int:
    global DEADLINE, EXECUTION_ENV
    parser = argparse.ArgumentParser()
    parser.add_argument("--category", action="append")
    parser.add_argument("--fail-fast", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--check-manifest", action="store_true")
    args = parser.parse_args()
    previous_deadline, previous_env = DEADLINE, EXECUTION_ENV
    started = monotonic()
    DEADLINE = started + AGGREGATE_TIMEOUT_SECONDS
    before = None
    output = {"status": "FAIL", "failure_kind": None, "phase": "preflight", "message": None,
              "aggregate_timeout_seconds": AGGREGATE_TIMEOUT_SECONDS,
              "canonical_proof": "UNAVAILABLE", "results": [], "excluded": []}
    parent = None
    def deadline_alarm(signum, frame):
        raise AggregateTimeout("AGGREGATE_TIMEOUT during " + str(output["phase"]))
    previous_handler = signal.signal(signal.SIGALRM, deadline_alarm)
    previous_timer = signal.setitimer(signal.ITIMER_REAL, AGGREGATE_TIMEOUT_SECONDS)
    try:
        parent = Path(tempfile.mkdtemp(prefix="glyph-runtime-config-validation-"))
        EXECUTION_ENV = isolated_environment(parent)
        try:
            reject_partial_repository()
            before = canonical_fingerprint()
            freshness = census_freshness()
            output["census_freshness"] = freshness
            if freshness["status"] != "PASS":
                raise ValueError("checker census is stale; run tools/generate_glyph_checker_census.py")
            entries, exclusions, categories = load()
            output["excluded"] = [{"id": entry["id"], "applicability": entry["applicability"], "reason": entry["reason"]} for entry in entries if entry["applicability"] != "current"] + [{"id": exclusion["id"], "applicability": "excluded", "reason": exclusion["reason"]} for exclusion in exclusions]
            output["manifest_entries"] = len(entries)
            output["strong_signal_exclusions"] = len(exclusions)
            if args.category and any(category not in categories for category in args.category):
                raise ValueError("unknown category: " + ", ".join(sorted(set(args.category) - categories)))
            selected = [entry for entry in entries if entry["applicability"] == "current" and (not args.category or entry["category"] in args.category)]
            if args.category:
                empty = sorted(set(args.category) - {str(entry["category"]) for entry in selected})
                if empty:
                    raise ValueError("requested category selects zero current checks: " + ", ".join(empty))
            require_clean_source()
            if not args.check_manifest:
                output["phase"] = "source_context"
                context_data = immutable_source_context(selected)
                output["context"] = context_data
                output["phase"] = "snapshot_setup"
                clone = clone_snapshot(context_data, parent)
                env = isolated_environment(parent, context_data)
                isolated_before = canonical_fingerprint(clone)
                for entry in selected:
                    output["phase"] = "checker:" + str(entry["id"])
                    remaining = require_budget(output["phase"])
                    timeout = min(CHECKER_TIMEOUT_SECONDS, remaining)
                    code, stdout, stderr, failure, duration = run_checker(entry["command"], clone, checker_environment(entry, env), timeout)
                    if failure == "CHECKER_TIMEOUT" and remaining <= CHECKER_TIMEOUT_SECONDS:
                        failure = "AGGREGATE_TIMEOUT"
                    result = {"id": entry["id"], "command": entry["command"], "category": entry["category"],
                              "applicability": entry["applicability"], "exit_code": code, "status": "FAIL",
                              "failure_kind": failure, "timeout_seconds": timeout,
                              "stdout_summary": stdout.strip().splitlines()[-1:], "stderr_summary": stderr.strip().splitlines()[-1:],
                              "duration_seconds": round(duration, 3), "isolated_proof": "UNAVAILABLE"}
                    output["results"].append(result)
                    try:
                        if canonical_fingerprint(clone) != isolated_before:
                            result["isolated_proof"] = "MISMATCH"
                            failure = failure or "ISOLATED_REPOSITORY_MUTATION"
                        else:
                            result["isolated_proof"] = "MATCH"
                    except (AggregateTimeout, OSError, ValueError, subprocess.SubprocessError) as exc:
                        failure = failure or ("AGGREGATE_TIMEOUT" if isinstance(exc, AggregateTimeout) else "ISOLATED_PROOF_FAILURE")
                        result["proof_error"] = str(exc)
                    result["failure_kind"] = failure
                    result["status"] = "PASS" if code == 0 and not failure else "FAIL"
                    if failure:
                        output["failure_kind"] = failure
                        break
                    if code and args.fail_fast:
                        break
            output["status"] = "PASS" if not output["failure_kind"] and all(result["status"] == "PASS" for result in output["results"]) else "FAIL"
        except (AggregateTimeout, OSError, ValueError, TypeError, subprocess.SubprocessError) as exc:
            output["failure_kind"] = "AGGREGATE_TIMEOUT" if isinstance(exc, AggregateTimeout) else "SETUP_FAILURE"
            output["message"] = str(exc)
            output["status"] = "FAIL"
        finally:
            if before is not None:
                try:
                    if canonical_fingerprint() == before:
                        output["canonical_proof"] = "MATCH"
                    else:
                        output["canonical_proof"] = "MISMATCH"
                        output["failure_kind"] = "CANONICAL_REPOSITORY_MUTATION"
                        output["status"] = "FAIL"
                except (AggregateTimeout, OSError, ValueError, subprocess.SubprocessError) as exc:
                    output["canonical_proof"] = "UNAVAILABLE"
                    output["final_proof_error"] = str(exc)
                    output["failure_kind"] = output["failure_kind"] or ("AGGREGATE_TIMEOUT" if isinstance(exc, AggregateTimeout) else "FINAL_PROOF_FAILURE")
                    output["status"] = "FAIL"
            else:
                output["status"] = "FAIL"
    except (AggregateTimeout, OSError, ValueError, subprocess.SubprocessError) as exc:
        output["status"] = "FAIL"
        output["failure_kind"] = "AGGREGATE_TIMEOUT" if isinstance(exc, AggregateTimeout) else "SETUP_FAILURE"
        output["message"] = str(exc)
    finally:
        # No atexit/context-manager recursive deletion may overrun the deadline.
        # A timed-out run can retain only its disposable scratch tree, reported explicitly.
        try:
            if parent is not None:
                output["phase_before_cleanup"] = output["phase"]
                code, _, error, failure, _ = run_checker(["rm", "-rf", str(parent)], parent.parent,
                    EXECUTION_ENV or base_environment(), require_budget("disposable cleanup"))
                if code or failure:
                    raise AggregateTimeout("disposable cleanup did not finish within the operational deadline")
        except (AggregateTimeout, OSError, ValueError, subprocess.SubprocessError) as exc:
            output["status"] = "FAIL"
            output["failure_kind"] = output["failure_kind"] or "AGGREGATE_TIMEOUT"
            output["cleanup_error"] = str(exc)
            output["retained_temporary_directory"] = str(parent) if parent is not None else None
        finally:
            signal.setitimer(signal.ITIMER_REAL, 0)
            signal.signal(signal.SIGALRM, previous_handler)
            if previous_timer[0] > 0:
                signal.setitimer(signal.ITIMER_REAL, max(.001, previous_timer[0] - (monotonic() - started)), previous_timer[1])
            DEADLINE, EXECUTION_ENV = previous_deadline, previous_env
    if args.json:
        print(json.dumps(output, sort_keys=True))
    elif args.check_manifest and output["status"] == "PASS":
        print(f"glyph_runtime_config_validation_manifest: PASS; entries={output['manifest_entries']}; strong_signal_exclusions={output['strong_signal_exclusions']}")
    else:
        print(f"glyph_runtime_config_validation: {output['status']}" + (": " + str(output["message"]) if output["message"] else ""))
        for result in output["results"]:
            print(f"- {result['id']}: {result['status']}")
        if output["failure_kind"]:
            print(f"failure_kind={output['failure_kind']}; phase={output['phase']}; canonical_proof={output['canonical_proof']}")
        print("excluded=" + ",".join(item["id"] for item in output["excluded"]))
    return 0 if output["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
