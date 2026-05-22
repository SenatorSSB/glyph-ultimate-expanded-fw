# Build and Flash Notes

Use repo-local PlatformIO:

- `./scripts/pio-local.sh`
- or `python -m platformio`

High-level caution only:

- Keep build artifacts and caches local to the repo.
- Do not rely on global PlatformIO state.
- Do not add flashing procedures here unless they are already sourced in repo docs.

Known stock verification command:

- `./scripts/pio-local.sh run -e glyph_mk6`
