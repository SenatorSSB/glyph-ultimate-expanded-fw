"""Finite GP-VAL-042 authentication for the exact C023 candidate."""
from __future__ import annotations

import hashlib
import json
import re
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
VAL042_I = "c2b604b1edf5bfa0551fe73a568a1f50a48ea30d"
TREE = "da886ff6d9b2d545bd93ce50745ae353129d8e7c"
RAW = "0bd5c9cfc481bb4e7fc3b595f59efa7c415695a7b01df3b55a84ebfd66a6a4b4"
F = "36bf0f314afe19fc8fcbf4caf97b5bf5f83dac39"
F_TREE = "45fa24dc7f95a5cd0e796c2c7c3b46f91688b329"
ARTIFACT_SHA256 = "7e8833e5a83d1656e51f9ca258de78e7808eda2a6f3da918759a1553575f1224"
ARTIFACT_SIZE = 803840
R = "0f1648fb9c17fbded5bc1265b2702c542e689ce0"
PROTOCOL_SHA256 = "97ab3e50e10f38c012544b523cb67cebed32faf261b47609fdd6c095337a5c66"
MAPPING = "docs/runtime_config/fixtures/gp_val042_c023_transition.json"
TRANSITIONS = "docs/runtime_config/fixtures/gp_val042_accepted_transitions.json"
PROTOCOL = "docs/agent_framework/GP_CONFIG_023_HARDWARE_PROTOCOL.md"
RESULT = "docs/calibration/gp_config_023_hardware_result.md"
EVIDENCE = "docs/calibration/fixtures/gp_config_023_hardware_evidence.json"
HANDOFF_START = "<!-- gp-config023-handoff-val042-activation:start -->"
HANDOFF_END = "<!-- gp-config023-handoff-val042-activation:end -->"
REQUIRED_ROWS = (
    "valid_stored_startup", "ordinary_selection_profile_modifier",
    "reconnect_reboot", "external_invalid_index_rejection",
    "invalid_stored_refusal_gc_usb", "invalid_stored_refusal_reboot",
    "manual_recovery", "restoration", "rollback", "safe_stop_and_anomalies",
)
KEYBOARD_DISPOSITION = "NOT_TESTED / DEFERRED_POST_FIRST_PUBLIC_BETA"
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
    PROTOCOL, RESULT, EVIDENCE,
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


def _hardware_pending_contract(root: Path, order: dict) -> dict:
    """Accept only the reviewed exact-F pending handoff, with no physical result."""
    expected_locator = (
        "local_backups/hardware-artifacts/"
        f"{F}/{ARTIFACT_SHA256}/firmware.uf2"
    )
    require(
        order["status"] == "HARDWARE_TEST_REQUIRED"
        and order["branch"] == "codex/gp-config-023-release-safety"
        and order["candidate_git_sha"] == F
        and order["candidate_base_configurator_sha"] == B
        and order["firmware_artifact_build_path"] == ".pio/build/glyph_mk6/firmware.uf2"
        and order["preserved_firmware_artifact_locator"] == expected_locator
        and order["firmware_artifact_sha256"] == ARTIFACT_SHA256
        and order["hardware_evidence_dependency_satisfied"] is False
        and order["hardware_evidence_record"] is None
        and order["hardware_result"] is None
        and order["hardware_evidence_gaps"] == [],
        "C023 hardware-pending queue identity or non-claim changed",
    )
    require(
        _git(root, "rev-list", "--parents", "-n", "1", F).decode().split() == [F, C]
        and _git(root, "rev-parse", F + "^{tree}").decode().strip() == F_TREE,
        "C023 exact F parent/tree changed",
    )
    evidence = json.loads(current_bytes(root, EVIDENCE), object_pairs_hook=unique)
    required_rows = (
        "valid_stored_startup", "ordinary_selection_profile_modifier",
        "reconnect_reboot", "external_invalid_index_rejection",
        "invalid_stored_refusal_gc_usb", "invalid_stored_refusal_reboot",
        "manual_recovery", "restoration", "rollback", "safe_stop_and_anomalies",
    )
    require(
        evidence["work_order_id"] == "GP-CONFIG-023"
        and evidence["candidate_branch"] == order["branch"]
        and evidence["candidate_git_sha"] == F
        and evidence["candidate_base_configurator_sha"] == B
        and evidence["firmware_artifact_sha256"] == ARTIFACT_SHA256
        and evidence["preserved_firmware_artifact_locator"] == expected_locator
        and evidence["candidate_protocol_reference"] == PROTOCOL
        and evidence["candidate_protocol_version"] == "GP_CONFIG_023_HW_V1"
        and evidence["pre_update_sha256_verified"] is False
        and evidence["result"] == "NOT_TESTED"
        and evidence["anomalies"] == []
        and [step["id"] for step in evidence["steps"]] == list(required_rows)
        and all(step["observed"].startswith("NOT_TESTED") for step in evidence["steps"])
        and evidence["rollback_recovery"].startswith("NOT_TESTED")
        and len(evidence["evidence_gaps"]) == len(required_rows),
        "C023 pending fixture must preserve exact identity and all physical rows NOT_TESTED",
    )
    protocol = current_bytes(root, PROTOCOL).decode("utf-8")
    result = current_bytes(root, RESULT).decode("utf-8")
    protocol_identity = (
        F, F_TREE, C, B, ARTIFACT_SHA256, expected_locator,
        "Do not write a Config or prepare/store an invalid Config without separate explicit owner approval",
        "The owner performs any device or Config action manually",
        "No executor or reviewer writes to a device",
    )
    require(
        "Status: `HARDWARE_TEST_REQUIRED`" in protocol
        and all(f"`{row}`" in protocol for row in required_rows)
        and all(value in protocol for value in protocol_identity)
        and F in result
        and ARTIFACT_SHA256 in result
        and "NOT_TESTED / HARDWARE_TEST_REQUIRED" in result
        and "no physical test" in result,
        "C023 pending protocol/result identity or physical non-claim changed",
    )
    return evidence


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
    _catalog(catalog, prior_catalog)
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


def _catalog(value: dict, prior: list) -> list:
    require(set(value) == {"schema_version", "accepted_transitions"}
            and type(value["schema_version"]) is int and value["schema_version"] == 1
            and type(value["accepted_transitions"]) is list,
            "C023 catalog schema substitution")
    records = value["accepted_transitions"]
    require(records[:len(prior)] == prior and len(records) in (len(prior), len(prior) + 1),
            "C023 catalog lost/replaced predecessor or added extra transition")
    added = records[len(prior):]
    if added:
        record = added[0]
        fields = {"work_order", "candidate", "build", "parent", "tree",
                  "review_commit", "evidence_commit", "integration"}
        require(type(record) is dict and set(record) == fields
                and record["work_order"] == "GP-CONFIG-023"
                and (record["candidate"], record["build"], record["parent"], record["tree"],
                     record["review_commit"]) == (C, F, C, F_TREE, R)
                and all(type(record[k]) is str and re.fullmatch("[0-9a-f]{40}", record[k])
                        for k in fields - {"work_order"}),
                "C023 accepted catalog tuple substitution")
    return added


def _hardware_rows(evidence: dict, result: bytes):
    require(evidence["result"] == "PASS"
            and evidence["anomalies"] == evidence["evidence_gaps"] == []
            and [step["id"] for step in evidence["steps"]] == list(REQUIRED_ROWS)
            and all(step["observed"].strip().startswith("PASS") for step in evidence["steps"]),
            "C023 physical row missing/failing")
    text = result.decode("utf-8")
    require(KEYBOARD_DISPOSITION in text
            and "PRESERVE_ORIGINAL_RAW_KEYBOARD_OUTPUT" in text
            and "POST_BETA_KEYBOARD_PHYSICAL_VALIDATION" in text
            and "PHYSICAL_NOT_SAFELY_TESTABLE" in text
            and "Keyboard physical PASS" not in text,
            "C023 owner scope/physical limitation missing or Keyboard PASS invented")


def _processor(root: Path, revision: str, state: dict, before: dict):
    require(state["status"] == "HARDWARE_VALIDATED"
            and state["hardware_result"] == "PASS"
            and state["hardware_evidence_dependency_satisfied"] is True
            and state["hardware_evidence_gaps"] == []
            and ancestor(root, R, revision) and not ancestor(root, F, revision)
            and critical_tree(root, revision) == before,
            "C023 first PASS must be source-free E after reviewed R")
    pending = item(root, R, "GP-CONFIG-023")
    acceptance = {"status", "hardware_result", "hardware_evidence_dependency_satisfied",
                  "hardware_evidence_gaps", "hardware_evidence_record"}
    require({k:v for k,v in state.items() if k not in acceptance}
            == {k:v for k,v in pending.items() if k not in acceptance},
            "C023 E changed non-acceptance work-order authority")
    reference = state["hardware_evidence_record"]
    if reference == "repo-json:" + EVIDENCE:
        evidence_root = revision
    else:
        match = re.fullmatch("git-json:([0-9a-f]{40}):" + re.escape(EVIDENCE), str(reference))
        require(match is not None, "C023 evidence lacks immutable Git root")
        evidence_root = match.group(1)
    require(ancestor(root, R, evidence_root) and ancestor(root, evidence_root, revision),
            "C023 evidence root outside R-to-E chronology")
    from check_glyph_agent_framework_docs import validate_work_order, validate_evidence_record
    validated = dict(state, hardware_evidence_record="git-json:" + evidence_root + ":" + EVIDENCE)
    validate_work_order(validated, evidence_repo_root=root)
    validate_evidence_record(validated, evidence_repo_root=root)
    payload = raw_bytes(root, evidence_root, EVIDENCE)
    result = raw_bytes(root, revision, RESULT)
    _hardware_rows(json.loads(payload, object_pairs_hook=unique), result)
    protocol = raw_bytes(root, revision, PROTOCOL)
    require(sha(protocol) == PROTOCOL_SHA256 and protocol == raw_bytes(root, R, PROTOCOL),
            "C023 historical protocol replaced")
    return {"evidence_commit":revision, "evidence_root":evidence_root,
            "payload":payload, "result":result, "protocol":protocol, "native":state}


def _accepted(root: Path, revision: str, record: dict, processor: dict, after: dict):
    integration = record["integration"]
    require(record["evidence_commit"] == processor["evidence_commit"]
            and _git(root, "rev-list", "--parents", "-n", "1", integration).decode().split()
                == [integration, processor["evidence_commit"], F]
            and ancestor(root, integration, revision)
            and critical_tree(root, integration) == after,
            "C023 I must be genuine exact [E,F] integration")
    old, merged = _tree(root, processor["evidence_commit"]), _tree(root, integration)
    delta = {p for p in old.keys() | merged.keys() if old.get(p) != merged.get(p)}
    require(delta == CRITICAL | HOSTS
            and all(merged[p] == _tree(root, F)[p] for p in delta),
            "C023 I contains noncandidate or incomplete source/proof delta")
    from glyph_hardware_correspondence import verify_correspondence
    verify_correspondence(root, F, C, target=revision, integrated=True, check_worktree=False)


def _lifecycle(root: Path, head: str, before: dict, after: dict):
    """Latch the first immutable E; later I and DONE retain that exact acceptance."""
    prior = previous._catalog(raw_bytes(root, B, previous.TRANSITIONS))
    processor = None
    first_catalog = None
    done = False
    for revision in _git(root, "rev-list", "--reverse", "--topo-order", R + ".." + head).decode().split():
        row = item(root, revision, "GP-CONFIG-023")
        records = (_catalog(json.loads(raw_bytes(root, revision, TRANSITIONS), object_pairs_hook=unique), prior)
                   if TRANSITIONS in _tree(root, revision) else [])
        if processor and not ancestor(root, processor["evidence_commit"], revision):
            require(row["hardware_result"] is None and row["status"] not in {"HARDWARE_VALIDATED", "DONE"}
                    and not records, "C023 competing PASS/catalog outside first E ancestry")
            continue
        accepted = row["hardware_result"] == "PASS" or row["status"] in {"HARDWARE_VALIDATED", "DONE"}
        if accepted:
            require(row["status"] in {"HARDWARE_VALIDATED", "DONE"} and row["hardware_result"] == "PASS"
                    and row["hardware_evidence_dependency_satisfied"] is True
                    and row["hardware_evidence_gaps"] == [], "C023 invalid PASS state")
            if processor is None:
                processor = _processor(root, revision, row, before)
            else:
                require(previous.stateutil.same_acceptance(row, processor["native"]),
                        "C023 immutable E acceptance replaced/downgraded")
            require(not done or row["status"] == "DONE", "C023 DONE downgraded")
        elif processor:
            require(False, "C023 accepted PASS erased")
        if processor:
            for path, key in ((PROTOCOL, "protocol"), (EVIDENCE, "payload"), (RESULT, "result")):
                require(_tree(root, revision).get(path, ())[:2] == ("100644", "blob")
                        and raw_bytes(root, revision, path) == processor[key],
                        "C023 accepted evidence/protocol/result replaced: " + path)
        if records:
            require(processor is not None, "C023 catalog before source-free E")
            if first_catalog is None:
                first_catalog = records[0]
            require(records == [first_catalog], "C023 catalog replaced")
            _accepted(root, revision, first_catalog, processor, after)
        elif first_catalog:
            require(False, "C023 accepted catalog removed")
        if row["status"] == "DONE":
            require(records, "C023 DONE before I catalog")
            from check_glyph_agent_framework_docs import validate_completion_evidence
            queue = previous.stateutil.parsed_queue(raw_bytes(root, revision, QUEUE))
            validate_completion_evidence(row, row["done_evidence"], policy=queue["completion_correspondence"],
                                         publication_sha=revision, repo_root=root)
            done = True
    state = item(root, head, "GP-CONFIG-023")
    require((state["hardware_result"] == "PASS" or state["status"] in {"HARDWARE_VALIDATED", "DONE"})
            == (processor is not None), "C023 current status/history mismatch")
    records = _catalog(json.loads(current_bytes(root, TRANSITIONS), object_pairs_hook=unique), prior)
    if processor:
        require(previous.stateutil.same_acceptance(state, processor["native"]), "C023 current acceptance replacement")
        for path in (QUEUE, PROTOCOL, EVIDENCE, RESULT):
            _stage_and_live(root, head, path, _tree(root, head)[path])
        require(critical_tree(root, head) == before or records,
                "C023 integrated PASS lacks accepted catalog")
        require(critical_tree(root, head) != before or not records,
                "C023 source-free E contains I catalog")
    else:
        require(not records, "C023 accepted catalog without HEP")
    return processor, records


@original._proof_invocation
def authenticate(root: Path):
    root = Path(root).resolve()
    before, after, prior, mapping = source_contract(root)
    head = _git(root, "rev-parse", "HEAD").decode().strip()
    require(_git(root, "rev-list", "--parents", "-n", "1", F).decode().split() == [F, C]
            and _git(root, "rev-parse", F + "^{tree}").decode().strip() == F_TREE
            and critical_tree(root, F) == after, "C023 exact tested F/source correspondence changed")
    require(ancestor(root, B, head), "C023 governance snapshot lost canonical B ancestry")
    current = critical_tree(root, head)
    require(current in (before, after), "C023 current source outside exact B/C critical trees")
    c_is_ancestor = ancestor(root, C, head)
    c023_order = item(root, head, "GP-CONFIG-023")
    val042_order = item(root, head, "GP-VAL-042")
    handoff = _handoff(root, head)
    done042 = val042_order["done_evidence"]
    require(val042_order["status"] == "DONE"
            and isinstance(done042, dict)
            and done042.get("mode") == "DIRECT_ANCESTRY"
            and done042.get("implementation_base_sha") == B
            and done042.get("reviewed_implementation_sha") == VAL042_I
            and done042.get("prior_canonical_integration_sha") == VAL042_I
            and handoff["candidate_state"] == "PRESERVED_UNBUILT_UNMERGED",
            "C023 source-free handoff requires exact GP-VAL-042 strict DONE")
    processor, records = _lifecycle(root, head, before, after)
    if processor:
        handoff_stage = "HARDWARE_VALIDATED"
    elif c023_order["status"] == "PREAUTHORIZED":
        require(c023_order["candidate_git_sha"] == C
                and c023_order["candidate_base_configurator_sha"] == B
                and c023_order["firmware_artifact_build_path"] is None
                and c023_order["hardware_result"] is None,
                "C023 pre-build queue state changed")
        handoff_stage = "PROCESSOR_READY"
    else:
        _hardware_pending_contract(root, c023_order)
        handoff_stage = "HARDWARE_PENDING"
    if current == after:
        require(c_is_ancestor, "C023 source integrated without exact candidate ancestry")
        phase = "ACCEPTED_TRANSITION" if processor else "CANDIDATE_VALIDATION_ONLY"
        source_candidate = C
    else:
        require(not c_is_ancestor, "C023 source-free governance snapshot contains candidate ancestry")
        phase = "SOURCE_FREE_PROCESSOR"
        source_candidate = C
    delta = set(filter(None, _git(root, "diff", "--no-renames", "--name-only", "-z", B, head).decode().split("\0")))
    require(delta <= GOVERNANCE | CRITICAL | (HOSTS if records else frozenset()),
            "C023 unknown governance/source delta")
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
        if records:
            require(tree.get(path) == _tree(root, F).get(path),
                    "C023 accepted host proof differs from exact F: " + path)
            _stage_and_live(root, head, path, tree[path])
    require(MAPPING in tree and TRANSITIONS in tree,
            "C023 governance mapping/catalog must be committed")
    _stage_and_live(root, head, MAPPING, tree[MAPPING])
    _stage_and_live(root, head, TRANSITIONS, tree[TRANSITIONS])
    return {"contract": "c023_usb_index", "phase": phase, "handoff_stage": handoff_stage,
            "candidate": C, "base": B,
            "target": head, "critical_paths": previous.CRITICAL | CRITICAL,
            "source_candidates": {path: source_candidate for path in CRITICAL},
            "changed_paths": frozenset(delta),
            "accepted_metadata_paths": frozenset((PROTOCOL, EVIDENCE, RESULT)) if processor else frozenset(),
            "evidence_commit": processor["evidence_commit"] if processor else None,
            "object_roots": frozenset(set(prior["object_roots"]) | {C, B, F, R}
                | ({processor["evidence_commit"], processor["evidence_root"]} if processor else set())
                | ({records[0]["integration"]} if records else set()))}


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
