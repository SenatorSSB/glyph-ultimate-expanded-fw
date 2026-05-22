# Agent Final Report Template

Agents must use this structure at the end of a task or batch.

```text
Summary:
- One to five bullets describing what changed.

Issues completed:
- G1 — title
- G2 — title

Files changed:
- path/to/file
- path/to/file

Verification:
- command: passed/failed/not run
- command: passed/failed/not run

Behavior changes:
- none
- or exact description

Semantic changes:
- none
- or exact description

Backend behavior claims:
- none
- source-backed: describe source
- inferred: describe uncertainty
- unknown: describe gap

Generated artifact changes:
- none
- or exact description with counts

Stop conditions hit:
- none
- or exact condition and why stopped

Follow-ups:
- next recommended issue
- risk or blocker
```

## Rules

Do not claim tests passed unless they were run.

Do not hide skipped verification.

Do not say “no semantic changes” if any gameplay labels, mappings, thresholds, or source-authority classifications changed.

Do not claim backend behavior without a source.

Do not summarize generated count changes vaguely. Provide exact counts.
