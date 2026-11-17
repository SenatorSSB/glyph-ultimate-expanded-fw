#!/usr/bin/env python3
"""Validate public navigation and bounded current claims, not historical journals."""
from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
PUBLIC_PATHS = ("README.md", "docs/README.md", "docs/CURRENT_STATE.md",
                "docs/ROADMAP.md", "docs/CAPABILITIES.md", "docs/USAGE.md")


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


def validate_docs(root: Path = REPO_ROOT, overrides: dict[str, str] | None = None) -> None:
    """Overrides let tests mutate current prose without touching tracked files."""
    docs = {}
    for path in PUBLIC_PATHS:
        docs[path] = overrides[path] if overrides and path in overrides else (root / path).read_text(encoding="utf-8")
    docs["docs/CURRENT_STATE.md"] = validate_current_state(docs["docs/CURRENT_STATE.md"])
    docs["docs/ROADMAP.md"] = validate_roadmap(docs["docs/ROADMAP.md"])
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
