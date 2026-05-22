# AGENTS

This repository is the Glyph firmware and backend realization workstream for Senscope.

Scope boundaries:

- Main Senscope semantic-source work lives elsewhere.
- The no-smash / dataset semantic pipeline must not be modified here.
- Firmware behavior changes require explicit scope approval.
- This repo is for repo-local docs, build support, and realization-layer work.

Operating rules:

- Use `./scripts/pio-local.sh` or `python -m platformio` for repo-local PlatformIO work.
- Do not use `git reset`, `git clean`, `git stash`, `git revert`, or `git push --force`.
- Final workflow is commit, push, stop, report.
- Preferred baseline verification is `./scripts/pio-local.sh run -e glyph_mk6`.

If a task would cross from docs/setup into firmware behavior, stop and re-scope first.
