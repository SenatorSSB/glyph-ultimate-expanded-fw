#!/usr/bin/env python3
"""Validate public routes, current claims and selected evidence boundaries."""
from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
CURATED_PATHS = ("docs/history/HISTORY.md", "docs/history/DECISIONS.md",
                 "docs/history/HARDWARE_ACCEPTANCE.md", "docs/history/SOURCE_LINEAGE.md",
                 "docs/evidence/README.md")
PUBLIC_PATHS = ("AGENTS.md", "README.md", "docs/README.md", "docs/CURRENT_STATE.md",
                "docs/ROADMAP.md", "docs/CAPABILITIES.md", "docs/USAGE.md",
                "docs/PROFILE_SYSTEM.md", "profiles/README.md",
                "docs/ARCHITECTURE.md", "docs/DEVELOPMENT.md") + CURATED_PATHS


class DocsNavigationError(AssertionError):
    """Raised when current documentation guardrails drift."""


def fail(message: str) -> None:
    raise DocsNavigationError(message)


def normalize(text: str) -> str:
    return " ".join(text.replace("`", "").replace("**", "").split()).lower()


def current_section(text: str, kind: str) -> str:
    start, end = f"<!-- {kind}-v1:start -->", f"<!-- {kind}-v1:end -->"
    legacy = {"current-state": "legacy-current-state-journal",
              "current-roadmap": "legacy-roadmap-journal"}[kind]
    boundary = f"<!-- {legacy}:start -->"
    if (text.count(start) != 1 or text.count(end) != 1 or text.count(boundary) != 1
            or not text.index(start) < text.index(end) < text.index(boundary)):
        fail(f"{kind}: missing, duplicate or misordered current/legacy boundaries")
    # No unvalidated prose can precede the current section except the document title.
    if not re.fullmatch(r"# [^\n]+\s*", text.split(start)[0]):
        fail(f"{kind}: current prose outside bounded section")
    return text.split(start)[1].split(end)[0]


def require(label: str, text: str, phrases: tuple[str, ...]) -> None:
    missing = [p for p in phrases if normalize(p) not in normalize(text)]
    if missing:
        fail(f"{label}: missing " + ", ".join(missing))


def links(text: str) -> set[str]:
    return set(re.findall(r"\[[^]\n]*\]\(([^)\s]+)\)", text))


def require_links(label: str, text: str, targets: tuple[str, ...]) -> None:
    missing = set(targets) - links(text)
    if missing:
        fail(f"{label}: missing routes " + ", ".join(sorted(missing)))


def reject_stale_claims(label: str, text: str) -> None:
    n = normalize(text)
    patterns = (
        r"(?:public (?:beta|release)|final public release) (?:is |has been )?(?:available|published|released|complete|launched|ready now|exists)",
        r"runtime[- ]loaded (?:config|profiles?) (?:is|are) not implemented",
        r"(?:webserial/device write|protobuf binary write|runtime-config storage|firmware binary/protobuf parser integration) is not implemented",
    )
    if any(re.search(p, n) for p in patterns):
        fail(f"{label}: stale blanket capability or positive public-release claim")


def status_row(text: str, name: str, required_status: str) -> None:
    rows = [line for line in text.splitlines() if line.startswith(f"| {name} |")]
    if len(rows) != 1:
        fail(f"current-state: expected one qualification row for {name}")
    status = rows[0].split("|")[2]
    require(name, status, (required_status,))
    if name == "DInput" and re.search(r"\bPASS\b", status):
        fail("current-state: selected DInput physical qualification must remain N/A")


def validate_current_state(text: str) -> str:
    current = current_section(text, "current-state")
    require("current-state", current, ("configurator", "integration is COMPLETE",
        "PREPARED_NOT_ACTIVATED", "NOT_RELEASED", "Senscope complete-path acceptance",
        "dcf6e29589f558a95c021bef491578f87e41750f",
        "a7731388430ea70dbe666298953795f4018069b0",
        "2c77e2b7e50af2fd3b516d1ee7d0b8a67bcf992d6fcf0e3109a837422740cd42",
        "1,325,568", "API-visible"))
    for name, status in (("DInput", "N/A"), ("Browser Gamepad API / JoyCheck", "NOT_QUALIFIED"),
                         ("Keyboard", "DEFERRED / NOT_TESTED"), ("Switch 2", "OUT_OF_SCOPE / NOT_TESTED"),
                         ("Nunchuk", "NOT_TESTED"), ("Fresh Install / recovery hardening", "DEFERRED / UNQUALIFIED")):
        status_row(current, name, status)
    reject_stale_claims("current-state", current)
    return current


def validate_roadmap(text: str) -> str:
    current = current_section(text, "current-roadmap")
    require("roadmap", current, ("## Near-term preparation", "## Later / conditional",
        "PREPARED_NOT_ACTIVATED", "NOT_RELEASED", "Senscope", "DInput", "Fresh Install"))
    reject_stale_claims("roadmap", current)
    return current


def check_public_agents_contract(text: str) -> None:
    """Validate public safety and routes without mirroring internal orchestration."""
    n = " ".join(text.replace("`", "").replace("**", "").split()).lower()
    targets = set(re.findall(r"\[[^]\n]*\]\(([^)\s]+)\)", text))
    for target in ("docs/DEVELOPMENT.md", "docs/ARCHITECTURE.md", "docs/CURRENT_STATE.md",
                   "docs/CAPABILITIES.md", "docs/PROFILE_SYSTEM.md", "profiles/README.md",
                   "docs/runtime_config/IMPLEMENTATION_BOUNDARY.md"):
        if target not in targets:
            fail(f"AGENTS: missing public route {target}")
    if "pio run -e glyph_mk6" not in n:
        fail("AGENTS: missing canonical Mk6 build command")
    if "./scripts/build-glyph-mk6-quiet.sh" not in n:
        fail("AGENTS: missing fallback build command")
    distinctions = {
        "build/hardware": r"(?:ci build|build pass|build proof).{0,35}(?:is not|!=|≠|does not (?:prove|confer)|differs from).{0,25}(?:physical )?hardware (?:acceptance|pass)",
        "TIMEOUT/PASS": r"timeout.{0,15}(?:is not|!=|≠|does not mean).{0,10}pass",
        "SKIPPED/PASS": r"skipped.{0,15}(?:is not|!=|≠|does not mean).{0,10}pass",
    }
    for label, pattern in distinctions.items():
        if not re.search(pattern, n):
            fail(f"AGENTS: missing {label} distinction")
    for pattern in (
        r"(?:ci build|build pass|build proof).{0,20}(?:proves|is|inherits|confers) (?:physical )?hardware (?:acceptance|pass)",
        r"(?:timeout|skipped) (?:is|means|equals) pass",
    ):
        if re.search(pattern, n):
            fail("AGENTS: build/incomplete validation cannot confer acceptance")
    # Internal names may occur in a short retained-history note, never as the
    # public operating instructions. Check affirmative requirements even there.
    operational = re.split(r"^## (?:Legacy|Historical)[^\n]*\n", text, maxsplit=1, flags=re.M | re.I)[0]
    internal = r"AGENT_CONTEXT|WORKFLOW\.md|agent_framework|ACTIVE_AGENT_QUEUE|\bPlanner\b|\bCurator\b|\bRunner\b|\brunway\b|PREAUTHORIZED|\bREADY\b|GLYPH-UD-|daemon|model.routing|scheduled.task|queue promotion"
    if re.search(internal, operational, re.I):
        fail("AGENTS: public workflow operationalizes internal campaign machinery")
    if re.search(r"(?:active_agent_queue|ready work order).{0,70}(?:is required|must|required for|every ordinary task)", n):
        fail("AGENTS: ordinary tasks cannot require a queue/work order")
    if re.search(r"(?:must|required to|first) (?:read|follow|use).{0,60}(?:agent_context|workflow\.md|agent_framework|active_agent_queue|planner|curator|runway)", n):
        fail("AGENTS: historical/internal material is not a public prerequisite")
    # Require the complete explicit action-specific device boundary in one
    # paragraph, not scattered references to devices and general task approval.
    device = next((" ".join(p.split()).lower() for p in text.replace("`", "").split("\n\n")
                   if re.search(r"(?:no|do not|never).{0,25}(?:firmware )?flash", p, re.I | re.S)), "")
    if (not all(re.search(pattern, device) for pattern in (
            r"serial/device write|serial.{0,15}device write", r"hidden device mutation",
            r"destructive recovery", r"controller operation"))
            or not re.search(r"unless.{0,20}(?:the )?user.{0,20}explicitly authoriz.{0,35}(?:specific|particular|exact) device action", device)):
        fail("AGENTS: missing explicit authorization for each specific device action")
    if not re.search(r"(?:never|do not).{0,20}automatic.{0,130}(?:credential|token)", n):
        fail("AGENTS: missing protection against automatic GitHub credential changes")
    if not re.search(r"network failure.{0,15}(?:is not|!=|does not (?:prove|mean)).{0,20}authentication", n):
        fail("AGENTS: network failure is not authentication proof")
    for sentence in re.split(r"[.\n]", n):
        if re.search(r"(?:network|dns).{0,25}fail|after.{0,20}fail", sentence) and re.search(
                r"(?:auto[- ]?login|automatically (?:log|change)|(?:run|use) gh auth login|change (?:github )?credentials)", sentence):
            if not re.search(r"never|do not|must not", sentence):
                fail("AGENTS: network failure cannot authorize account mutation")


def check_public_agent_routes(index: str, current: str | None = None) -> None:
    """Keep coding-agent and contributor entry points distinct and public."""
    rows = [line for line in index.splitlines() if re.search(r"coding agents", line, re.I)]
    if len(rows) != 1 or not all(f"]({target})" in rows[0] for target in
                                ("../AGENTS.md", "DEVELOPMENT.md", "ARCHITECTURE.md")):
        fail("docs index: coding-agent route must use AGENTS then public technical docs")
    internal = r"AGENT_CONTEXT|ACTIVE_AGENT_QUEUE|WORKFLOW\.md|agent_framework|\bPlanner\b|\bCurator\b|\brunway\b"
    if re.search(internal, rows[0], re.I):
        fail("docs index: coding-agent route requires internal workflow")
    if current is not None:
        # The bounded current owner is public; legacy journals are not scanned.
        if re.search(internal, current, re.I):
            fail("current-state: normal developer/agent route requires internal workflow")
        for target in ("DEVELOPMENT.md", "../AGENTS.md", "runtime_config/IMPLEMENTATION_BOUNDARY.md"):
            if f"]({target})" not in current:
                fail(f"current-state: missing public/safety route {target}")
        n = " ".join(current.split()).lower()
        if not re.search(r"native ultimate/profilestore lane.{0,35}does not authorize.{0,30}generic runtime configuration.{0,20}new device operations", n):
            fail("current-state: missing native lane/runtime/device boundary")


def validate_technical_surface(docs: dict[str, str]) -> None:
    """Protect relationships and reader routes, allowing prose/diagram rewording."""
    def route(path: str, reader: str, target: str) -> None:
        rows = [line for line in docs[path].splitlines() if re.search(reader, line, re.I)]
        if not any(f"]({target})" in line for line in rows):
            fail(f"{path}: missing {reader} route to {target}")

    route("README.md", r"\bdevelopers\b", "docs/DEVELOPMENT.md")
    route("README.md", r"coding agents", "AGENTS.md")
    route("docs/README.md", r"\bdevelopers\b", "DEVELOPMENT.md")
    # The developer route must not require old orchestration as a second step.
    for path in ("README.md", "docs/README.md"):
        for line in docs[path].splitlines():
            if re.search(r"\bdevelopers\b", line, re.I) and re.search(
                    r"AGENTS\.md|WORKFLOW\.md|AGENT_CONTEXT|ACTIVE_AGENT_QUEUE|agent_framework", line):
                fail(f"{path}: developer route depends on internal agent workflow")
    architecture = docs["docs/ARCHITECTURE.md"]
    development = docs["docs/DEVELOPMENT.md"]
    for path, text, targets in (
        ("architecture", architecture, ("PROFILE_SYSTEM.md", "CAPABILITIES.md",
            "../platformio.ini", "../config/glyph/common/src/config.cpp",
            "../src/core/mode_selection.cpp", "../include/core/ProfileStore.hpp")),
        ("development", development, ("ARCHITECTURE.md", "CURRENT_STATE.md", "PROFILE_SYSTEM.md")),
    ):
        for target in targets:
            if f"]({target})" not in text:
                fail(f"{path}: missing technical route {target}")
    a, d = normalize(architecture).replace("**", ""), normalize(development).replace("**", "")
    def distinction(label: str, text: str, pattern: str) -> None:
        if not re.search(pattern, text):
            fail(f"technical docs: missing {label} distinction")
    distinction("row/engine", a, r"(?:row label|profile label).{0,30}(?:is not|differs from|!=|≠).{0,25}mode engine")
    distinction("engine/backend", a, r"mode engine.{0,30}(?:is not|differs from|!=|≠).{0,25}(?:communication )?backend")
    distinction("row/record", a, r"config row.{0,25}(?:is not|differs from|!=|≠).{0,25}profilestore record")
    distinction("record/package", a, r"(?:neither alone is|record (?:is not|!=|≠|differs from)).{0,20}complete package")
    distinction("Configurator/website", a, r"configurator (?:firmware )?transport.{0,40}(?:distinct from|is not|differs from).{0,30}retired official configurator website")
    distinction("build/hardware", d, r"(?:ci build|build pass|build proof).{0,35}(?:is not|!=|≠|differs from).{0,25}(?:physical )?hardware (?:acceptance|pass)")
    if re.search(r"(?:ci build|build pass|build proof).{0,20}(?:proves|is|inherits) (?:physical )?hardware (?:acceptance|pass)", d):
        fail("development: build cannot confer hardware acceptance")
    for status in ("timeout", "skipped"):
        distinction(f"{status}/PASS", d, rf"{status}.{{0,15}}(?:is not|!=|≠|does not mean).{{0,10}}pass")
        if re.search(rf"{status} (?:is|means|equals) pass", d):
            fail(f"development: {status} cannot mean PASS")
    if "pio run -e glyph_mk6" not in d:
        fail("development: missing canonical build command")
    # Only the introductory normal path is dependency-free; the final migration
    # note may name retained internal files without making them prerequisites.
    intro = re.split(r"^## ", development, flags=re.M)
    supported = next((s for s in intro if s.lower().startswith("supported public development path")), "")
    if not supported or re.search(r"ACTIVE_AGENT_QUEUE|agent_framework|WORKFLOW\.md|AGENT_CONTEXT", supported):
        fail("development: normal public path requires internal campaign documents")
    if not re.search(r"^## Documentation maintenance policy\s*$", development, re.M):
        fail("development: missing documentation ownership policy")
    policy = development.split("## Documentation maintenance policy", 1)[1].split("\n## ", 1)[0]
    for owner in ("CURRENT_STATE", "CAPABILITIES", "USAGE", "PROFILE_SYSTEM", "ARCHITECTURE",
                  "DEVELOPMENT", "ROADMAP", "profiles/README", "history", "evidence"):
        if not any(owner in line for line in policy.splitlines() if line.startswith("|")):
            fail(f"development: missing canonical owner {owner}")
    for pattern in (r"mode engine is (?:the same as|a) (?:communication )?backend",
                    r"config row is (?:itself )?a profilestore record",
                    r"profilestore record is (?:itself )?a complete package",
                    r"configurator transport is the (?:retired )?official configurator website"):
        if re.search(pattern, a):
            fail("architecture: conflated system responsibilities")


def validate_history_surface(docs: dict[str, str]) -> None:
    """Protect scoped evidence and ownership; do not validate entire timelines."""
    index = docs["docs/README.md"]
    routes = ("history/HISTORY.md", "history/DECISIONS.md",
              "history/HARDWARE_ACCEPTANCE.md", "history/SOURCE_LINEAGE.md", "evidence/README.md")
    historical_rows = "\n".join(line for line in index.splitlines()
                                if "historical/evidence research" in line.lower())
    require_links("historical reader route", historical_rows, routes)
    if re.search(r"ACTIVE_AGENT_QUEUE|agent_framework", historical_rows):
        fail("historical reader route requires internal orchestration")
    history, decisions, hardware, lineage, evidence = (docs[p] for p in CURATED_PATHS)
    require_links("history current owner", history, ("../CURRENT_STATE.md",))
    h = normalize(history)
    if not re.search(r"current_state.{0,60}owns (?:present|current) truth", h):
        fail("history: ambiguous present-truth owner")
    if not re.search(r"(?:selected chronology|selected milestones).{0,80}(?:not exhaustive|not an exhaustive)", h):
        fail("history: selected chronology must not claim completeness")
    if re.search(r"history.{0,25}(?:owns|is the authority for) (?:present|current) truth", h):
        fail("history cannot replace current truth")
    for entry in re.split(r"^### ", decisions, flags=re.M)[1:]:
        require("decision entry", entry, ("Status:", "Scope:", "Sources:"))
        if not re.search(r"status:\s*(?:current|historical|superseded)\b", normalize(entry)):
            fail("decision: missing explicit status")
    if not re.search(r"^### ", decisions, re.M):
        fail("decisions: missing scoped entries")
    tested = "dcf6e29589f558a95c021bef491578f87e41750f"
    tree = "a7731388430ea70dbe666298953795f4018069b0"
    uf2 = "2c77e2b7e50af2fd3b516d1ee7d0b8a67bcf992d6fcf0e3109a837422740cd42"
    for name, text in (("hardware", hardware), ("lineage", lineage)):
        require(name, text, (tested, tree, uf2))
        # Identity is bound to the labelled row, not merely mentioned elsewhere.
        source_rows = [line for line in text.splitlines() if line.startswith("| Tested source |")]
        if len(source_rows) != 1 or tested not in source_rows[0]:
            fail(f"{name}: tested source identity was replaced by a descendant")
    require("hardware size", hardware, ("1,325,568",))
    for name, status in (("DInput", "N/A"), ("Browser Gamepad API / JoyCheck", "NOT_QUALIFIED"),
                         ("Nunchuk", "NOT_TESTED")):
        status_row(hardware, name, status)
        row = next(line for line in hardware.splitlines() if line.startswith(f"| {name} |"))
        if re.search(r"\bPASS\b", row.split("|")[2]):
            fail(f"hardware: cannot promote {name} to PASS")
    for name, text in (("hardware", hardware), ("lineage", lineage)):
        n = normalize(text)
        if not re.search(r"(?:build proof|build success|ci rebuild).{0,35}(?:is not|!=|does not (?:confer|inherit)).{0,25}(?:physical )?hardware acceptance", n):
            fail(f"{name}: missing build/acceptance distinction")
        if re.search(r"(?:ci (?:re)?build|rebuild|build proof) (?:automatically |now |also )?(?:inherits?|confers?|proves?) (?:physical )?hardware acceptance", n):
            fail(f"{name}: rebuild cannot inherit physical acceptance")
    n = normalize(lineage)
    if not re.search(r"later.{0,35}descendants.{0,50}(?:are not|do not become).{0,25}tested source", n):
        fail("lineage: later descendants must remain distinct from tested source")
    if not re.search(r"fresh.{0,40}(?:commit|repository).{0,70}(?:does not|will not).{0,35}(?:become|is).{0,35}physically tested (?:source )?commit", n):
        fail("lineage: fresh-history commit cannot become physically tested commit")
    if re.search(r"fresh.{0,40}(?:commit|repository).{0,30}(?:is|becomes|will become) the physically tested (?:source )?commit", n):
        fail("lineage: false fresh-history physical identity")
    if not re.search(r"linking evidence.{0,60}(?:does not|cannot).{0,30}(?:broaden|upgrade).{0,15}(?:its )?scope", normalize(evidence)):
        fail("evidence: missing scope warning")
    for path in CURATED_PATHS:
        # Scan prose AND link targets. Raw/private inputs remain at their original
        # owner-controlled location; only sanitized repository records are public.
        if re.search(r"(?:/Users/|/home/|/private/|/tmp/|file://|[A-Za-z]:[\\/]|local_backups/|private[-_ ]capture[-_ ]path|private[-_ ]artifact[-_ ]location|[\w.+-]+@[\w.-]+\.[A-Za-z]{2,})", docs[path], re.I):
            fail(f"{path}: private locator/contact in curated public evidence")


def validate_docs(root: Path = REPO_ROOT, overrides: dict[str, str] | None = None) -> None:
    """Overrides let tests mutate current prose without touching tracked files."""
    docs = {}
    for path in PUBLIC_PATHS:
        docs[path] = overrides[path] if overrides and path in overrides else (root / path).read_text(encoding="utf-8")
    check_public_agents_contract(docs["AGENTS.md"])
    validate_technical_surface(docs)
    validate_history_surface(docs)
    docs["docs/CURRENT_STATE.md"] = validate_current_state(docs["docs/CURRENT_STATE.md"])
    docs["docs/ROADMAP.md"] = validate_roadmap(docs["docs/ROADMAP.md"])
    check_public_agent_routes(docs["docs/README.md"], docs["docs/CURRENT_STATE.md"])
    require_links("README", docs["README.md"], ("docs/USAGE.md", "docs/CAPABILITIES.md",
        "docs/CURRENT_STATE.md", "profiles/README.md", "docs/README.md", "docs/ROADMAP.md", "AGENTS.md"))
    if "profiles/ultimate/README.md" in links(docs["README.md"]):
        fail("README: historical v0 golden must not be the primary authoring route")
    for path in ("README.md", "docs/USAGE.md", "docs/CAPABILITIES.md"):
        require(path, docs[path], ("30 profile rows total", "shared 30-row budget"))
    for path in ("docs/README.md", "docs/USAGE.md", "docs/CAPABILITIES.md"):
        require_links(path, docs[path], ("../profiles/README.md",))
    require("docs index", docs["docs/README.md"], ("Players / users", "Profile authors", "Developers",
        "Coding agents", "Historical/evidence research", "## Compact glossary"))
    for path in ("docs/README.md", "docs/CAPABILITIES.md", "docs/USAGE.md"):
        require_links(path, docs[path], ("PROFILE_SYSTEM.md",))
    system, authoring = docs["docs/PROFILE_SYSTEM.md"], docs["profiles/README.md"]
    require_links("profile system", system, ("../profiles/README.md",))
    require_links("authoring", authoring, (
        "../docs/PROFILE_SYSTEM.md", "schema/glyph-native-ultimate-profile.v1.schema.json",
        "templates/UltimateNativeSeed.v1.profile.json"))
    require("authoring", authoring, ("LLM authoring contract", "historical v0", "archival"))
    for path, text in (("profile system", system), ("authoring", authoring)):
        n = normalize(text)
        if not re.search(r"(?:key|direction) 5.{0,100}non-center", n):
            fail(f"{path}: retain the nine-way/non-center key 5 distinction")
        if not all(str(i) in n for i in range(1, 10)) or "7 8 9 4 5 6 1 2 3" not in n:
            fail(f"{path}: missing nine-way indexing grid")
        if not re.search(r"(?:not a complete package|does not (?:create|install) a complete package)", n):
            fail(f"{path}: retain authoring versus complete-package boundary")
        unsupported = (
            r"authoring json is (?:itself )?a complete package",
            r"(?:supports?|provides?|implements?) arbitrary (?:scripts?|scripting|timers?|macros?)",
            r"(?:scripts?|timers?|macros?) (?:are|is) supported",
        )
        if any(re.search(pattern, n) for pattern in unsupported):
            fail(f"{path}: unsupported package or scripting claim")
    cap = docs["docs/CAPABILITIES.md"]
    require("capabilities", cap, ("## Mode engines", "## Communication backends", "## Native Ultimate profiles",
        "## Profile and package management", "## Physical qualification", "Keyboard is not a backend"))
    backend = cap.split("## Communication backends", 1)[1].split("\n## ", 1)[0]
    if re.search(r"^\|[^|]*\bKeyboard\b[^|]*\|", backend, re.M | re.I):
        fail("capabilities: Keyboard cannot be a transport backend row")
    for path, text in docs.items():
        reject_stale_claims(path, text)
        for target in links(text):
            if "://" in target:
                continue
            dest, _, anchor = target.partition("#")
            resolved = (root / path).parent / dest if dest else root / path
            if not resolved.is_file():
                fail(f"{path}: broken local link {target}")
            if anchor:
                headings = re.findall(r"^#+ (.+)$", resolved.read_text(encoding="utf-8"), re.M)
                slugs = {re.sub(r"[^\w -]", "", h.lower()).replace(" ", "-") for h in headings}
                if anchor not in slugs:
                    fail(f"{path}: missing anchor {target}")
    # Player navigation may never depend on internal queues or calibration packets.
    for path in ("README.md", "docs/USAGE.md"):
        if any("calibration/" in t or "ACTIVE_AGENT_QUEUE" in t for t in links(docs[path])):
            fail(f"{path}: player path depends on historical/agent archaeology")


def main() -> int:
    validate_docs()
    print("glyph_docs_navigation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
