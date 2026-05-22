# Agent Stop Conditions

Stop immediately and report if any of the following occur:

- A requested change would alter firmware behavior without explicit scope.
- A change would touch the no-smash / dataset semantic pipeline.
- `./scripts/pio-local.sh run -e glyph_mk6` fails in a way that indicates an environment or dependency problem.
- A source artifact is referenced but its provenance is unclear.
- A task would require `git reset`, `git clean`, `git stash`, `git revert`, or `git push --force`.
- Unexpected unrelated file changes appear and need interpretation before proceeding.

When the work is complete, the final sequence is:

1. Commit.
2. Push.
3. Stop.
4. Report what changed, what passed, and what remains missing.
