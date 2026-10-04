# GP-VAL-041 USB-name current acceptance proof

This H1 package preserves original GP-CONFIG-019 candidate `fe84db39f2fcdd369d0ae26c1cbb80fd5a15d15d`, direct base `d2f78cd3a3fa38c60d04dab54236ee630ead379e` and tree `240ce04d0fc6c47d4ceb005c2e9dd6b9485a89ac`. The immutable five-path raw inventory SHA-256 is `c6e56845b9c63577c46a11db1660aa5881160ea6022c324e7fac62b14971a711`.

The named checker runs two fresh routes. Historical proof extracts only authenticated original Git objects, keeps all 32 source and 12 fragment pins, reproduces the original 18 observations and runs the original 160 identity negatives. Governance execution works with the four original fixture/report/main/stub paths absent; when present, their live bytes must equal original C019. The historical checker remains immutable at C019; the current checker is a separately authenticated overlay.

Current proof authenticates 34 inputs against accepted F020 `7db4f447d5e796367071b7143fa6c9274c70ae5e`, executes the unchanged original harness with the exact current acceptance fragment and links the real validator and pinned production decoder. Current input identity is checked at execution; earlier external PASS is not reused. The source-free preparation base is `c1a9f0fb9e1d3461d813b31d1643344e3e34d223`.

31 of 32 historical whole-file pins and 11 of 12 body pins remain equal. Removing only the accepted validator include and six-line rejection guard reproduces the exact historical ConfiguratorBackend bytes and acceptance fragment. Historical acceptance SHA-256 stays `400290a51fb4740cec889bd7c5eecf719a5e80c8145da3589dd5a66a9d991746`; current acceptance is separately pinned as `b7c17505e097612fb4b718fc385a0525b3713dc5e4187955364a58c5b8b8547a`.

## Observations and current controls

All original 18 expected rows, all 12 historical fragment identities and the five immutable host identities are recorded in [the fixture](fixtures/gp_val041_usb_name_current_acceptance.json). The 20 added cases are duplicate/empty names × mode/backend activation binding × raw 1/60/0/61/255. All eight valid cases preserve names and return CMD_SUCCESS with one save and live publication. All twelve invalid cases first reach the real decoder, preserve the supplied binding representation, fail the real validator, return CMD_ERROR with zero saves and preserve both live Config and saved stub bytes exactly. Original SAVE/LOAD stubs retain their declared host boundary; no physical storage acceptance is implied.

The checker requires exact output for all 18 original observations and all 20 controls, uses `-fshort-enums` with a one-byte Button assertion, and runs ASan/UBSan with nonrecovering errors and empty sanitizer stderr. It compiles and executes freshly on every invocation. Results are printed separately as historical and current; any missing or false result fails. The optional external JSON report records actual rows, commands, input identities and sanitizer output from that invocation.

## Exact current input inventory

Every entry is regular mode100644. The fixture records the corresponding Git blobs separately. The first 32 entries retain the original historical inventory; the final two add the accepted validator header and body.

| Path | Current SHA-256 |
| --- | --- |
| `HAL/pico/src/display/DefaultConfigMenu.cpp` | `279b44fb4e55f73178591908f843f51a086c4e1c3c26d537aac18a26eae95b20` |
| `HAL/pico/include/display/DefaultConfigMenu.hpp` | `94c6404c37fa6de41563ba06fe839a169b2281d990d8bde36d61c6f29238fa7f` |
| `HAL/pico/src/display/ConfigMenu.cpp` | `5772d5accd688ffe176d968146c02c17682512c9551348438d6a7a76e94a57be` |
| `HAL/pico/include/display/ConfigMenu.hpp` | `16c4c1da62c3b0309a51779780727d1191b6c7bb4bff1a6b1bde2c69c68a8088` |
| `config/glyph/common/src/display/GlyphConfigMenu.cpp` | `4ef795f0d34a745cf2d96f52be2493808452e2998a371ee5a96747a08207fcf0` |
| `config/glyph/common/include/display/GlyphConfigMenu.hpp` | `428ad8033d9a03adbf51526a7cb494287da0525e6c493f83f8c19d8d366f64d7` |
| `config/glyph/common/include/glyph_overrides.hpp` | `ab4074ed3cd6988abadaf9a79343be8fdd9751c3fb24ebc2d25f3111857cae1d` |
| `config/glyph/common/src/config.cpp` | `bde443c7eceb417494ae71191a2076c0ab251e987706f30a757b14aaf16ad0e5` |
| `HAL/pico/src/core/Persistence.cpp` | `941cc54f0fb762e6067db338601325d33cf7f980148a59caa1d61f226e140955` |
| `HAL/pico/include/core/Persistence.hpp` | `56d8c3281b54a6d8168a7e8d04d31c0c2b20d1c2223b21b77a9a1549460a669d` |
| `HAL/pico/src/comms/ConfiguratorBackend.cpp` | `68bc7756eacb63c6831709c803349d52206ed7a271dc49b0cd33d6c53f0c3c38` |
| `HAL/pico/src/comms/backend_init.cpp` | `8cbd355e6323a775ab88aacef2ca07d2cad88232790f9d8b8d3f2f686875e2ea` |
| `HAL/pico/include/comms/backend_init.hpp` | `3c2e4b29d06e85e17ba0f63ac7160589ec0b5661874406a9e3a576446b2cf227` |
| `HAL/pico/src/reboot.cpp` | `f89b9199f55e8f116901ca49484f7ef6c3fe51c048dc31a98934d08bf0a5627e` |
| `include/reboot.hpp` | `bcc6237cd7c3b85e263cdfd2f265aaf257537a75fc6518acb4edf5f0ab14ef6d` |
| `src/core/mode_selection.cpp` | `8df6ddf1ca626f7d840e68ea700654bcbc30f6473fe7383abc4bf6e99fc4fd44` |
| `src/core/config_utils.cpp` | `b97af928bff72103f90b0155e4e63fd44a3cfcb84e46ac93cf74f6f3227e02ab` |
| `HAL/pico/include/util/state_util.hpp` | `db4b4ee7dcfe462dd00097a5109e028787e11d7868b012f447c9fee84e68ea81` |
| `platformio.ini` | `99fc26f84f4cf2c118d08fde7269a13b9b37f6ed1efb2d32291ba9f0b8e780e9` |
| `config/glyph/env.ini` | `c754c2f504c8740763d3f65fa114cc61c21fe5d73bd489c728610c1299d1fccf` |
| `builder_scripts/arduino_pico.py` | `676b20e42500cb0b5f671892250a2c063e21a31459ed542ad48a9481a7fce0af` |
| `docs/runtime_config/fixtures/gp_prov_014_decoder_closure.json` | `a0f017c36ce0354f91d1a62210756c0464c6db9b5183ba6592ce69d32da1e13f` |
| `tools/fixtures/gp_config012_button_host/schema/config.proto` | `2844d8fc8c78c9fbed00a6954a13d9826f4634cac152f8a9a707666f47bb893b` |
| `tools/fixtures/gp_config012_button_host/schema/config.options` | `6a53dc93a79027669a3990c3a785e386e02e063c1f3438744aac49c3ad074805` |
| `tools/fixtures/gp_config012_button_host/generated/config.pb.h` | `bdd72a220126911d7f6d2558ec5517be96189af92242979e3af43d1076550323` |
| `tools/fixtures/gp_config012_button_host/generated/config.pb.c` | `d7041bfaf221cc747c7f2dc3fa8586352a1b8dc363fbdcfca181774562941626` |
| `tools/fixtures/gp_config012_button_host/nanopb/pb.h` | `e0db84a27e0d41a2d2d347b8c879e30ceb856d36dc192cce0f1124f833c67bc2` |
| `tools/fixtures/gp_config012_button_host/nanopb/pb_decode.h` | `fcac5f7680fe6e870157e4bcf34d5162bdd4fff0d7db3cad1122f2ad24a6da87` |
| `tools/fixtures/gp_config012_button_host/nanopb/pb_decode.c` | `f5b425beaa207251e531c8ce2c86c9b6867e2920ed59cc1b125332af0c147632` |
| `tools/fixtures/gp_config012_button_host/nanopb/pb_common.h` | `6495a691aca68d6973f2274b5dd54b74fbb57f6b019c45fff255a857fe1abcfd` |
| `tools/fixtures/gp_config012_button_host/nanopb/pb_common.c` | `8d2ec28baaaf2b7a5e90e4cb2fa9700d21cef7f826f051a637c30b7a1e6a0516` |
| `tools/fixtures/gp_config012_button_host/LICENSE.nanopb.txt` | `e2f2fc8fe3faa7dcb09dbe995db48c6ec5c1f72705db915101e4a83fed44f66d` |
| `include/core/config_button_validation.hpp` | `176cec58249c48e51d418af0af9f64b4d6b8942d4c53c6a8b6f519dcc9c3193f` |
| `src/core/config_button_validation.cpp` | `4025f581961e63a8ef6a290b41786b59291bada5e77ab665dbe448ed27418d2d` |

## Execution and boundaries

Run `python3 tools/check_glyph_gp_config019_usb_name_selection.py` for both routes. `--route historical` and `--route current` select explicit diagnostic routes; coupled validation must run both. `--report /absolute/external/path.json` preserves actual invocation evidence outside the repository. No network, firmware build, source mutation, Config/device write or cached PASS is used.

The finite adopted GP-VAL-041 contract and its receipt authorize this package. Their catalogue separately pins the edited checker, this report, the fixture and current harness. Full correspondence checks committed overlays and current/live/index identity; this focused checker does not replace those gates. Required parent regressions, fresh independent review, source-free integration and separate strict GP-VAL-041 DONE remain distinct. Only then may the preserved GP-CONFIG-019 candidate resume integration.

No naming uniqueness, first-match repair, fallback, Keyboard policy, public release or controller acceptance is selected. Original fingerprint MISMATCH/UNKNOWN remains historical. Hardware acceptance NOT_CLAIMED; Nunchuk NOT_TESTED; root cause UNPROVEN. The accepted C020 source and frozen pending C014 identities remain unchanged.
