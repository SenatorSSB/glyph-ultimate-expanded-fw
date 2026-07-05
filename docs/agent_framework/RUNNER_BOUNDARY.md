# Runner Boundary

Status label: CURRENT.

This branch is not doing runner work.

## Not Implemented Here

- Runner prompt.
- Runner daemon.
- `scripts/agent_runner.py`.
- Scheduled automation.
- Browser/device write.
- WebSerial/device write.
- Protobuf binary write.
- Backend config.pb write.
- Persistent runtime-config storage.
- Flashing automation.
- Runtime-loaded profile/config path.

## Future Relationship

The framework docs, schemas, and examples may later be consumed by a runner.
Any future runner must remain subordinate to repository gates:

- It must not bypass build proof.
- It must not bypass hardware PASS requirements for active behavior changes.
- It must not bypass source-authority boundaries.
- It must not create runtime-loaded config or device-write behavior by
  implication.
- It must preserve current facts unless new evidence changes them: Nunchuk
  remains NOT_TESTED, root cause remains unproven, and runtime-loaded config is
  not implemented.
