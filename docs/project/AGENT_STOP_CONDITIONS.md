# Agent Stop Conditions

Agents must stop and ask the user if any listed condition occurs.

## Source authority stop conditions

Stop if:

- backend behavior is undocumented;
- source files contradict docs;
- tests contradict source interpretation;
- a capability is inferred but not confirmed;
- behavior from another controller/backend would need to be assumed;
- repository source is insufficient to support the claim.

## Controller behavior stop conditions

Stop if task requires deciding:

- SOCD behavior;
- priority ordering;
- modifier fusion rules;
- layer/mode interaction;
- analog output scaling;
- coordinate transformation;
- USB/GC/protocol behavior;
- push-to-device behavior;
- export-file semantics;
- firmware field meaning.

unless the repo source/docs already make the answer explicit.

## Senscope integration stop conditions

Stop if task requires:

- changing neutral Profile schema;
- changing Senscope game semantic source authority;
- selecting a Smash gameplay semantic source;
- changing no-smash/no-strong-input behavior;
- adding gameplay thresholds;
- treating backend constraints as game semantics.

## Git / repo safety stop conditions

Stop if task appears to require:

- `git reset`;
- `git clean`;
- `git stash`;
- `git revert`;
- force-push;
- deleting source files;
- broad unrelated rewrites;
- dependency installation not justified by repo setup.

## Test stop conditions

Stop if:

- targeted tests fail after reasonable local fixes;
- test failures imply backend behavior changed;
- expected outputs differ without source explanation;
- broad tests are required but too expensive/unclear.

## Export / push stop conditions

Stop before:

- implementing export file generation;
- implementing push-to-device;
- reverse-engineering private/encrypted formats;
- claiming generated files are importable by a vendor tool.

unless the task explicitly authorizes it and source support is clear.
