# Build and Flash Notes

Use repo-local PlatformIO:

- `./scripts/pio-local.sh`
- or `python -m platformio`

For build-affecting tasks, prefer the quiet wrapper:

- `./scripts/build-glyph-mk6-quiet.sh`

Use `./scripts/pio-local.sh run -e glyph_mk6` only when debugging full build output.

High-level caution only:

- Keep build artifacts and caches local to the repo.
- Do not rely on global PlatformIO state.
- Do not paste full successful PlatformIO logs into final reports.
- On build failure, report only the final 80 log lines unless more detail is requested.
- Cloud environments may not have `.venv`; local environments may have `.venv`, but the scripts must fall back safely.
- Do not add flashing procedures here unless they are already sourced in repo docs.

Known stock verification command:

- `./scripts/pio-local.sh run -e glyph_mk6`
