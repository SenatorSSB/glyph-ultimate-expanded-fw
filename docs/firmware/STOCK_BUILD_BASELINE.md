# Stock Build Baseline

Known successful baseline command for debugging full output:

- `./scripts/pio-local.sh run -e glyph_mk6`

Preferred quiet build command for normal build-affecting tasks:

- `./scripts/build-glyph-mk6-quiet.sh`

Expected stock build artifacts:

- `.pio/build/glyph_mk6/firmware.uf2`
- `.pio/build/glyph_mk6/firmware.bin`
- `.pio/build/glyph_mk6/firmware.elf`

Build and cache artifacts are ignored locally through `.gitignore`.

Do not paste full successful PlatformIO logs into final reports. On build failure, report only the final 80 log lines unless more detail is requested.
