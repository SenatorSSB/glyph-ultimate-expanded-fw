# Runner Boundary

Status label: CURRENT.

This repository does not need a bespoke orchestration runner for the current
workflow: `CUSTOM_RUNNER_NOT_REQUIRED`.

## Not Implemented Here

- Custom-runner prompt or daemon.
- `scripts/agent_runner.py`.
- External scheduled automation creation or mutation. Exact operator-facing
  task prompts exist in `SCHEDULED_TASKS.md`, but they do not create schedules.
- Browser/device write.
- WebSerial/device write.
- Protobuf binary write.
- Backend config.pb write.
- Persistent runtime-config storage.
- Flashing automation.
- Runtime-loaded profile/config path.

## Future Relationship

The framework docs, schemas, queue, and examples may later be consumed by a
runner only if a concrete unmet requirement justifies it, such as headless CI,
a machine API, provider-neutral orchestration, strict external budgets,
regulated audit, special authentication, or hard isolation that native Codex
cannot provide.
Any future runner must remain subordinate to repository gates:

- It must not bypass build proof.
- It must not bypass hardware PASS requirements for active behavior changes.
- It must not bypass source-authority boundaries.
- It must not create runtime-loaded config or device-write behavior by
  implication.
- It must preserve current facts unless new evidence changes them: Nunchuk
  remains NOT_TESTED, root cause remains unproven, and runtime-loaded config is
  not implemented.
