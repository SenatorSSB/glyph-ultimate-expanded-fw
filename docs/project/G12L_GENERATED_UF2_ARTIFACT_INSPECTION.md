# G12l Generated UF2 Artifact Inspection

Status: read-only generated artifact inspection. No flashing, upload command, copy-to-device command, mounted-device write, or hardware write was performed.

## Purpose

Build `glyph_mk6`, locate generated firmware artifacts, parse generated UF2 metadata read-only, and compare the generated UF2 shape against the archived official Glyph 1.0.7 Update and Clean/Fresh Install UF2 files.

This document does not approve hardware flashing. Even an Update-style candidate remains only a candidate for future human-controlled spare-device review after explicit approval.

## Build Metadata

| Field | Value |
| --- | --- |
| Branch | `docs/g12l-generated-uf2-artifact-inspection` |
| Build source commit | `52d54d16e6a057f8373cdce8eb31129a29cf0453` |
| Build source dirty/clean status | Clean before the inspection build (`git status --short` produced no output) |
| Build command | `./scripts/build-glyph-mk6-quiet.sh` |
| Build result | Passed |
| Build output summary | RAM 19.8%; Flash 24.2%; `glyph_mk6 SUCCESS` in 17.31 seconds |
| Build wrapper behavior | Runs `./scripts/pio-local.sh run -e glyph_mk6`; no upload command |

Note: `builder_scripts/arduino_pico.py` embeds the current Git short commit hash and appends `-DIRTY` when the worktree is dirty. Therefore firmware bytes and hashes are commit/dirty-state sensitive even when only docs/tooling changed. The artifact inspected here was produced from the clean source state above before this documentation and parser were added.

## Read-Only Tooling

This batch added `tools/uf2/inspect_uf2.py`, a Python 3 standard-library-only local UF2 parser. It reads local UF2 paths and prints JSON metadata. It does not write files, copy firmware, call upload tools, access mounted device paths, or flash hardware.

Usage used for this inspection:

```bash
python3 tools/uf2/inspect_uf2.py \
  docs/sources/raw/glyph_firmware_uf2/1.0.7/GlyphFirmware-1.0.7.uf2 \
  docs/sources/raw/glyph_firmware_uf2/1.0.7/GlyphFirmware-1.0.7-Clean.uf2 \
  .pio/build/glyph_mk6/firmware.uf2
```

## Artifact Inventory

`find .pio -maxdepth 6 -type f | sort` was run after the clean inspection build. Candidate firmware artifacts found under `.pio/build/glyph_mk6` were:

| Path | Extension | Size bytes | SHA-256 | File type | Candidate role |
| --- | ---: | ---: | --- | --- | --- |
| `.pio/build/glyph_mk6/firmware.uf2` | `.uf2` | 783,872 | `a695246217928cf6b7834e669a59bd8c38647cbaab09ba75d14686ecc4e6cba3` | UF2 firmware image, family Raspberry Pi RP2040, address `0x10000000`, 1,531 total blocks | Clean inspection generated UF2 candidate |
| `.pio/build/glyph_mk6/firmware.bin` | `.bin` | 391,864 | `51f4e659d1970994707dbc28ac98d7b542b81384221c61c597b8e27f1571cbd2` | data | Clean inspection generated binary side artifact |
| `.pio/build/glyph_mk6/firmware.elf` | `.elf` | 5,405,012 | `f0fcd8e2ecf7ff3e1862795ad4ce8e86f625a5dc6234f52ff3774b927f14c823` | ELF 32-bit LSB executable, ARM, EABI5, statically linked, with debug_info, not stripped | Clean inspection generated ELF side artifact |
| `.pio/build/glyph_mk6/firmware 2.bin` | `.bin` | 390,720 | `1f768f8be1eee53d5563c075a3dde95af1cd895cd59f2e61eee6f1d86f54bdd6` | data | Stale prior local build artifact; not the current UF2 candidate |
| `.pio/build/glyph_mk6/firmware 2.elf` | `.elf` | 5,404,796 | `1ad6ce697bb5a263f8ff5a36f8a7da4f6dbc6266b5063b53cefedae76006a52f` | ELF 32-bit LSB executable, ARM, EABI5, statically linked, with debug_info, not stripped | Stale prior local build artifact |
| `.pio/build/glyph_mk6/firmware 3.bin` | `.bin` | 391,872 | `464b1f4a240ee1a44b0fe1e0e587778c840b775d091912967054b9f1bc8f3fb8` | data | Stale prior local build artifact |
| `.pio/build/glyph_mk6/firmware 3.elf` | `.elf` | 5,405,012 | `0384d241bfb49c5a31d5d5c51c798a87b55590b3d26900818dc53f89b8e02944` | ELF 32-bit LSB executable, ARM, EABI5, statically linked, with debug_info, not stripped | Stale prior local build artifact |
| `.pio/build/glyph_mk6/firmware 4.bin` | `.bin` | 391,872 | `7fd9cf6438f22d8a99bf7d18e49b107ca3654c34b661820a15a1e455de8d2f5f` | data | Stale prior local build artifact |
| `.pio/build/glyph_mk6/firmware 4.elf` | `.elf` | 5,405,012 | `8d35f6cf4a4e936d9934a7642407b31f82221a3d6a5a0076bf3b0f5e704523a8` | ELF 32-bit LSB executable, ARM, EABI5, statically linked, with debug_info, not stripped | Stale prior local build artifact |
| `.pio/build/glyph_mk6/firmware 5.bin` | `.bin` | 391,872 | `5952a79b32cf87a5a4df7f93042a7b2a6c867fe966f7bc295ef75836ff97eff4` | data | Stale prior local build artifact |
| `.pio/build/glyph_mk6/firmware 5.elf` | `.elf` | 5,405,012 | `db8e871c95ddeeac075366822e70c3868bc646a50f7abe804f8ff7fed480c8e9` | ELF 32-bit LSB executable, ARM, EABI5, statically linked, with debug_info, not stripped | Stale prior local build artifact |

No `.hex` or `.map` firmware artifacts were found by `find .pio -maxdepth 6 -type f -name '*.hex'` or `find .pio -maxdepth 6 -type f -name '*.map'`.

Generated artifacts were not added to Git.

Verification later reran `./scripts/build-glyph-mk6-quiet.sh` while docs/tool changes were uncommitted. That dirty verification rebuild overwrote `.pio/build/glyph_mk6/firmware.uf2` with whole-file SHA-256 `fa9dcb1ede84ec1f91c3861ee6397b1317a8c07e37088879e78c342d9664ef75` and segment SHA-256 `1221d58cfaacc3778fbc5f44ca9b3118ea707e1de44c8cbce9cbc66f6fa9db3e`; the parsed range remained `0x10000000..0x1005fb00`, with no Clean-only high-flash overlap.

## UF2 Analysis

Ranges are half-open: start inclusive, end exclusive.

| Artifact | Magic valid | Blocks | Declared block count values | Family ID(s) | Target range(s) | Total payload bytes | Segment payload SHA-256 | Any all-zero segment | Classification |
| --- | ---: | ---: | --- | --- | --- | ---: | --- | ---: | --- |
| Official Update `GlyphFirmware-1.0.7.uf2` | Yes | 1,503 | `1503` | `0xe48bff56` | `0x10000000..0x1005df00` | 384,768 | `207a0073251e87aaa70490acfc2812e10fe1c724dd76e7a816c205c1e29e79f8` | No | Official Update app-only reference |
| Official Clean `GlyphFirmware-1.0.7-Clean.uf2` | Yes | 3,551 | `3551` | `0xe48bff56` | `0x10000000..0x1005df00`; `0x1017f000..0x101ff000` | 909,056 | App: `207a0073251e87aaa70490acfc2812e10fe1c724dd76e7a816c205c1e29e79f8`; zero segment: `07854d2fef297a06ba81685e660c332de36d5d18d546927d30daad6d7fda1541` | Yes | Official Clean/Fresh Install reference |
| Generated `.pio/build/glyph_mk6/firmware.uf2` | Yes | 1,531 | `1531` | `0xe48bff56` | `0x10000000..0x1005fb00` | 391,936 | `0b0b384063f280c9da78a163718d060ce96a292418870fa62752b7f7ce81459a` | No | `UPDATE_STYLE_APP_ONLY_CANDIDATE` |

The generated UF2 has no duplicate or missing block numbers according to the read-only parser.

## Official-Vs-Generated Range Comparison

| Check | Result | Evidence |
| --- | --- | --- |
| Official Update app range | Reference range is `0x10000000..0x1005df00` | Archived official Update UF2 read-only parse |
| Official Clean-only high-flash zero range | Reference range is `0x1017f000..0x101ff000` | Archived official Clean UF2 read-only parse |
| Generated UF2 overlaps official Update app range | Yes | Generated range starts at `0x10000000` and extends through the official app range |
| Generated UF2 extends beyond exact official Update end | Yes, by `0x1c00` / 7,168 bytes | Generated end `0x1005fb00`; official Update end `0x1005df00` |
| Generated UF2 overlaps Clean-only high-flash range | No | Generated end `0x1005fb00`, below `0x1017f000` |
| Generated UF2 writes outside local app-like range | No | Local generated app/sketch window is documented in `G12N` as `0x10000000..0x1017f000`; generated end is below that |
| Generated UF2 contains all-zero segment | No | Its single parsed segment is not all zero |

## Conclusion

The generated current UF2 candidate is classified as:

```text
UPDATE_STYLE_APP_ONLY_CANDIDATE
```

It is suitable for further human review because it is a valid RP2040-family UF2, contains one app-like segment, does not overlap the official Clean/Fresh Install high-flash zero segment, and does not write outside the documented local app/sketch window.

It is not approval to flash. More evidence remains needed before any hardware action, including recovery/update-mode verification and explicit human approval for any future spare-device protocol.
