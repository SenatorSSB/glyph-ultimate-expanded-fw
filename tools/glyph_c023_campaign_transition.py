"""Finite GP-VAL-042 authentication for the exact C023 candidate."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import glyph_c022_campaign_transition as previous
from glyph_hardware_correspondence import CorrespondenceError, classify_path
from glyph_tracked_worktree_integrity import IGNORED_ALLOWED_ROOTS

original = previous.original
require = previous.require
_git = previous._git
_tree = previous._tree
raw_bytes = previous.raw_bytes
current_bytes = previous.current_bytes
critical_tree = previous.critical_tree
ancestor = previous.ancestor
item = previous.item
unique = previous.unique
sha = previous.sha
_stage_and_live = previous._stage_and_live
QUEUE = previous.QUEUE

C = "03bbf5da14a7d450f2986b12ad69ec6b3f704bad"
B = "b224227a76cb8edb73e5f4b2ad5de874d1e61ad1"
TREE = "da886ff6d9b2d545bd93ce50745ae353129d8e7c"
RAW = "0bd5c9cfc481bb4e7fc3b595f59efa7c415695a7b01df3b55a84ebfd66a6a4b4"
MAPPING = "docs/runtime_config/fixtures/gp_val042_c023_transition.json"
TRANSITIONS = "docs/runtime_config/fixtures/gp_val042_accepted_transitions.json"
HANDOFF_START = "<!-- gp-config023-handoff-val042-activation:start -->"
HANDOFF_END = "<!-- gp-config023-handoff-val042-activation:end -->"
CRITICAL = frozenset((
    "HAL/pico/src/comms/backend_init.cpp",
    "config/glyph/common/src/config.cpp",
    "include/core/config_usb_default_validation.hpp",
    "include/core/config_validation.hpp",
    "src/core/config_usb_default_validation.cpp",
    "src/core/config_validation.cpp",
))
HOSTS = frozenset((
    "docs/runtime_config/fixtures/gp_config023_usb_index_validation.json",
    "docs/runtime_config/gp_config023_usb_index_validation.md",
    "tools/check_glyph_gp_config023_usb_index_validation.py",
    "tools/fixtures/gp_config023_usb_host/host_stubs.hpp",
    "tools/fixtures/gp_config023_usb_host/usb_index_harness.cpp",
))
GOVERNANCE = frozenset((
    "docs/AGENT_CONTEXT.md", "docs/CURRENT_STATE.md", "docs/ROADMAP.md",
    "docs/agent_framework/HARDWARE_CORRESPONDENCE.md",
    "docs/project/ACTIVE_AGENT_QUEUE.md",
    "docs/runtime_config/fixtures/glyph_checker_census.json",
    "docs/runtime_config/fixtures/runtime_config_validation_manifest.json",
    "docs/runtime_config/fixtures/runtime_config_validation_health.json",
    "docs/runtime_config/runtime_config_validation_health.md",
    "tools/check_glyph_runtime_config_validation_health.py",
    "docs/runtime_config/fixtures/gp_val042_c023_transition.json",
    "docs/runtime_config/fixtures/gp_val042_accepted_transitions.json",
    "tools/glyph_campaign_transition.py",
    "tools/glyph_hardware_correspondence.py",
    "tools/check_glyph_config_010_integration_semantic_correspondence.py",
    "tools/check_glyph_runtime_config_validation_aggregate.py",
    "tools/run_glyph_runtime_config_validation.py",
    "tools/glyph_c022_campaign_transition.py",
    "tools/glyph_c023_campaign_transition.py",
    "tools/test_glyph_c023_campaign_transition.py",
    "tools/check_glyph_c023_proof_replay.py",
))


def present(root: Path) -> bool:
    root = Path(root).resolve()
    tree = _tree(root, _git(root, "rev-parse", "HEAD").decode().strip())
    return MAPPING in tree or (root / MAPPING).exists() or (root / MAPPING).is_symlink()


def has_source_overlay(root: Path) -> bool:
    """Select C023 only after its source appears in the current critical tree."""
    root = Path(root).resolve()
    head = _git(root, "rev-parse", "HEAD").decode().strip()
    baseline = _tree(root, B)
    current = critical_tree(root, head)
    return any(current.get(path) != baseline.get(path) for path in CRITICAL)


def _candidate_entries(root: Path) -> list[dict]:
    raw = _git(root, "diff-tree", "-r", "--no-renames", "--raw", "-z", B, C)
    require(sha(raw) == RAW, "C023 raw NUL inventory digest changed")
    fields = raw.split(b"\0")
    entries = []
    index = 0
    while index < len(fields) - 1:
        header = fields[index].decode("ascii")
        path = fields[index + 1].decode("utf-8")
        index += 2
        data = raw_bytes(root, C, path)
        entries.append({
            "path": path,
            "old_mode": header[1:7],
            "new_mode": header[8:14],
            "old_blob": header[15:55],
            "new_blob": header[56:96],
            "status": header[97:],
            "new_sha256": sha(data),
            "bytes": len(data),
        })
    return entries


def _handoff(root: Path, ref: str | None) -> dict:
    text = (current_bytes(root, QUEUE)
            if ref is None else raw_bytes(root, ref, QUEUE)).decode("utf-8")
    require(text.count(HANDOFF_START) == text.count(HANDOFF_END) == 1,
            "C023 handoff marker missing/duplicated")
    block = text.split(HANDOFF_START, 1)[1].split(HANDOFF_END, 1)[0].strip()
    require(block.startswith("```json") and block.endswith("```"),
            "C023 handoff JSON fence changed")
    value = json.loads(block[7:-3], object_pairs_hook=unique)
    mapping_bytes = (current_bytes(root, MAPPING)
                     if ref is None else raw_bytes(root, ref, MAPPING))
    require(value == {
        "schema_name": "glyph_gp_config023_candidate_handoff_val042_activation",
        "schema_version": 1,
        "work_order": "GP-VAL-042",
        "candidate": C,
        "canonical_base": B,
        "candidate_tree": TREE,
        "candidate_direct_parent": B,
        "raw_inventory_sha256": RAW,
        "raw_inventory_count": 11,
        "mapping": MAPPING,
        "mapping_sha256": sha(mapping_bytes),
        "source_free_canonical": True,
        "gate_waivers": False,
        "independent_review_sha256": json.loads(mapping_bytes, object_pairs_hook=unique)["review_sha256"],
        "conformance": {"production_paths": 6, "proof_paths": 5,
                        "all_modes": "100644", "source_scope": "EXACT"},
        "source_proof": {"checker": "tools/check_glyph_gp_config023_usb_index_validation.py",
                          "status": "PASS", "abis": ["default", "short-enum"],
                          "sanitizers": ["ASan", "UBSan"], "firmware_build": "NOT_RUN",
                          "hardware": "NOT_CLAIMED"},
        "candidate_state": "PRESERVED_UNBUILT_UNMERGED",
    }, "C023 source-free handoff identity/content mismatch")
    return value


@original._proof_invocation
def source_contract(root: Path):
    root = Path(root).resolve()
    require(_git(root, "rev-list", "--parents", "-n", "1", C).decode().split() == [C, B]
            and _git(root, "rev-parse", C + "^{tree}").decode().strip() == TREE,
            "C023 candidate parent/tree changed")
    base_tree, candidate_tree = _tree(root, B), _tree(root, C)
    delta = {p for p in base_tree.keys() | candidate_tree.keys()
             if base_tree.get(p) != candidate_tree.get(p)}
    require(delta == CRITICAL | HOSTS and len(delta) == 11,
            "C023 exact six-source/five-proof path inventory changed")
    entries = _candidate_entries(root)
    for row in entries:
        path = row["path"]
        old, new = base_tree.get(path), candidate_tree.get(path)
        require(path in delta and new is not None and new[:2] == ("100644", "blob")
                and row["new_mode"] == new[0] and row["new_blob"] == new[2]
                and row["new_sha256"] == sha(raw_bytes(root, C, path))
                and row["bytes"] == len(raw_bytes(root, C, path))
                and (row["old_mode"], row["old_blob"], row["status"]) ==
                    ((old[0], old[2], "M") if old else ("000000", "0" * 40, "A")),
                "C023 raw path/mode/blob/size mismatch: " + path)
        require(classify_path(path) == ("CRITICAL" if path in CRITICAL else "NON_BEHAVIORAL"),
                "C023 source/proof role mismatch: " + path)
    mapping = json.loads(current_bytes(root, MAPPING), object_pairs_hook=unique)
    require(set(mapping) == {"schema_name", "schema_version", "work_order", "candidate",
            "base", "tree", "raw_inventory_sha256", "entries", "review", "review_sha256",
            "conformance"}
            and mapping["schema_name"] == "glyph_gp_val042_c023_transition"
            and type(mapping["schema_version"]) is int and mapping["schema_version"] == 1
            and mapping["work_order"] == "GP-VAL-042"
            and (mapping["candidate"], mapping["base"], mapping["tree"],
                 mapping["raw_inventory_sha256"]) == (C, B, TREE, RAW)
            and mapping["entries"] == entries,
            "C023 mapping identity/inventory mismatch")
    review = mapping["review"]
    require(type(review) is dict and review.get("status") == "APPROVED_EXACT_C023_FOR_GP_VAL_042_ONLY"
            and review.get("reviewed_candidate") == C and review.get("reviewed_base") == B
            and review.get("reviewed_tree") == TREE and review.get("findings") == []
            and sha((json.dumps(review, indent=2, sort_keys=True) + "\n").encode()) == mapping["review_sha256"],
            "C023 independent review record mismatch")
    conformance = mapping["conformance"]
    require(conformance["production_paths"] == sorted(CRITICAL)
            and conformance["proof_paths"] == sorted(HOSTS)
            and conformance["all_changed_modes"] == "100644"
            and conformance["schema_default_decoder_unchanged"] is True
            and conformance["firmware_build"] == "NOT_RUN_BY_ORDER",
            "C023 source/build-role conformance mismatch")
    prior_catalog = previous._catalog(raw_bytes(root, B, previous.TRANSITIONS))
    catalog = json.loads(current_bytes(root, TRANSITIONS), object_pairs_hook=unique)
    require(set(catalog) == {"schema_version", "accepted_transitions"}
            and type(catalog["schema_version"]) is int and catalog["schema_version"] == 1
            and catalog["accepted_transitions"] == prior_catalog,
            "C023 catalog must preserve the exact accepted C022 transition without inventing C023 PASS")
    handoff = _handoff(root, None)
    prior, _ = previous.predecessor_contract(root)
    previous.source_contract(root)
    before, after = critical_tree(root, B), critical_tree(root, C)
    require({p for p in before.keys() | after.keys() if before.get(p) != after.get(p)} == CRITICAL,
            "C023 critical source union changed outside six authorized paths")
    for path in previous.PROTECTED_FIVE:
        require(_tree(root, B).get(path) == _tree(root, C).get(path),
                "C023 protected checker changed: " + path)
    return before, after, prior, mapping


@original._proof_invocation
def authenticate(root: Path):
    root = Path(root).resolve()
    before, after, prior, mapping = source_contract(root)
    head = _git(root, "rev-parse", "HEAD").decode().strip()
    require(ancestor(root, B, head), "C023 governance snapshot lost canonical B ancestry")
    current = critical_tree(root, head)
    require(current in (before, after), "C023 current source outside exact B/C critical trees")
    c_is_ancestor = ancestor(root, C, head)
    c023_order = item(root, head, "GP-CONFIG-023")
    val042_order = item(root, head, "GP-VAL-042")
    handoff = _handoff(root, head)
    require(c023_order["status"] == "PREAUTHORIZED"
            and val042_order["status"] == "PREAUTHORIZED"
            and c023_order["candidate_git_sha"] == C
            and c023_order["candidate_base_configurator_sha"] == B
            and c023_order["firmware_artifact_build_path"] is None
            and c023_order["hardware_result"] is None
            and val042_order["candidate_git_sha"] == C
            and val042_order["candidate_base_configurator_sha"] == B
            and val042_order["activation_state"] == "ACTIVATABLE"
            and handoff["candidate_state"] == "PRESERVED_UNBUILT_UNMERGED",
            "C023/042 queue state or hardware non-claim changed")
    if current == after:
        require(c_is_ancestor, "C023 source integrated without exact candidate ancestry")
        phase = "CANDIDATE_VALIDATION_ONLY"
        source_candidate = C
    else:
        require(not c_is_ancestor, "C023 source-free governance snapshot contains candidate ancestry")
        phase = "SOURCE_FREE_PROCESSOR"
        source_candidate = C
    delta = set(filter(None, _git(root, "diff", "--no-renames", "--name-only", "-z", B, head).decode().split("\0")))
    require(delta <= GOVERNANCE | CRITICAL, "C023 unknown governance/source delta")
    tree = _tree(root, head)
    for path in delta:
        require(tree.get(path, ())[:2] == ("100644", "blob"), "C023 nonregular changed path: " + path)
        require(classify_path(path) != "CRITICAL" or path in CRITICAL,
                "C023 governance exemption attempted critical path: " + path)
    expected = current
    index = {}
    for record in filter(None, _git(root, "ls-files", "--stage", "-z").decode().split("\0")):
        metadata, path = record.split("\t")
        mode, blob, stage = metadata.split()
        if path in expected:
            require(stage == "0", "C023 unmerged critical input: " + path)
            index[path] = (mode, "blob", blob)
    require(index == expected, "C023 critical index differs from HEAD")
    tags = {row[2:]: row[0] for row in
            filter(None, _git(root, "ls-files", "-v", "-z").decode().split("\0"))}
    for path, entry in expected.items():
        file = root / path
        require(path in tags and tags[path].isupper() and tags[path] != "S"
                and file.is_file() and not file.is_symlink()
                and all(not parent.is_symlink() for parent in file.parents if parent != root.parent),
                "C023 critical input missing, flagged, or symlinked: " + path)
        mode = "100755" if file.stat().st_mode & 0o111 else "100644"
        data = file.read_bytes()
        blob = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
        require((mode, "blob", blob) == entry,
                "C023 live critical bytes/mode differ from HEAD: " + path)
    ignored = set(filter(None, _git(root, "ls-files", "--others", "--ignored", "--exclude-standard", "-z").decode().split("\0")))
    dirty = set()
    for args in (("diff", "--name-only", "-z"), ("diff", "--cached", "--name-only", "-z"),
                 ("ls-files", "--others", "--exclude-standard", "-z"),
                 ("ls-files", "--others", "--ignored", "--exclude-standard", "-z")):
        dirty.update(filter(None, _git(root, *args).decode().split("\0")))
    for path in dirty:
        try:
            category = classify_path(path)
        except CorrespondenceError:
            category = "UNKNOWN"
        require(category != "CRITICAL", "C023 dirty critical input: " + path)
        cache = (any(path == prefix or path.startswith(prefix + "/") for prefix in IGNORED_ALLOWED_ROOTS)
                 or (path.startswith("tools/__pycache__/") and path.endswith(".pyc")))
        require(path in GOVERNANCE or (path in ignored and cache),
                "C023 dirty path outside exact governance/cache inventory: " + path)
    for path in HOSTS:
        require(candidate_tree := _tree(root, C).get(path), "C023 candidate proof absent: " + path)
        require(raw_bytes(root, C, path), "C023 empty candidate proof: " + path)
    require(MAPPING in tree and TRANSITIONS in tree,
            "C023 governance mapping/catalog must be committed")
    _stage_and_live(root, head, MAPPING, tree[MAPPING])
    _stage_and_live(root, head, TRANSITIONS, tree[TRANSITIONS])
    return {"contract": "c023_usb_index", "phase": phase, "candidate": C, "base": B,
            "target": head, "critical_paths": previous.CRITICAL | CRITICAL,
            "source_candidates": {path: source_candidate for path in CRITICAL},
            "changed_paths": frozenset(delta), "accepted_metadata_paths": frozenset(),
            "object_roots": frozenset(set(prior["object_roots"]) | {C, B})}


@original._proof_invocation
def verify_current_source(root: Path, path: str, historical_sha256: str | None = None):
    root = Path(root).resolve()
    old = raw_bytes(root, B, path)
    if historical_sha256 is not None:
        require(sha(old) == historical_sha256, "C023 historical source identity mismatch: " + path)
    current = current_bytes(root, path)
    if current != old:
        proof = authenticate(root)
        owner = proof["source_candidates"].get(path)
        require(owner is not None and current == raw_bytes(root, owner, path),
                "unadopted C023 current source overlay: " + path)
    return old


@original._proof_invocation
def replay_covered_checker_paths(root: Path) -> frozenset[str]:
    """Preserve exact C022 replay coverage and add no generic path exemption."""
    proof = authenticate(root)
    require(proof["contract"] == "c023_usb_index"
            and proof["candidate"] == C,
            "C023 replay coverage lacks exact source-free candidate authentication")
    return previous.replay_covered_checker_paths(root)
