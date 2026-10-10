"""Exact GP-VAL-034 C014 proof. Candidate validation never implies hardware PASS."""
from __future__ import annotations
import ast
import hashlib
import json
import re
import stat
from pathlib import Path
import glyph_campaign_transition as original
import glyph_c020_abi_repair_transition as predecessor
from glyph_hardware_correspondence import CorrespondenceError, classify_path, verify_correspondence
from glyph_tracked_worktree_integrity import IGNORED_ALLOWED_ROOTS

C = 'a3664be5354ec4253122eb2e738e70e5dfdb9ccc'
B = '8b8e45b17a5670bbf983360faf87bdf9d6b50ce2'
TREE = '287732689ce5ef069db72148a78926f4f5376ea0'
HANDOFF = '5205ba518d1d5fa19e7584d6c6d5210932091b3e'
READY = '7911692afed3e68becefd8e3c90413d4e230ea82'
MAPPING = 'docs/runtime_config/fixtures/gp_val034_c014_transition.json'
TRANSITIONS = 'docs/runtime_config/fixtures/gp_val034_accepted_transitions.json'
MAPPING_SHA256 = 'b391107e4ae7d69f716b6ed1f37857af9fba522508638badb42e4710a427b847'
RAW = 'c40d8aadf736832b52a746455d940b29296522c281f49b3ab314e3d22c1d11aa'
QUEUE = original.QUEUE
PROTOCOL = 'docs/agent_framework/GP_CONFIG_014_HARDWARE_PROTOCOL.md'
EVIDENCE = 'docs/calibration/fixtures/gp_config_014_hardware_evidence.json'
RESULT = 'docs/calibration/gp_config_014_hardware_result.md'
CRITICAL = frozenset(('include/modes/CustomControllerMode.hpp', 'src/modes/CustomControllerMode.cpp'))
HOSTS = frozenset(('tools/check_glyph_gp_config014_modifier_capacity.py',
 'tools/fixtures/gp_config014_modifier_capacity/modifier_capacity_harness.cpp',
 'docs/runtime_config/gp_config014_modifier_capacity.md',
 'docs/runtime_config/fixtures/gp_config014_modifier_capacity.json'))
HOST_OVERLAYS = frozenset(('tools/check_glyph_custom_modifier_cache_characterization.py',
 'tools/check_glyph_gp_config012_button_mask_characterization.py',
 'tools/check_glyph_setconfig_runtime_rebinding_characterization.py',
 'tools/check_glyph_gp_config014_modifier_capacity.py'))
HOST_OVERLAY_BLOBS = {'tools/check_glyph_custom_modifier_cache_characterization.py': {'blob': 'd5d71dc0ab97a525585cb0b2f21296c81ea1a5a2', 'sha256': 'fcc0a671a6ac5a1262f125567e84f2ffe0c56ee12c9533ad994ebd0b45701935', 'mode': '100644'}, 'tools/check_glyph_gp_config012_button_mask_characterization.py': {'blob': 'bc03ec9b0beac7c96876022d37673746052ab4d8', 'sha256': 'f515c1c806494acaf60d38dc2d92aaef10e1d292998abe322161fda6ea0cfcd1', 'mode': '100644'}, 'tools/check_glyph_setconfig_runtime_rebinding_characterization.py': {'blob': '4d5fbc036c1d68105d86a2cdf09002b63a388271', 'sha256': '54e93cb3a9c4d757eb2517772ddf86b44d03c6f55bfc1c032eede30381a6a437', 'mode': '100644'}, 'tools/check_glyph_gp_config014_modifier_capacity.py': {'blob': '7e91f2c1415b6de55766d8cf6c694a93ed36a50d', 'sha256': 'b9296f5b33d73e7946e415645535e07ad364b5211803dfecfef2a6e764f85c46', 'mode': '100644'}}

# Existing immutable KBD characterization: exact H1 coexistence only. No019
# future inventory or source-route hash refresh is authorized by these pins.
KBD_C = '4fb7c1e9507547774ff9f55cd7788355648d5d1e'
KBD_B = '328c6a1bfb09eb035c2065d0de080283307f34d6'
KBD_AUTHORITY = 'd9ad6132ca0912398839673cc0da24e54a924210'
KBD_TREE = 'a847f1dab9e7918ec49d5dd887b009adf087c87f'
KBD_RAW = 'f8cc5721ad63f142d535aae73087c9466d1891e3010ea241fd03688aa81f6ad5'
KBD_HOST_PINS = {'docs/calibration/fixtures/gp_kbd_001_keyboard_pipeline_characterization.json': {'mode': '100644', 'blob': 'ea61079fcbb3962b1da9c301de7c3d3867ee4db3', 'sha256': 'ce03196f7fd8f2c779b5ac8a563b9f6f0017dbf4a5bc4e80e99bce01b3a0f455'}, 'docs/calibration/gp_kbd_001_keyboard_pipeline_characterization.md': {'mode': '100644', 'blob': '66592c2bb5a9c4860d4a72accdab52e72080b8fc', 'sha256': 'cec227bda66d072c756686b40100fef19fc768bdcb5038040dced1ea720a4d0d'}, 'tools/check_glyph_gp_kbd_001_keyboard_pipeline.py': {'mode': '100644', 'blob': 'fad8c930329b3317ddf7c07bfec725ac1a7f457f', 'sha256': 'c15ccd4ddc7ae3a88913934afb574fbf647777dd53ceb6060695b938dafacdc8'}, 'tools/fixtures/gp_kbd_001_keyboard_pipeline/include/TUKeyboard.hpp': {'mode': '100644', 'blob': '4bd11a0168f8f0f2308aefd6f7b2942156c9ba9c', 'sha256': '6c6701107f94b540a3819de3f5207f37b7bb5f26cb95ebcb92381f1056c1b0b7'}, 'tools/fixtures/gp_kbd_001_keyboard_pipeline/main.cpp': {'mode': '100644', 'blob': 'd9bbaf7cccd5b35f65b6bd8b0462d78c9bf4fd63', 'sha256': 'c3423bb79fec9dc1b5a221e74e44ce04488fb7aceff86360e2aa4f302f36e9cf'}}
KBD_DEPENDENCY_PINS = {'HAL/pico/src/core/KeyboardMode.cpp': {'mode': '100644', 'blob': 'a14f01d030dad62305fc0accdc07d224c61eefcf', 'sha256': 'a4396ef241cde82c7296ee01aad6b7907e6c7579aa4349c5366621c73c59791d'}, 'src/modes/CustomKeyboardMode.cpp': {'mode': '100644', 'blob': '60c7c69ad77e6c3acf931fdd3ccf1d448701c7f8', 'sha256': '90db32b605383adda19c9f00ad69daf538a766d801415483915ea8d6429a9def'}, 'src/core/InputMode.cpp': {'mode': '100644', 'blob': 'f1388a1948fc73f7525463db219a53f5af1e6b7b', 'sha256': '080bcc65bb83b1b896a2b4efa6ea9e9d304071ee30f279fe3386ff2c29cc85c7'}, 'src/core/socd.cpp': {'mode': '100644', 'blob': '81a0d53fae96305c07d5943f4785b33b02ca1949', 'sha256': '5a2bb8e776873d149559e914b07cc4224853e3e3593a46760c38d23ff4d38bb3'}, 'HAL/pico/include/core/KeyboardMode.hpp': {'mode': '100644', 'blob': '81ad10d78f86da84fd8b1e51fb3857a463014f1e', 'sha256': '6bc35650a119ec942e26015dcb36361ffb284e0f8221134ccd5776ebdfb7a7b5'}, 'include/modes/CustomKeyboardMode.hpp': {'mode': '100644', 'blob': '79a2725ca7703dfdabbd1c186d197e2250122c86', 'sha256': 'c907de266f4ebeea8518511cf725c57bf52c85c0c9827f25cc2a7d20381f9464'}, 'include/core/InputMode.hpp': {'mode': '100644', 'blob': '02f3cfd54c47cf2b8f4587a2d519d0682240eec4', 'sha256': 'dc382c38eb2c30cf7f94727670ae5530a682daf6555db65ea5d5b5f0dc2f23ee'}, 'include/core/socd.hpp': {'mode': '100644', 'blob': '5d912b274ba54fde5e07a575cf9bec84da07c9bb', 'sha256': '88ff9be552e89f0c92a1548662fc4bf9b6fd4408b242f6f42bec8ecf70e6fc91'}, 'include/core/state.hpp': {'mode': '100644', 'blob': 'ff3aa94df61fd6a41448799fa1d6f508c41ecd0f', 'sha256': 'c46eb5347843ac4574dcffb28faeace608f029c27b94690c02ce06981cc4e6a3'}, 'HAL/pico/include/util/state_util.hpp': {'mode': '100644', 'blob': '40b8aeb9c4db3268696c49f20b3278efabc7688c', 'sha256': 'db4b4ee7dcfe462dd00097a5109e028787e11d7868b012f447c9fee84e68ea81'}, 'HAL/pico/include/stdlib.hpp': {'mode': '100644', 'blob': '6bc7bc5ee7f56de07116608399af228314dab004', 'sha256': '676ecc6f5a9b333bf2c55a9df11ddf037a83fe217788c17f887fae4851ea90bc'}, 'config/glyph/common/include/glyph_overrides.hpp': {'mode': '100644', 'blob': '90cc393759e91c8acacd6edef9ecb05b86d7fdc8', 'sha256': 'ab4074ed3cd6988abadaf9a79343be8fdd9751c3fb24ebc2d25f3111857cae1d'}, 'config/glyph/common/src/display/GlyphConfigMenu.cpp': {'mode': '100644', 'blob': '819549dfdf2de34d5ceebed58fa30d278da4f4cb', 'sha256': '4ef795f0d34a745cf2d96f52be2493808452e2998a371ee5a96747a08207fcf0'}, 'HAL/pico/src/display/DefaultConfigMenu.cpp': {'mode': '100644', 'blob': 'bf855a584b3e859083d98a1aa49a38daee9204f5', 'sha256': '279b44fb4e55f73178591908f843f51a086c4e1c3c26d537aac18a26eae95b20'}, 'HAL/pico/src/comms/backend_init.cpp': {'mode': '100644', 'blob': 'f7726a0063dd05409d7464d947a47efc675bdbef', 'sha256': '8cbd355e6323a775ab88aacef2ca07d2cad88232790f9d8b8d3f2f686875e2ea'}, 'src/core/mode_selection.cpp': {'mode': '100644', 'blob': '7d659d3133271c2ed956a16d8f5e3eda73040f81', 'sha256': '8df6ddf1ca626f7d840e68ea700654bcbc30f6473fe7383abc4bf6e99fc4fd44'}, 'config/glyph/common/src/config.cpp': {'mode': '100644', 'blob': '701e4ac8c0a635b77ef4282f29109f7bb0bea726', 'sha256': 'bde443c7eceb417494ae71191a2076c0ab251e987706f30a757b14aaf16ad0e5'}, 'platformio.ini': {'mode': '100644', 'blob': '4d56f8630c1b12e84cd12f40ce05a4dc71b9362e', 'sha256': '99fc26f84f4cf2c118d08fde7269a13b9b37f6ed1efb2d32291ba9f0b8e780e9'}, 'config/glyph/env.ini': {'mode': '100644', 'blob': 'fac4e20461ad632ca1d65826241a4a9c73630f04', 'sha256': 'c754c2f504c8740763d3f65fa114cc61c21fe5d73bd489c728610c1299d1fccf'}, 'builder_scripts/arduino_pico.py': {'mode': '100644', 'blob': '35381a91ad5aa4ffdbcd362365c1bf9fbd13136e', 'sha256': '676b20e42500cb0b5f671892250a2c063e21a31459ed542ad48a9481a7fce0af'}, 'tools/glyph_tracked_worktree_integrity.py': {'mode': '100644', 'blob': 'f653b4619ee0ce8a8c35d972fa591545522c0be7', 'sha256': '604bea90c4b3cb2cbb0fdf023918da7ba45d1be7d128c2b40050e09e5a220fc7'}, 'tools/fixtures/gp_config012_button_host/generated/config.pb.h': {'mode': '100644', 'blob': '01d0dda2ae768dd0f18c0f338a74c55e613bb199', 'sha256': 'bdd72a220126911d7f6d2558ec5517be96189af92242979e3af43d1076550323'}, 'tools/fixtures/gp_config012_button_host/nanopb/pb.h': {'mode': '100644', 'blob': '3f181d873a81d82c27c56874f6a63328f38eaaf3', 'sha256': 'e0db84a27e0d41a2d2d347b8c879e30ceb856d36dc192cce0f1124f833c67bc2'}, 'tools/fixtures/gp_config012_button_host/schema/config.proto': {'mode': '100644', 'blob': 'a58a2bf4dd827ad92482f1ac30c3d56bbea93c05', 'sha256': '2844d8fc8c78c9fbed00a6954a13d9826f4634cac152f8a9a707666f47bb893b'}, 'tools/fixtures/gp_config012_button_host/schema/config.options': {'mode': '100644', 'blob': '7175d8463ade5b0cd45f1a5f8f99be44f5719c3c', 'sha256': '6a53dc93a79027669a3990c3a785e386e02e063c1f3438744aac49c3ad074805'}, 'tools/fixtures/gp_config012_button_host/include/Arduino.h': {'mode': '100644', 'blob': '7a3d1de2a3400cb7ee45750c25491e9b434f2608', 'sha256': '70de967f79f47db90cb5864847e129e4d6c322dcfa08338cd31ddf601354dc20'}, 'tools/fixtures/gp_config012_button_host/include/pico/stdlib.h': {'mode': '100644', 'blob': '9bf1084ddd04162e6b0fe39f56f52b6d46cbd1c9', 'sha256': '0990f6f853b296816a654c1a4d4ccd8593bc819a1d591af8f01ab238926c41d4'}, 'docs/runtime_config/fixtures/gp_prov_014_decoder_closure.json': {'mode': '100644', 'blob': '25d32a1fc1cc9c39626eadd4dca4835103579d80', 'sha256': 'a0f017c36ce0354f91d1a62210756c0464c6db9b5183ba6592ce69d32da1e13f'}}
KBD_HOSTS = frozenset(KBD_HOST_PINS)

# GP-VAL-041: immutable019 evidence and independently pinned current proof.
CONFIG019_C = 'fe84db39f2fcdd369d0ae26c1cbb80fd5a15d15d'
CONFIG019_B = 'd2f78cd3a3fa38c60d04dab54236ee630ead379e'
CONFIG019_TREE = '240ce04d0fc6c47d4ceb005c2e9dd6b9485a89ac'
CONFIG019_RAW = 'c6e56845b9c63577c46a11db1660aa5881160ea6022c324e7fac62b14971a711'
CONFIG019_F020 = '7db4f447d5e796367071b7143fa6c9274c70ae5e'
CONFIG019_OPENING = '12cad41ee8157010c512e4772ff62ffdb68771e6'
CONFIG019_RECEIPT_COMMIT = '6eb288e61a0d148530474eef12bd0aa3243e8526'
CONFIG019_RECEIPT_PARENT = 'b55ee1301733700b7187bd650ec33f09ca3db1c8'
CONFIG019_ADOPTION = 'c1a9f0fb9e1d3461d813b31d1643344e3e34d223'
CONFIG019_ADOPTION_QUEUE_SHA256 = 'b7a7b8970325e3d2f575bfb835fd2f8fc4b00cb740e8ff69e099cf19237949c0'
CONFIG019_RECEIPT = 'docs/agent_framework/curation_receipts/gp_val041_finite_scope_20261004.json'
CONFIG019_CONTRACT = 'docs/agent_framework/GP_VAL_041_FINITE_SCOPE_CURATOR_20261004.md'
CONFIG019_AUTHORITY_PINS = {'docs/agent_framework/curation_receipts/gp_val041_finite_scope_20261004.json': {'mode': '100644',
                                                                                 'blob': 'fd661816a95aa8d0022c886bfb5b5208b99d4437',
                                                                                 'sha256': 'bc146ec462843c96c90c77c48ae448d60638564b1ca33f2a9225aebbd952aa87'},
 'docs/agent_framework/GP_VAL_041_FINITE_SCOPE_CURATOR_20261004.md': {'mode': '100644',
                                                                      'blob': '4e2e7c1f31a88d1b8ffa91b0fbb8d083cab90941',
                                                                      'sha256': 'd6077678174b6e253fdc0fc2d283f5ed767e21ba761b51cd97a56617c80caac1'}}
CONFIG019_CHECKER = 'tools/check_glyph_gp_config019_usb_name_selection.py'
CONFIG019_HOST_PINS = {'docs/calibration/fixtures/gp_config_019_usb_name_selection_characterization.json': {'mode': '100644',
                                                                                      'blob': 'de08edbad80d33f053f5af8ffd61c0781f181812',
                                                                                      'sha256': 'a605e894a1568325abb823fd089ee7fb659b78b301a272e60d137161b206500a'},
 'docs/calibration/gp_config_019_usb_name_selection_characterization.md': {'mode': '100644',
                                                                           'blob': 'eae7a289aacc8c0d9ea9455ec0ce812d7f7a7c63',
                                                                           'sha256': 'e5315cb7f26792050ed72d41511103bdc1b00b1ae3abc52faec562688e3f5e5d'},
 'tools/check_glyph_gp_config019_usb_name_selection.py': {'mode': '100644',
                                                          'blob': '103a7cd22b96a3f806a88771d9b54cc20105999d',
                                                          'sha256': 'f21ec0eecfd4601e91ba5d6b5370f6798952f9d2a3f781bd5b1c3a55a917e540'},
 'tools/fixtures/gp_config019_usb_name_selection/include/host_stubs.hpp': {'mode': '100644',
                                                                           'blob': 'ffccc37ce24592e783646b17fdd3339c5e368128',
                                                                           'sha256': '019087c96be2f61b20827771375f656f5e2811e694293cbab6e2592055560ce1'},
 'tools/fixtures/gp_config019_usb_name_selection/main.cpp': {'mode': '100644',
                                                             'blob': '1f91f2ad54bd7148c5089d0f4c9d211b9e0978e6',
                                                             'sha256': 'aedd1cf767dc370451028a8bfc3a0f17e6859cc6c7cb79384874b67da1969d65'}}
CONFIG019_DEPENDENCY_PINS = {'HAL/pico/src/display/DefaultConfigMenu.cpp': {'mode': '100644',
                                                'blob': 'bf855a584b3e859083d98a1aa49a38daee9204f5',
                                                'sha256': '279b44fb4e55f73178591908f843f51a086c4e1c3c26d537aac18a26eae95b20'},
 'HAL/pico/include/display/DefaultConfigMenu.hpp': {'mode': '100644',
                                                    'blob': '49a6e62839320ea96f6d8a954af5828d75dc6287',
                                                    'sha256': '94c6404c37fa6de41563ba06fe839a169b2281d990d8bde36d61c6f29238fa7f'},
 'HAL/pico/src/display/ConfigMenu.cpp': {'mode': '100644',
                                         'blob': 'f1a5f978fadd90fdffd7af19966444fd0748936b',
                                         'sha256': '5772d5accd688ffe176d968146c02c17682512c9551348438d6a7a76e94a57be'},
 'HAL/pico/include/display/ConfigMenu.hpp': {'mode': '100644',
                                             'blob': 'b896fa08480d15fbb4b35e345de6cb66555bddff',
                                             'sha256': '16c4c1da62c3b0309a51779780727d1191b6c7bb4bff1a6b1bde2c69c68a8088'},
 'config/glyph/common/src/display/GlyphConfigMenu.cpp': {'mode': '100644',
                                                         'blob': '819549dfdf2de34d5ceebed58fa30d278da4f4cb',
                                                         'sha256': '4ef795f0d34a745cf2d96f52be2493808452e2998a371ee5a96747a08207fcf0'},
 'config/glyph/common/include/display/GlyphConfigMenu.hpp': {'mode': '100644',
                                                             'blob': 'ab18e1ba53f3eb4f355784b5d6a0a87f65929249',
                                                             'sha256': '428ad8033d9a03adbf51526a7cb494287da0525e6c493f83f8c19d8d366f64d7'},
 'config/glyph/common/include/glyph_overrides.hpp': {'mode': '100644',
                                                     'blob': '90cc393759e91c8acacd6edef9ecb05b86d7fdc8',
                                                     'sha256': 'ab4074ed3cd6988abadaf9a79343be8fdd9751c3fb24ebc2d25f3111857cae1d'},
 'config/glyph/common/src/config.cpp': {'mode': '100644',
                                        'blob': '701e4ac8c0a635b77ef4282f29109f7bb0bea726',
                                        'sha256': 'bde443c7eceb417494ae71191a2076c0ab251e987706f30a757b14aaf16ad0e5'},
 'HAL/pico/src/core/Persistence.cpp': {'mode': '100644',
                                       'blob': '907e6ca3d84fc414aa67dadfcbf4f60d1e1200a7',
                                       'sha256': '941cc54f0fb762e6067db338601325d33cf7f980148a59caa1d61f226e140955'},
 'HAL/pico/include/core/Persistence.hpp': {'mode': '100644',
                                           'blob': '43cbd3f39b4c9a09ecc855b0f2704b2081a45981',
                                           'sha256': '56d8c3281b54a6d8168a7e8d04d31c0c2b20d1c2223b21b77a9a1549460a669d'},
 'HAL/pico/src/comms/ConfiguratorBackend.cpp': {'mode': '100644',
                                                'blob': '3e934f2f5aae13a36310a35d273727da60723abe',
                                                'sha256': '28ef942416d0ec4b92588304fcf72f219a0c6b1e2a582f20e2dc7e0e07d1b876'},
 'HAL/pico/src/comms/backend_init.cpp': {'mode': '100644',
                                         'blob': 'f7726a0063dd05409d7464d947a47efc675bdbef',
                                         'sha256': '8cbd355e6323a775ab88aacef2ca07d2cad88232790f9d8b8d3f2f686875e2ea'},
 'HAL/pico/include/comms/backend_init.hpp': {'mode': '100644',
                                             'blob': '783cb54e5d01d33e931136e9cbb15f696a510029',
                                             'sha256': '3c2e4b29d06e85e17ba0f63ac7160589ec0b5661874406a9e3a576446b2cf227'},
 'HAL/pico/src/reboot.cpp': {'mode': '100644',
                             'blob': '796c7f4b7337004b6f68a59c9e775e55f4578742',
                             'sha256': 'f89b9199f55e8f116901ca49484f7ef6c3fe51c048dc31a98934d08bf0a5627e'},
 'include/reboot.hpp': {'mode': '100644',
                        'blob': '506e0c5784eaa9d5da632e05504fef4928b20e52',
                        'sha256': 'bcc6237cd7c3b85e263cdfd2f265aaf257537a75fc6518acb4edf5f0ab14ef6d'},
 'src/core/mode_selection.cpp': {'mode': '100644',
                                 'blob': '7d659d3133271c2ed956a16d8f5e3eda73040f81',
                                 'sha256': '8df6ddf1ca626f7d840e68ea700654bcbc30f6473fe7383abc4bf6e99fc4fd44'},
 'src/core/config_utils.cpp': {'mode': '100644',
                               'blob': 'beeb1202f67f61ce717e0e020cb3dd339dfa6206',
                               'sha256': 'b97af928bff72103f90b0155e4e63fd44a3cfcb84e46ac93cf74f6f3227e02ab'},
 'HAL/pico/include/util/state_util.hpp': {'mode': '100644',
                                          'blob': '40b8aeb9c4db3268696c49f20b3278efabc7688c',
                                          'sha256': 'db4b4ee7dcfe462dd00097a5109e028787e11d7868b012f447c9fee84e68ea81'},
 'platformio.ini': {'mode': '100644',
                    'blob': '4d56f8630c1b12e84cd12f40ce05a4dc71b9362e',
                    'sha256': '99fc26f84f4cf2c118d08fde7269a13b9b37f6ed1efb2d32291ba9f0b8e780e9'},
 'config/glyph/env.ini': {'mode': '100644',
                          'blob': 'fac4e20461ad632ca1d65826241a4a9c73630f04',
                          'sha256': 'c754c2f504c8740763d3f65fa114cc61c21fe5d73bd489c728610c1299d1fccf'},
 'builder_scripts/arduino_pico.py': {'mode': '100644',
                                     'blob': '35381a91ad5aa4ffdbcd362365c1bf9fbd13136e',
                                     'sha256': '676b20e42500cb0b5f671892250a2c063e21a31459ed542ad48a9481a7fce0af'},
 'docs/runtime_config/fixtures/gp_prov_014_decoder_closure.json': {'mode': '100644',
                                                                   'blob': '25d32a1fc1cc9c39626eadd4dca4835103579d80',
                                                                   'sha256': 'a0f017c36ce0354f91d1a62210756c0464c6db9b5183ba6592ce69d32da1e13f'},
 'tools/fixtures/gp_config012_button_host/schema/config.proto': {'mode': '100644',
                                                                 'blob': 'a58a2bf4dd827ad92482f1ac30c3d56bbea93c05',
                                                                 'sha256': '2844d8fc8c78c9fbed00a6954a13d9826f4634cac152f8a9a707666f47bb893b'},
 'tools/fixtures/gp_config012_button_host/schema/config.options': {'mode': '100644',
                                                                   'blob': '7175d8463ade5b0cd45f1a5f8f99be44f5719c3c',
                                                                   'sha256': '6a53dc93a79027669a3990c3a785e386e02e063c1f3438744aac49c3ad074805'},
 'tools/fixtures/gp_config012_button_host/generated/config.pb.h': {'mode': '100644',
                                                                   'blob': '01d0dda2ae768dd0f18c0f338a74c55e613bb199',
                                                                   'sha256': 'bdd72a220126911d7f6d2558ec5517be96189af92242979e3af43d1076550323'},
 'tools/fixtures/gp_config012_button_host/generated/config.pb.c': {'mode': '100644',
                                                                   'blob': 'c59855ecb19be7f5193833d94fe41cc1828ffb14',
                                                                   'sha256': 'd7041bfaf221cc747c7f2dc3fa8586352a1b8dc363fbdcfca181774562941626'},
 'tools/fixtures/gp_config012_button_host/nanopb/pb.h': {'mode': '100644',
                                                         'blob': '3f181d873a81d82c27c56874f6a63328f38eaaf3',
                                                         'sha256': 'e0db84a27e0d41a2d2d347b8c879e30ceb856d36dc192cce0f1124f833c67bc2'},
 'tools/fixtures/gp_config012_button_host/nanopb/pb_decode.h': {'mode': '100644',
                                                                'blob': '1ef9d56c6e0b6430f9067cbb911c7e697d034e24',
                                                                'sha256': 'fcac5f7680fe6e870157e4bcf34d5162bdd4fff0d7db3cad1122f2ad24a6da87'},
 'tools/fixtures/gp_config012_button_host/nanopb/pb_decode.c': {'mode': '100644',
                                                                'blob': '0f71c33b1bd99e531c9eacda5f9b012ddb3c8339',
                                                                'sha256': 'f5b425beaa207251e531c8ce2c86c9b6867e2920ed59cc1b125332af0c147632'},
 'tools/fixtures/gp_config012_button_host/nanopb/pb_common.h': {'mode': '100644',
                                                                'blob': '58aa90f76d58596d3f45a120b65b4a0bff7fd688',
                                                                'sha256': '6495a691aca68d6973f2274b5dd54b74fbb57f6b019c45fff255a857fe1abcfd'},
 'tools/fixtures/gp_config012_button_host/nanopb/pb_common.c': {'mode': '100644',
                                                                'blob': '6aee76b1efa1e6f2f3fe7d43629da9b2114eea19',
                                                                'sha256': '8d2ec28baaaf2b7a5e90e4cb2fa9700d21cef7f826f051a637c30b7a1e6a0516'},
 'tools/fixtures/gp_config012_button_host/LICENSE.nanopb.txt': {'mode': '100644',
                                                                'blob': 'd11c9af1d7e469e9a5357a660fd184f58c3a4ff2',
                                                                'sha256': 'e2f2fc8fe3faa7dcb09dbe995db48c6ec5c1f72705db915101e4a83fed44f66d'}}
CONFIG019_CURRENT_SOURCE_PINS = {'HAL/pico/src/display/DefaultConfigMenu.cpp': {'mode': '100644',
                                                'blob': 'bf855a584b3e859083d98a1aa49a38daee9204f5',
                                                'sha256': '279b44fb4e55f73178591908f843f51a086c4e1c3c26d537aac18a26eae95b20'},
 'HAL/pico/include/display/DefaultConfigMenu.hpp': {'mode': '100644',
                                                    'blob': '49a6e62839320ea96f6d8a954af5828d75dc6287',
                                                    'sha256': '94c6404c37fa6de41563ba06fe839a169b2281d990d8bde36d61c6f29238fa7f'},
 'HAL/pico/src/display/ConfigMenu.cpp': {'mode': '100644',
                                         'blob': 'f1a5f978fadd90fdffd7af19966444fd0748936b',
                                         'sha256': '5772d5accd688ffe176d968146c02c17682512c9551348438d6a7a76e94a57be'},
 'HAL/pico/include/display/ConfigMenu.hpp': {'mode': '100644',
                                             'blob': 'b896fa08480d15fbb4b35e345de6cb66555bddff',
                                             'sha256': '16c4c1da62c3b0309a51779780727d1191b6c7bb4bff1a6b1bde2c69c68a8088'},
 'config/glyph/common/src/display/GlyphConfigMenu.cpp': {'mode': '100644',
                                                         'blob': '819549dfdf2de34d5ceebed58fa30d278da4f4cb',
                                                         'sha256': '4ef795f0d34a745cf2d96f52be2493808452e2998a371ee5a96747a08207fcf0'},
 'config/glyph/common/include/display/GlyphConfigMenu.hpp': {'mode': '100644',
                                                             'blob': 'ab18e1ba53f3eb4f355784b5d6a0a87f65929249',
                                                             'sha256': '428ad8033d9a03adbf51526a7cb494287da0525e6c493f83f8c19d8d366f64d7'},
 'config/glyph/common/include/glyph_overrides.hpp': {'mode': '100644',
                                                     'blob': '90cc393759e91c8acacd6edef9ecb05b86d7fdc8',
                                                     'sha256': 'ab4074ed3cd6988abadaf9a79343be8fdd9751c3fb24ebc2d25f3111857cae1d'},
 'config/glyph/common/src/config.cpp': {'mode': '100644',
                                        'blob': '701e4ac8c0a635b77ef4282f29109f7bb0bea726',
                                        'sha256': 'bde443c7eceb417494ae71191a2076c0ab251e987706f30a757b14aaf16ad0e5'},
 'HAL/pico/src/core/Persistence.cpp': {'mode': '100644',
                                       'blob': '907e6ca3d84fc414aa67dadfcbf4f60d1e1200a7',
                                       'sha256': '941cc54f0fb762e6067db338601325d33cf7f980148a59caa1d61f226e140955'},
 'HAL/pico/include/core/Persistence.hpp': {'mode': '100644',
                                           'blob': '43cbd3f39b4c9a09ecc855b0f2704b2081a45981',
                                           'sha256': '56d8c3281b54a6d8168a7e8d04d31c0c2b20d1c2223b21b77a9a1549460a669d'},
 'HAL/pico/src/comms/ConfiguratorBackend.cpp': {'mode': '100644',
                                                'blob': '6ca93c96c944ee539a2d409e32889306c1eafac7',
                                                'sha256': '68bc7756eacb63c6831709c803349d52206ed7a271dc49b0cd33d6c53f0c3c38'},
 'HAL/pico/src/comms/backend_init.cpp': {'mode': '100644',
                                         'blob': 'f7726a0063dd05409d7464d947a47efc675bdbef',
                                         'sha256': '8cbd355e6323a775ab88aacef2ca07d2cad88232790f9d8b8d3f2f686875e2ea'},
 'HAL/pico/include/comms/backend_init.hpp': {'mode': '100644',
                                             'blob': '783cb54e5d01d33e931136e9cbb15f696a510029',
                                             'sha256': '3c2e4b29d06e85e17ba0f63ac7160589ec0b5661874406a9e3a576446b2cf227'},
 'HAL/pico/src/reboot.cpp': {'mode': '100644',
                             'blob': '796c7f4b7337004b6f68a59c9e775e55f4578742',
                             'sha256': 'f89b9199f55e8f116901ca49484f7ef6c3fe51c048dc31a98934d08bf0a5627e'},
 'include/reboot.hpp': {'mode': '100644',
                        'blob': '506e0c5784eaa9d5da632e05504fef4928b20e52',
                        'sha256': 'bcc6237cd7c3b85e263cdfd2f265aaf257537a75fc6518acb4edf5f0ab14ef6d'},
 'src/core/mode_selection.cpp': {'mode': '100644',
                                 'blob': '7d659d3133271c2ed956a16d8f5e3eda73040f81',
                                 'sha256': '8df6ddf1ca626f7d840e68ea700654bcbc30f6473fe7383abc4bf6e99fc4fd44'},
 'src/core/config_utils.cpp': {'mode': '100644',
                               'blob': 'beeb1202f67f61ce717e0e020cb3dd339dfa6206',
                               'sha256': 'b97af928bff72103f90b0155e4e63fd44a3cfcb84e46ac93cf74f6f3227e02ab'},
 'HAL/pico/include/util/state_util.hpp': {'mode': '100644',
                                          'blob': '40b8aeb9c4db3268696c49f20b3278efabc7688c',
                                          'sha256': 'db4b4ee7dcfe462dd00097a5109e028787e11d7868b012f447c9fee84e68ea81'},
 'platformio.ini': {'mode': '100644',
                    'blob': '4d56f8630c1b12e84cd12f40ce05a4dc71b9362e',
                    'sha256': '99fc26f84f4cf2c118d08fde7269a13b9b37f6ed1efb2d32291ba9f0b8e780e9'},
 'config/glyph/env.ini': {'mode': '100644',
                          'blob': 'fac4e20461ad632ca1d65826241a4a9c73630f04',
                          'sha256': 'c754c2f504c8740763d3f65fa114cc61c21fe5d73bd489c728610c1299d1fccf'},
 'builder_scripts/arduino_pico.py': {'mode': '100644',
                                     'blob': '35381a91ad5aa4ffdbcd362365c1bf9fbd13136e',
                                     'sha256': '676b20e42500cb0b5f671892250a2c063e21a31459ed542ad48a9481a7fce0af'},
 'docs/runtime_config/fixtures/gp_prov_014_decoder_closure.json': {'mode': '100644',
                                                                   'blob': '25d32a1fc1cc9c39626eadd4dca4835103579d80',
                                                                   'sha256': 'a0f017c36ce0354f91d1a62210756c0464c6db9b5183ba6592ce69d32da1e13f'},
 'tools/fixtures/gp_config012_button_host/schema/config.proto': {'mode': '100644',
                                                                 'blob': 'a58a2bf4dd827ad92482f1ac30c3d56bbea93c05',
                                                                 'sha256': '2844d8fc8c78c9fbed00a6954a13d9826f4634cac152f8a9a707666f47bb893b'},
 'tools/fixtures/gp_config012_button_host/schema/config.options': {'mode': '100644',
                                                                   'blob': '7175d8463ade5b0cd45f1a5f8f99be44f5719c3c',
                                                                   'sha256': '6a53dc93a79027669a3990c3a785e386e02e063c1f3438744aac49c3ad074805'},
 'tools/fixtures/gp_config012_button_host/generated/config.pb.h': {'mode': '100644',
                                                                   'blob': '01d0dda2ae768dd0f18c0f338a74c55e613bb199',
                                                                   'sha256': 'bdd72a220126911d7f6d2558ec5517be96189af92242979e3af43d1076550323'},
 'tools/fixtures/gp_config012_button_host/generated/config.pb.c': {'mode': '100644',
                                                                   'blob': 'c59855ecb19be7f5193833d94fe41cc1828ffb14',
                                                                   'sha256': 'd7041bfaf221cc747c7f2dc3fa8586352a1b8dc363fbdcfca181774562941626'},
 'tools/fixtures/gp_config012_button_host/nanopb/pb.h': {'mode': '100644',
                                                         'blob': '3f181d873a81d82c27c56874f6a63328f38eaaf3',
                                                         'sha256': 'e0db84a27e0d41a2d2d347b8c879e30ceb856d36dc192cce0f1124f833c67bc2'},
 'tools/fixtures/gp_config012_button_host/nanopb/pb_decode.h': {'mode': '100644',
                                                                'blob': '1ef9d56c6e0b6430f9067cbb911c7e697d034e24',
                                                                'sha256': 'fcac5f7680fe6e870157e4bcf34d5162bdd4fff0d7db3cad1122f2ad24a6da87'},
 'tools/fixtures/gp_config012_button_host/nanopb/pb_decode.c': {'mode': '100644',
                                                                'blob': '0f71c33b1bd99e531c9eacda5f9b012ddb3c8339',
                                                                'sha256': 'f5b425beaa207251e531c8ce2c86c9b6867e2920ed59cc1b125332af0c147632'},
 'tools/fixtures/gp_config012_button_host/nanopb/pb_common.h': {'mode': '100644',
                                                                'blob': '58aa90f76d58596d3f45a120b65b4a0bff7fd688',
                                                                'sha256': '6495a691aca68d6973f2274b5dd54b74fbb57f6b019c45fff255a857fe1abcfd'},
 'tools/fixtures/gp_config012_button_host/nanopb/pb_common.c': {'mode': '100644',
                                                                'blob': '6aee76b1efa1e6f2f3fe7d43629da9b2114eea19',
                                                                'sha256': '8d2ec28baaaf2b7a5e90e4cb2fa9700d21cef7f826f051a637c30b7a1e6a0516'},
 'tools/fixtures/gp_config012_button_host/LICENSE.nanopb.txt': {'mode': '100644',
                                                                'blob': 'd11c9af1d7e469e9a5357a660fd184f58c3a4ff2',
                                                                'sha256': 'e2f2fc8fe3faa7dcb09dbe995db48c6ec5c1f72705db915101e4a83fed44f66d'},
 'include/core/config_button_validation.hpp': {'mode': '100644',
                                               'blob': '1b6e3dc98a9b6c0eb1f04e077c86382eaee324bb',
                                               'sha256': '176cec58249c48e51d418af0af9f64b4d6b8942d4c53c6a8b6f519dcc9c3193f'},
 'src/core/config_button_validation.cpp': {'mode': '100644',
                                           'blob': '70a7cee746fd42d1cfaff11f6043650bbfcc4c74',
                                           'sha256': '4025f581961e63a8ef6a290b41786b59291bada5e77ab665dbe448ed27418d2d'}}
CONFIG019_FRAGMENT_PINS = {'defaults': '6bd7e0f7170aff3608106096b26b0b4e410aa6e0cf4aa43aa00076bb8b66e31f',
 'default_copy': 'fb34a4b4eeaf27de120f21e866f4dd6294fec326a9e9b0be9d1f832215fda834',
 'sameName': 'b7faa9e5b31de90ac1dfe0254286beb22e68a1d673dab82dd4f9fd1879d179c4',
 'selector': '5fcc08ae11cd40795fa5c8c2d4bae1d1c3bdee2f6a660842ccb9ffaf7b179247',
 'usb_menu': 'c5f6d0cc98d8c077fd2a914437734ea9f3a47b3e25c62561becebb5caedf1e9d',
 'acceptance': '400290a51fb4740cec889bd7c5eecf719a5e80c8145da3589dd5a66a9d991746',
 'load': '374511570ccad298cbe6265f0dcffc877ca0d452484369a501dc42fa94fdc770',
 'mask_helpers': '1e422153ff64a5991c88b1fc8a0957ac31c65d26e9ba623459025d3a9cf40e15',
 'backend_helpers': 'f1d9899958ea5c7372188d349c9aea82e593c8e329c6223a39a6a165d54a0fbc',
 'backend_selector': 'de38f52b6d0362985a4107407dc6ed12deb41ac6c5cf522e3ebf38cc43aa322d',
 'usb_getter': '807d98db9948beabf51edee14d6cfaa6326ce5f33039dbb458adfd178318311b',
 'watchdog_consumer': '158a3d028c42dc87fe236e64f85f9c619dfd6ca1316c30821e75ecba53715b1b'}
CONFIG019_ACCEPTANCE_SHA256 = 'b7c17505e097612fb4b718fc385a0525b3713dc5e4187955364a58c5b8b8547a'
CONFIG019_OVERLAY_PINS = {'tools/check_glyph_gp_config019_usb_name_selection.py': {'mode': '100644',
                                                          'blob': 'fca0697ccf5f98e3593421934b75dc658f4a8750',
                                                          'sha256': 'efd7568fdda52e153bb7ea76fc3d827932a9bc228eb75d628de6404090eb7402'},
 'tools/fixtures/gp_config019_usb_name_selection/current_acceptance.cpp': {'mode': '100644',
                                                                           'blob': '897646b941b1c89a0d90dd95ba6eedb3f3ff9b33',
                                                                           'sha256': 'be0ace2b917ade71cde930e5e3293443bfe26f4713a4d40d82008a22e0615e1b'},
 'docs/runtime_config/fixtures/gp_val041_usb_name_current_acceptance.json': {'mode': '100644',
                                                                             'blob': 'b7415fe877f2ac0023edd9ea62a443b2b22ec2ad',
                                                                             'sha256': 'c918594c260e8a4a675d84c0b808be1c87ac876ea8b2ca138316162de2863453'},
 'docs/runtime_config/gp_val041_usb_name_current_acceptance.md': {'mode': '100644',
                                                                  'blob': '22c2aa6d49071e5ad2e3d9720fb19943cd959dd2',
                                                                  'sha256': '9aa78efa0e35eb483281865e2e25f6611c9653beccb4757ba399959a0012eaab'}}
CONFIG019_MANIFEST_ENTRY_SHA256 = '29150fcfac8f1f08ee0c1e46cc652da281e9064e44748e4c5f057d8a288479e8'
CONFIG019_HOSTS = frozenset(CONFIG019_HOST_PINS)
CONFIG019_ORIGINAL_HOSTS = CONFIG019_HOSTS - {CONFIG019_CHECKER}
CONFIG019_OVERLAY_PATHS = frozenset((CONFIG019_CHECKER,
 'tools/fixtures/gp_config019_usb_name_selection/current_acceptance.cpp',
 'docs/runtime_config/fixtures/gp_val041_usb_name_current_acceptance.json',
 'docs/runtime_config/gp_val041_usb_name_current_acceptance.md'))

NEW_PATHS = frozenset((MAPPING, TRANSITIONS, 'tools/glyph_c014_campaign_transition.py',
 'tools/test_glyph_c014_campaign_transition.py'))
GOVERNANCE_PATHS = (predecessor.GOVERNANCE_PATHS | predecessor.REVISION_THREE_PATHS |
 predecessor.PERSISTENT_BATCH_PATHS | HOSTS | HOST_OVERLAYS | NEW_PATHS | KBD_HOSTS | CONFIG019_HOSTS | CONFIG019_OVERLAY_PATHS |
 frozenset(CONFIG019_AUTHORITY_PINS) |
 frozenset((PROTOCOL, EVIDENCE, RESULT, predecessor.OWNER_DIRECTION,
            'tools/check_glyph_custom_modifier_cache_characterization.py')))
ROOTS = predecessor.ROOTS | frozenset((C, B, HANDOFF, READY, KBD_C, KBD_B, KBD_AUTHORITY,
 predecessor.PERSISTENT_BATCH_AUTHORITY, predecessor.REVISION_THREE_AUTHORITY,
 predecessor.OWNER_DIRECTION_AUTHORITY, CONFIG019_C, CONFIG019_B, CONFIG019_F020,
 CONFIG019_OPENING, CONFIG019_RECEIPT_COMMIT, CONFIG019_RECEIPT_PARENT, CONFIG019_ADOPTION))
AUTHORITY_SHA256 = {
 B: 'a7006b98a6f7da16cddc17bc249861d613464010c30c5f458515e65a92a84dec',
 HANDOFF: 'b4897410c2922eed071cb8a8895f29724b26cfe0ff9b44af2791ace2f56f86cd',
 READY: '15216484e2fcebc992d3a78d5c8e67ed9890f820e0cd476e1261f763bc8fb7c1'}
REQUIRED_ROWS = ('modifier_0', 'modifier_10', 'modifier_11', 'modifier_20',
                 'combos_modifiers', 'ultimate_x1', 'reconnect_reboot', 'owner_config_restoration')
IDENTITIES = ('candidate_git_sha', 'candidate_base_configurator_sha',
 'firmware_artifact_sha256', 'firmware_artifact_build_path', 'preserved_firmware_artifact_locator',
 'manual_acceptance_protocol_reference', 'manual_acceptance_protocol_version',
 'hardware_evidence_contract_reference', 'hardware_evidence_contract_version')
require = original.require
unique = original.unique
_git = original._git
_tree = original._tree
raw_bytes = original.raw_bytes
current_bytes = original.current_bytes
critical_tree = original.critical_tree
ancestor = original.ancestor
item = original.item
queue = original.queue

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def immutable(identity):
    require(isinstance(identity, str) and re.fullmatch('[0-9a-f]{40}', identity),
            'nonimmutable C014 identity')
    return identity

def parsed_queue(raw):
    text = raw.decode()
    start, end = '<!-- queue-state:start -->', '<!-- queue-state:end -->'
    require(text.count(start) == text.count(end) == 1, 'queue marker mismatch')
    block = text.split(start)[1].split(end)[0].strip()
    require(block.startswith('```json') and block.endswith('```'), 'queue fence mismatch')
    return json.loads(block[7:-3], object_pairs_hook=unique)

def state_from(raw, order):
    found = [x for x in parsed_queue(raw)['items'] if x['id'] == order]
    require(len(found) == 1, 'missing/duplicate order')
    return found[0]

@original._proof_invocation
def source_contract(root):
    root = Path(root).resolve()
    for revision, digest in AUTHORITY_SHA256.items():
        require(sha(raw_bytes(root, revision, QUEUE)) == digest, 'C014 immutable authority substitution')
    require(_git(root, 'rev-list', '--parents', '-n', '1', C).decode().split() == [C, B],
            'C014 candidate direct parent mismatch')
    require(_git(root, 'rev-parse', C + '^{tree}').decode().strip() == TREE, 'C014 tree mismatch')
    require(sha(_git(root, 'diff-tree', '-r', '--no-renames', '--raw', '-z', B, C)) == RAW,
            'C014 raw inventory mismatch')
    mapping_raw = current_bytes(root, MAPPING)
    require(sha(mapping_raw) == MAPPING_SHA256, 'C014 mapping substitution')
    mapping = json.loads(mapping_raw, object_pairs_hook=unique)
    require(set(mapping) == {'schema_name', 'schema_version', 'work_order', 'candidate', 'base',
                            'tree', 'raw_inventory_sha256', 'entries', 'handoff', 'ready',
                            'review_sha256', 'validation_sha256'}, 'C014 mapping field mismatch')
    require(mapping['schema_name'] == 'glyph_gp_val034_c014_transition'
            and type(mapping['schema_version']) is int and mapping['schema_version'] == 1
            and mapping['work_order'] == 'GP-VAL-034'
            and (mapping['candidate'], mapping['base'], mapping['tree'], mapping['raw_inventory_sha256'],
                 mapping['handoff'], mapping['ready']) == (C, B, TREE, RAW, HANDOFF, READY),
            'C014 literal mapping identity mismatch')
    bt, ct = _tree(root, B), _tree(root, C)
    paths = {p for p in bt.keys() | ct.keys() if bt.get(p) != ct.get(p)}
    metadata = frozenset(('docs/runtime_config/fixtures/runtime_config_validation_manifest.json',
                         'docs/runtime_config/fixtures/glyph_checker_census.json',
                         'docs/runtime_config/fixtures/runtime_config_validation_health.json',
                         'docs/runtime_config/runtime_config_validation_health.md'))
    require(paths == CRITICAL | HOSTS | metadata and len(mapping['entries']) == 10,
            'C014 finite ten-path membership mismatch')
    require({x['path'] for x in mapping['entries']} == paths, 'C014 duplicate/omitted inventory path')
    for entry in mapping['entries']:
        require(set(entry) == {'path', 'old_mode', 'new_mode', 'old_blob', 'new_blob', 'status'},
                'C014 inventory fields mismatch')
        p = entry['path']; old = bt.get(p)
        require(ct[p][:2] == ('100644', 'blob') and entry['new_mode'] == '100644'
                and entry['new_blob'] == ct[p][2]
                and (entry['old_mode'], entry['old_blob'], entry['status']) ==
                    ((old[0], old[2], 'M') if old else ('000000', '0' * 40, 'A')),
                'C014 inventory blob/mode/status substitution: ' + p)
    before, after = critical_tree(root, B), critical_tree(root, C)
    require(len(before) == len(after) == 236
            and {p for p in before.keys() | after.keys() if before.get(p) != after.get(p)} == CRITICAL,
            'C014 critical union outside two entries')
    require(after['include/modes/CustomControllerMode.hpp'][2] == '9658f5e15f50887caaaf5a71efc0096e9677d144'
            and after['src/modes/CustomControllerMode.cpp'][2] == '8cb336f31acd4c324b3ae1f8ef0827c14f15ee85',
            'C014 repaired source not adopted exact blobs')
    require(critical_tree(root, HANDOFF) == before == critical_tree(root, READY)
            and ancestor(root, B, HANDOFF) and ancestor(root, HANDOFF, READY)
            and not ancestor(root, C, HANDOFF), 'C014 handoff/READY contains source or wrong ancestry')
    ready = item(root, READY, 'GP-VAL-034')
    require(ready['status'] == 'READY' and ready['activation_state'] == 'NOT_APPLICABLE'
            and item(root, READY, 'GP-VAL-037')['status'] == 'DONE', '034 readiness/predecessor mismatch')
    text = raw_bytes(root, HANDOFF, QUEUE).decode()
    match = re.findall(r'<!-- gp-config014-handoff:start -->\s*```json\s*(.*?)\s*```\s*<!-- gp-config014-handoff:end -->', text, re.S)
    require(len(match) == 1, 'missing/duplicate C014 handoff')
    handoff = json.loads(match[0], object_pairs_hook=unique)
    require(handoff['candidate'] == C and handoff['base'] == B and handoff['candidate_tree'] == TREE
            and handoff['inventory'] == mapping['entries'] and handoff['raw_inventory_sha256'] == RAW
            and handoff['candidate_published_live_verified'] is True
            and handoff['candidate_firmware_integrated'] is False and handoff['gate_waivers'] is False,
            'C014 source-free handoff substitution')
    for filename, key in (('candidate-review.json', 'review_sha256'),
                          ('candidate-validation.json', 'validation_sha256')):
        record = handoff['reports'][filename]
        require(record['sha256'] == mapping[key]
                and sha((json.dumps(record['report'], indent=2) + '\n').encode()) == mapping[key],
                'C014 immutable execution receipt digest mismatch')
    review = handoff['reports']['candidate-review.json']['report']
    require(review['reviewed_sha'] == C and review['blocking_findings_for_bounded_candidate_handoff'] == []
            and review['verdict'] == 'APPROVED_FOR_EXACT_CANDIDATE_PUBLICATION_AND_SOURCE_FREE_HANDOFF_ONLY'
            and review['gate_waivers'] is False and review['hardware_acceptance'] is False,
            'C014 independent conformance receipt mismatch')
    authenticate_kbd_contract(root)
    return before, after

def current_integrity(root, head, expected):
    """Prove actual critical working bytes, index, modes and ignored input traps."""
    require(critical_tree(root, head) == expected, 'current critical source outside C014 contract')
    tags = _git(root, 'ls-files', '-v', '-z').decode().split('\0')
    for record in filter(None, tags):
        tag, path = record[0], record[2:]
        if path in expected:
            require(not tag.islower() and tag != 'S', 'assume-unchanged/skip-worktree critical trap: ' + path)
    staged = {}
    for record in _git(root, 'ls-files', '--stage', '-z').decode().split('\0'):
        if record:
            meta, path = record.split('\t'); mode, blob, stage = meta.split()
            if path in expected:
                require(stage == '0', 'unmerged critical index')
                staged[path] = (mode, 'blob', blob)
    require(staged == expected, 'critical index differs from committed source')
    for path, entry in expected.items():
        file = root / path
        require(file.is_file() and all(not p.is_symlink() for p in (file, *file.parents)),
                'critical missing/symlink input: ' + path)
        mode = '100755' if file.stat().st_mode & 0o111 else '100644'
        data = file.read_bytes()
        blob = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
        require((mode, 'blob', blob) == entry, 'critical worktree bytes/mode mismatch: ' + path)
    dirty = set(); ignored = set(filter(None, _git(root, "ls-files", "--others", "--ignored", "--exclude-standard", "-z").decode().split("\0")))
    for args in (('diff', '--name-only', '-z'), ('diff', '--cached', '--name-only', '-z'),
                 ('ls-files', '--others', '--exclude-standard', '-z'),
                 ('ls-files', '--others', '--ignored', '--exclude-standard', '-z')):
        dirty.update(filter(None, _git(root, *args).decode().split('\0')))
    permitted_caches = set()
    for path in dirty:
        try:
            category = classify_path(path)
        except CorrespondenceError:
            category = 'UNKNOWN'
        require(category != 'CRITICAL', 'dirty/staged/untracked/ignored critical input: ' + path)
        cache = (any(path == prefix or path.startswith(prefix + '/') for prefix in IGNORED_ALLOWED_ROOTS)
                 or (path.startswith('tools/__pycache__/') and path.endswith('.pyc')))
        # Existing ignored build/custody/cache bytes never supply proof inputs.
        if path in ignored and cache:
            permitted_caches.add(path)
        else:
            require(path in GOVERNANCE_PATHS, 'dirty path outside finite C014 governance: ' + path)
            if (root / path).exists():
                current_bytes(root, path)
    return dirty - permitted_caches

def catalog(raw):
    value = json.loads(raw, object_pairs_hook=unique)
    require(set(value) == {'schema_version', 'accepted_transitions'}
            and type(value['schema_version']) is int and value['schema_version'] == 1
            and type(value['accepted_transitions']) is list and len(value['accepted_transitions']) <= 1,
            'C014 catalog fields/count mismatch')
    fields = {'work_order', 'candidate', 'build', 'parent', 'tree', 'review_commit', 'evidence_commit', 'integration'}
    for record in value['accepted_transitions']:
        require(type(record) is dict and set(record) == fields and record['work_order'] == 'GP-CONFIG-014'
                and record['candidate'] == C, 'unadopted C014 catalog record')
        for key in fields - {'work_order'}:
            immutable(record[key])
    return value['accepted_transitions']

def same_acceptance(a, b):
    return all(a[k] == b[k] for k in (*IDENTITIES, 'hardware_evidence_record',
                                    'hardware_result', 'hardware_evidence_gaps', 'hardware_evidence_dependency_satisfied'))

@original._proof_invocation
def processor_record(root, E, before, after):
    """Authenticate an actual source-free processor snapshot independently of I."""
    accepted = item(root, E, 'GP-CONFIG-014')
    require(accepted['status'] == 'HARDWARE_VALIDATED' and accepted['hardware_result'] == 'PASS'
            and accepted['hardware_evidence_gaps'] == []
            and accepted['hardware_evidence_dependency_satisfied'] is True, '014 E lacks complete native PASS')
    F, parent = immutable(accepted['candidate_git_sha']), immutable(accepted['candidate_base_configurator_sha'])
    require(_git(root, 'rev-list', '--parents', '-n', '1', F).decode().split() == [F, parent]
            and ancestor(root, C, F) and ancestor(root, READY, F)
            and not ancestor(root, F, E) and critical_tree(root, E) == before
            and critical_tree(root, F) == after, '014 F/source-free E ancestry or source mismatch')
    verify_correspondence(root, C, B, target=F, integrated=True, check_worktree=False)
    require(accepted['manual_acceptance_protocol_reference'] == PROTOCOL
            and accepted['manual_acceptance_protocol_version'] == 'GP_CONFIG_014_HW_V1', '014 protocol mismatch')
    digest = accepted['firmware_artifact_sha256']
    require(isinstance(digest, str) and re.fullmatch('[0-9a-f]{64}', digest)
            and accepted['preserved_firmware_artifact_locator'] ==
                f'local_backups/hardware-artifacts/{F}/{digest}/firmware.uf2', '014 artifact custody mismatch')
    reference = accepted['hardware_evidence_record']
    if reference == 'repo-json:' + EVIDENCE:
        evidence_root = E
    else:
        m = re.fullmatch(r'git-json:([0-9a-f]{40}):' + re.escape(EVIDENCE), str(reference))
        require(m is not None, '014 unsupported evidence reference')
        evidence_root = m.group(1)
        require(ancestor(root, evidence_root, E), '014 evidence root after processor E')
    payload = raw_bytes(root, evidence_root, EVIDENCE)
    native = dict(accepted, hardware_evidence_record='git-json:' + evidence_root + ':' + EVIDENCE)
    from check_glyph_agent_framework_docs import validate_work_order, validate_evidence_record
    validate_work_order(native, evidence_repo_root=root)
    validate_evidence_record(native, evidence_repo_root=root)
    evidence = json.loads(payload, object_pairs_hook=unique)
    ids = [row['id'] for row in evidence['steps']]
    require(len(ids) == len(set(ids)) and all(row in ids for row in REQUIRED_ROWS),
            '014 evidence required rows missing/duplicate')
    require(evidence['anomalies'] == [] and evidence['evidence_gaps'] == [], '014 acceptance has anomalies/gaps')
    review = None
    for revision in _git(root, 'rev-list', '--reverse', '--topo-order', READY + '..' + E).decode().split():
        state = item(root, revision, 'GP-CONFIG-014')
        if state['status'] in {'REVIEW', 'HARDWARE_TEST_REQUIRED'} and state['hardware_result'] is None:
            if all(state[k] == accepted[k] for k in IDENTITIES) and PROTOCOL in _tree(root, revision):
                record = {'build': F, 'tree': _git(root, 'rev-parse', F + '^{tree}').decode().strip(), 'parent': parent}
                original.validate_build_review(raw_bytes(root, revision, PROTOCOL).decode(), record, digest,
                                               accepted['preserved_firmware_artifact_locator'])
                review = revision
                break
    require(review is not None and review != E and ancestor(root, review, E)
            and ancestor(root, review, evidence_root) and not ancestor(root, F, review)
            and critical_tree(root, review) == before, '014 lacks source-free independent reviewed R before E')
    protocol = raw_bytes(root, review, PROTOCOL)
    require(raw_bytes(root, E, PROTOCOL) == protocol, '014 protocol changed between R/E')
    for row in evidence['steps']:
        require(row['id'] in protocol.decode(), '014 evidence row absent from reviewed protocol')
    return dict(work_order='GP-CONFIG-014', candidate=C, build=F, parent=parent,
                tree=_git(root, 'rev-parse', F + '^{tree}').decode().strip(),
                review_commit=review, evidence_commit=E, evidence_root=evidence_root,
                native=accepted, payload=payload, protocol=protocol,
                result=raw_bytes(root, E, RESULT))

@original._proof_invocation
def history(root, head, before, after):
    earliest = None; integrated = None; done = False
    c020 = item(root, B, 'GP-CONFIG-020')
    c020_literals = (predecessor.PROTOCOL, predecessor.EVIDENCE, predecessor.RESULT, predecessor.TRANSITIONS)
    for revision in _git(root, 'rev-list', '--reverse', '--topo-order', B + '..' + head).decode().split():
        if revision == CONFIG019_C:
            authenticate_config019_contract(root)
            require(ancestor(root, CONFIG019_B, B) and not ancestor(root, B, CONFIG019_C),
                    '019 historical sidebranch chronology mismatch')
            continue
        if revision == KBD_C:
            require(_git(root, 'rev-list', '--parents', '-n', '1', KBD_C).decode().split() == [KBD_C, KBD_B]
                    and ancestor(root, KBD_B, B) and not ancestor(root, B, KBD_C),
                    'KBD historical sidebranch chronology mismatch')
            continue
        old = item(root, revision, 'GP-CONFIG-020')
        require(old['status'] == 'DONE' and same_acceptance(old, c020), '014 history erased/replaced accepted C020')
        for path in c020_literals:
            require(raw_bytes(root, revision, path) == raw_bytes(root, B, path), '014 history changed immutable C020 metadata')
    for revision in _git(root, 'rev-list', '--reverse', '--topo-order', READY + '..' + head).decode().split():
        if revision == CONFIG019_C:
            authenticate_config019_contract(root)
            require(ancestor(root, CONFIG019_B, READY) and not ancestor(root, READY, CONFIG019_C),
                    '019 historical sidebranch cannot supply014 acceptance')
            continue
        state = item(root, revision, 'GP-CONFIG-014')
        records = catalog(raw_bytes(root, revision, TRANSITIONS)) if TRANSITIONS in _tree(root, revision) else []
        if records:
            require(earliest is not None, '014 integration catalog precedes processor E')
            record = records[0]
            require(all(record[k] == earliest[k] for k in ('candidate', 'build', 'parent', 'tree',
                                                          'review_commit', 'evidence_commit')),
                    '014 accepted catalog replaced earliest processor tuple')
            I = record['integration']
            require(ancestor(root, earliest['evidence_commit'], I) and ancestor(root, record['build'], I)
                    and ancestor(root, I, revision) and critical_tree(root, revision) == after,
                    '014 integration/catalog chronology or critical tree mismatch')
            require(integrated is None or integrated == record, '014 accepted catalog replacement')
            integrated = record
        if integrated is not None and ancestor(root, integrated['integration'], revision):
            require(bool(records), '014 accepted catalog removed after introduction')
        if state['hardware_result'] == 'PASS' or state['status'] in {'HARDWARE_VALIDATED', 'DONE'}:
            require(state['hardware_result'] == 'PASS' and state['status'] in {'HARDWARE_VALIDATED', 'DONE'}, '014 PASS in invalid native status')
            require(not done or state['status'] == 'DONE', '014 DONE status downgraded')
            if earliest is None:
                require(not records, '014 first PASS must be source-free E')
                earliest = processor_record(root, revision, before, after)
            else:
                require(same_acceptance(state, earliest['native']), '014 processor acceptance downgraded/replaced')
            if state['status'] == 'DONE':
                require(bool(records), '014 DONE lacks accepted integration catalog')
                done = True
        elif earliest is not None and ancestor(root, earliest['evidence_commit'], revision):
            require(False, '014 processor PASS erased/downgraded')
    return earliest, integrated

@original._proof_invocation
def authenticate(root):
    root = Path(root).resolve(); head = _git(root, 'rev-parse', 'HEAD').decode().strip()
    require(ancestor(root, READY, head), 'C014 context lacks immutable 034 READY authority')
    before, after = critical_tree(root, B), critical_tree(root, C)
    current = critical_tree(root, head)
    require(current in (before, after), 'current critical tree outside accepted020/C014')
    dirty = current_integrity(root, head, current)
    overlays = authenticate_host_overlays(root, head)
    kbd = authenticate_kbd_coexistence(root, head)
    config019 = authenticate_config019_coexistence(root, head)
    delta = set(filter(None, _git(root, 'diff', '--no-renames', '--name-only', '-z', B, head).decode().split('\0')))
    require(delta | dirty <= GOVERNANCE_PATHS | CRITICAL, 'unreviewed C014 governance/source delta')
    for path in delta:
        entry = _tree(root, head).get(path)
        require(entry is not None and entry[:2] == ('100644', 'blob'), 'C014 changed path deleted/unsafe mode: ' + path)
    predecessor._owner_direction_scope(root, head, delta | {predecessor.OWNER_DIRECTION})
    c020 = item(root, B, 'GP-CONFIG-020')
    for raw in (raw_bytes(root, head, QUEUE), current_bytes(root, QUEUE), _git(root, 'show', ':' + QUEUE)):
        state = state_from(raw, 'GP-CONFIG-020')
        require(same_acceptance(state, c020) and state['status'] == 'DONE', '014 changed accepted C020 identity/result')
    for path in (predecessor.PROTOCOL, predecessor.EVIDENCE, predecessor.RESULT, predecessor.TRANSITIONS):
        require(raw_bytes(root, head, path) == raw_bytes(root, B, path)
                and current_bytes(root, path) == raw_bytes(root, B, path)
                and _git(root, 'show', ':' + path) == raw_bytes(root, B, path), '014 changed immutable C020 metadata')
    for path in original.FROZEN:
        require(current_bytes(root, path) == raw_bytes(root, original.B, path), '014 changed frozen historical fixture')
    for path in HOSTS - HOST_OVERLAYS:
        if path in _tree(root, head) or (root / path).exists():
            require(current_bytes(root, path) == raw_bytes(root, C, path), '014 frozen candidate host substitution')
    state = item(root, head, 'GP-CONFIG-014')
    require(state['status'] != 'HARDWARE_FAILED' and state['hardware_result'] != 'FAIL', 'failed014 cannot validate')
    source_contract(root)
    prior = predecessor.authenticate_committed_predecessor(root, B)
    require(prior['phase'] == 'ACCEPTED_TRANSITION', 'C014 predecessor not actually accepted')
    records = catalog(current_bytes(root, TRANSITIONS))
    if TRANSITIONS in _tree(root, head):
        require(current_bytes(root, TRANSITIONS) == raw_bytes(root, head, TRANSITIONS), 'uncommitted014 accepted catalog')
    else:
        require(records == [], 'uncommitted014 acceptance')
    processor, accepted = history(root, head, before, after)
    require(records == ([accepted] if accepted else []), '014 current catalog/history mismatch')
    phase = 'BASELINE'; protected = predecessor.CRITICAL
    if current == after:
        require(ancestor(root, C, head), 'C014 source replay without candidate ancestry')
        verify_correspondence(root, C, B, target=head, integrated=True, check_worktree=False)
        phase = 'CANDIDATE_VALIDATION_ONLY'; protected |= CRITICAL
    require(not (state['hardware_result'] == 'PASS' or state['status'] in {'HARDWARE_VALIDATED', 'DONE'})
            or processor is not None, '014 PASS without genuine processor E')
    metadata = frozenset((predecessor.PROTOCOL, predecessor.EVIDENCE, predecessor.RESULT))
    roots = set(ROOTS) | set(prior['object_roots'])
    if processor:
        require(same_acceptance(state, processor['native']), '014 current processor tuple drift')
        for path, expected in ((EVIDENCE, processor['payload']), (PROTOCOL, processor['protocol']),
                               (RESULT, processor['result'])):
            require(current_bytes(root, path) == expected and raw_bytes(root, head, path) == expected
                    and _git(root, 'show', ':' + path) == expected, '014 accepted evidence/protocol/result substitution')
        for raw in (current_bytes(root, QUEUE), _git(root, 'show', ':' + QUEUE)):
            require(same_acceptance(state_from(raw, 'GP-CONFIG-014'), state), '014 live/index PASS tuple drift')
        roots.update(processor[k] for k in ('build', 'parent', 'review_commit', 'evidence_commit', 'evidence_root'))
        metadata |= frozenset((PROTOCOL, EVIDENCE, RESULT))
        if current == before:
            require(not accepted and not ancestor(root, processor['build'], head), 'source-free014 E contains integrated F')
            phase = 'SOURCE_FREE_PROCESSOR'
        else:
            require(accepted is not None, 'integrated014 PASS lacks accepted catalog')
    if accepted:
        require(current == after and processor is not None, '014 accepted catalog on baseline')
        verify_correspondence(root, accepted['build'], accepted['parent'], target=head,
                              integrated=True, check_worktree=False)
        phase = 'ACCEPTED_TRANSITION'; roots.add(accepted['integration'])
    source_candidates = {p: predecessor.C_R for p in predecessor.CRITICAL}
    if current == after:
        source_candidates.update({p: C for p in CRITICAL})
    return dict(phase=phase, contract='c014_capacity', candidate=C, base=B, target=head,
                critical_paths=protected, accepted_metadata_paths=metadata,
                changed_paths=frozenset(delta | dirty), object_roots=frozenset(roots),
                source_candidates=source_candidates, host_overlay_paths=overlays,
                kbd_host_paths=kbd, config019_host_paths=config019,
                evidence_commit=processor['evidence_commit'] if processor else None)

def verify_current_source(root, path, historical_sha256=None):
    root = Path(root).resolve(); old = raw_bytes(root, original.B, path)
    if historical_sha256 is not None:
        require(sha(old) == historical_sha256, 'historical source identity mismatch: ' + path)
    current = current_bytes(root, path)
    if current != old:
        proof = authenticate(root)
        owner = proof['source_candidates'].get(path)
        require(owner is not None and current == raw_bytes(root, owner, path), 'unadopted014 source overlay: ' + path)
    return old

@original._proof_invocation
def authenticate_kbd_contract(root):
    """Bind known immutable H1 object closure even before optional publication."""
    require(_git(root, 'rev-list', '--parents', '-n', '1', KBD_C).decode().split() == [KBD_C, KBD_B]
            and _git(root, 'rev-parse', KBD_C + '^{tree}').decode().strip() == KBD_TREE
            and sha(_git(root, 'diff-tree', '-r', '--no-renames', '--raw', '-z', KBD_B, KBD_C)) == KBD_RAW,
            'KBD immutable candidate parent/tree/raw inventory mismatch')
    before, after = _tree(root, KBD_B), _tree(root, KBD_C)
    metadata = frozenset(('docs/runtime_config/fixtures/runtime_config_validation_manifest.json',
                         'docs/runtime_config/fixtures/glyph_checker_census.json',
                         'docs/runtime_config/fixtures/runtime_config_validation_health.json',
                         'docs/runtime_config/runtime_config_validation_health.md'))
    require({p for p in before.keys() | after.keys() if before.get(p) != after.get(p)} == KBD_HOSTS | metadata,
            'KBD immutable nine-path membership mismatch')
    require(len(KBD_HOSTS) == 5 and len(KBD_DEPENDENCY_PINS) == 28
            and critical_tree(root, KBD_B) == critical_tree(root, KBD_C),
            'KBD immutable host/dependency/critical inventory mismatch')
    for path, pin in dict(KBD_DEPENDENCY_PINS, **KBD_HOST_PINS).items():
        expected = (pin['mode'], 'blob', pin['blob'])
        require(expected[:2] == ('100644', 'blob') and after.get(path) == expected
                and sha(raw_bytes(root, KBD_C, path)) == pin['sha256'], 'KBD immutable literal pin mismatch: ' + path)
        if path in KBD_HOSTS:
            require(path not in before, 'KBD host path not an original addition')
        else:
            require(all(_tree(root, revision).get(path) == expected for revision in (KBD_B, KBD_AUTHORITY, B, C)),
                    'KBD original/current literal dependency changed: ' + path)
    for path in metadata:
        require(before[path][:2] == after[path][:2] == ('100644', 'blob'), 'KBD metadata mode mismatch')
    return KBD_HOSTS

@original._proof_invocation
def authenticate_kbd_coexistence(root, head):
    """Only the five immutable Ckbd outputs may accompany unchanged014 inputs."""
    present = KBD_HOSTS & _tree(root, head).keys()
    live = {p for p in KBD_HOSTS if (root / p).exists() or (root / p).is_symlink()}
    indexed = {record.split('\t', 1)[1] for record in
               _git(root, 'ls-files', '--stage', '-z').decode().split('\0')
               if record and record.split('\t', 1)[1] in KBD_HOSTS}
    if not present and not live and not indexed:
        return frozenset()
    require(present == live == indexed == KBD_HOSTS and len(KBD_DEPENDENCY_PINS) == 28,
            'KBD incomplete exact host/dependency inventory')
    require(ancestor(root, KBD_C, head), 'KBD host files lack immutable candidate ancestry')
    pins = dict(KBD_DEPENDENCY_PINS, **KBD_HOST_PINS)
    for path, pin in pins.items():
        expected = (pin['mode'], 'blob', pin['blob'])
        require(pin['mode'] == '100644' and _tree(root, head).get(path) == expected,
                'KBD committed mode/blob substitution: ' + path)
        require(_tree(root, KBD_C).get(path) == expected
                and sha(raw_bytes(root, KBD_C, path)) == pin['sha256'],
                'KBD immutable source/host pin mismatch: ' + path)
        if path in KBD_DEPENDENCY_PINS:
            require(_tree(root, KBD_B).get(path) == expected
                    and _tree(root, KBD_AUTHORITY).get(path) == expected,
                    'KBD historical dependency authority mismatch: ' + path)
        data = current_bytes(root, path)
        require(sha(data) == pin['sha256'] and _git(root, 'show', ':' + path) == data,
                'KBD live/index dependency/host substitution: ' + path)
        require(_git(root, 'ls-files', '--stage', '--', path).decode().split()[:3]
                == [pin['mode'], pin['blob'], '0'], 'KBD index mode/blob substitution: ' + path)
    return KBD_HOSTS

def authenticate_host_overlays(root, head):
    present = HOST_OVERLAYS & _tree(root, head).keys()
    # Old baseline tools are allowed only at their exact immutable B blobs.
    adopted = any(_tree(root, head).get(p) != _tree(root, B).get(p) for p in present)
    if not adopted:
        return frozenset()
    require(set(HOST_OVERLAY_BLOBS) == HOST_OVERLAYS and present == HOST_OVERLAYS, '034 incomplete finite host overlay inventory')
    for path, pin in HOST_OVERLAY_BLOBS.items():
        require(_tree(root, head).get(path) == (pin['mode'], 'blob', pin['blob']), '034 committed host overlay differs from reviewed literal: ' + path)
        require(sha(raw_bytes(root, head, path)) == pin['sha256'] and sha(current_bytes(root, path)) == pin['sha256']
                and _git(root, 'show', ':' + path) == current_bytes(root, path), '034 host overlay live/index substitution: ' + path)
    return frozenset(present)

def verify_historical_dependency(root, path, expected_blob, expected_sha256):
    root = Path(root).resolve(); old = raw_bytes(root, B, path)
    require(_tree(root, B)[path] == ('100644', 'blob', expected_blob)
            and sha(old) == expected_sha256, '014 historical dependency pin mismatch: ' + path)
    proof = authenticate(root)
    require(path in HOST_OVERLAYS and path in proof['host_overlay_paths'], 'unadopted034 host overlay: ' + path)
    current = current_bytes(root, path)
    require(current == raw_bytes(root, proof['target'], path)
            and _git(root, 'show', ':' + path) == current, '034 host overlay is not committed/index/live exact')
    return old


def _config019_record_pins(pins):
    return [dict(path=path, **pin) for path, pin in pins.items()]


def _config019_checker_tables(raw):
    # Read literal evidence tables without executing the historical checker.
    tables = {}
    for node in ast.parse(raw.decode()).body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id in ('SOURCE_SHA256', 'FRAGMENT_SHA256'):
                    require(target.id not in tables, '019 duplicate historical literal table')
                    tables[target.id] = ast.literal_eval(node.value)
    return tables


@original._proof_invocation
def authenticate_config019_contract(root):
    """Immutable source/authority proof; this does not authenticate a dirty overlay."""
    root = Path(root).resolve()
    require(_git(root, 'rev-list', '--parents', '-n', '1', CONFIG019_C).decode().split()
            == [CONFIG019_C, CONFIG019_B]
            and _git(root, 'rev-parse', CONFIG019_C + '^{tree}').decode().strip() == CONFIG019_TREE
            and sha(_git(root, 'diff-tree', '-r', '--no-renames', '--raw', '-z',
                         CONFIG019_B, CONFIG019_C)) == CONFIG019_RAW,
            '019 immutable candidate parent/tree/raw inventory mismatch')
    before, after = _tree(root, CONFIG019_B), _tree(root, CONFIG019_C)
    require({p for p in before.keys() | after.keys() if before.get(p) != after.get(p)}
            == CONFIG019_HOSTS and len(CONFIG019_HOSTS) == 5
            and len(CONFIG019_DEPENDENCY_PINS) == 32 and len(CONFIG019_CURRENT_SOURCE_PINS) == 34,
            '019 immutable finite inventory mismatch')
    require(len(critical_tree(root, CONFIG019_B)) == 234
            and critical_tree(root, CONFIG019_B) == critical_tree(root, CONFIG019_C)
            and ancestor(root, CONFIG019_B, B) and not ancestor(root, B, CONFIG019_C),
            '019 immutable critical source/sidebranch mismatch')
    for path, pin in CONFIG019_HOST_PINS.items():
        require(path not in before and pin['mode'] == '100644'
                and after.get(path) == (pin['mode'], 'blob', pin['blob'])
                and sha(raw_bytes(root, CONFIG019_C, path)) == pin['sha256'],
                '019 immutable host mode/blob/digest mismatch: ' + path)
    for path, pin in CONFIG019_DEPENDENCY_PINS.items():
        expected = (pin['mode'], 'blob', pin['blob'])
        require(pin['mode'] == '100644' and before.get(path) == after.get(path) == expected
                and sha(raw_bytes(root, CONFIG019_C, path)) == pin['sha256'],
                '019 immutable historical dependency mismatch: ' + path)
    for path, pin in CONFIG019_CURRENT_SOURCE_PINS.items():
        require(pin['mode'] == '100644'
                and _tree(root, CONFIG019_F020).get(path) == (pin['mode'], 'blob', pin['blob'])
                and sha(raw_bytes(root, CONFIG019_F020, path)) == pin['sha256'],
                '019 current source differs from exact acceptedF020: ' + path)
    fixture = json.loads(raw_bytes(root, CONFIG019_C,
        'docs/calibration/fixtures/gp_config_019_usb_name_selection_characterization.json'), object_pairs_hook=unique)
    tables = _config019_checker_tables(raw_bytes(root, CONFIG019_C, CONFIG019_CHECKER))
    require(fixture['base_configurator_sha'] == CONFIG019_B
            and fixture['production_sources'] == _config019_record_pins(CONFIG019_DEPENDENCY_PINS)
            and tables['SOURCE_SHA256'] == {p: v['sha256'] for p, v in CONFIG019_DEPENDENCY_PINS.items()}
            and tables['FRAGMENT_SHA256'] == CONFIG019_FRAGMENT_PINS
            and len(CONFIG019_FRAGMENT_PINS) == 12 and len(fixture['expected_rows']) == 18,
            '019 immutable source/fragment/observation table mismatch')
    require({p for p in CONFIG019_DEPENDENCY_PINS
             if CONFIG019_DEPENDENCY_PINS[p] != CONFIG019_CURRENT_SOURCE_PINS[p]}
            == {'HAL/pico/src/comms/ConfiguratorBackend.cpp'}
            and set(CONFIG019_CURRENT_SOURCE_PINS) - set(CONFIG019_DEPENDENCY_PINS)
            == {'include/core/config_button_validation.hpp', 'src/core/config_button_validation.cpp'},
            '019 current inventory changed outside accepted validator consequence')
    backend = 'HAL/pico/src/comms/ConfiguratorBackend.cpp'
    accepted = raw_bytes(root, CONFIG019_F020, backend)
    require(accepted.count(original.INSERT_INCLUDE) == accepted.count(original.INSERT_BODY) == 1
            and accepted.replace(original.INSERT_INCLUDE, b'', 1).replace(original.INSERT_BODY, b'', 1)
            == raw_bytes(root, CONFIG019_C, backend), '019 accepted backend delta is not exact validator guard')
    for path, pin in CONFIG019_AUTHORITY_PINS.items():
        require(_tree(root, CONFIG019_RECEIPT_COMMIT).get(path) == (pin['mode'], 'blob', pin['blob'])
                and pin['mode'] == '100644'
                and sha(raw_bytes(root, CONFIG019_RECEIPT_COMMIT, path)) == pin['sha256'],
                '041 immutable authorization substitution: ' + path)
    require(_git(root, 'rev-list', '--parents', '-n', '1', CONFIG019_RECEIPT_COMMIT).decode().split()
            == [CONFIG019_RECEIPT_COMMIT, CONFIG019_RECEIPT_PARENT]
            and ancestor(root, CONFIG019_OPENING, CONFIG019_RECEIPT_PARENT)
            and _git(root, 'rev-list', '--parents', '-n', '1', CONFIG019_ADOPTION).decode().split()
            == [CONFIG019_ADOPTION, CONFIG019_RECEIPT_COMMIT]
            and sha(raw_bytes(root, CONFIG019_ADOPTION, QUEUE)) == CONFIG019_ADOPTION_QUEUE_SHA256,
            '041 opening/receipt/adoption chronology or authority mismatch')
    receipt = json.loads(raw_bytes(root, CONFIG019_RECEIPT_COMMIT, CONFIG019_RECEIPT), object_pairs_hook=unique)
    require(receipt['opening_reference'] == 'git-json:' + CONFIG019_OPENING + ':' + QUEUE + '#queue-state'
            and receipt['resolver_role'] == 'Glyph Work-Order Curator'
            and [(x['subject_id'], x['event_kind'], x['disposition']) for x in receipt['subject_resolutions']]
            == [('GP-VAL-041', 'INVALIDATED_PREAUTHORIZED', 'REAUTHORIZED')]
            and item(root, CONFIG019_ADOPTION, 'GP-VAL-041')['status'] == 'READY'
            and item(root, CONFIG019_ADOPTION, 'GP-CONFIG-019')['candidate_git_sha'] == CONFIG019_C,
            '041 adopted finite order mismatch')
    contract = raw_bytes(root, CONFIG019_RECEIPT_COMMIT, CONFIG019_CONTRACT).decode()
    literal_hosts = json.loads(contract.split('```json\n')[1].split('\n```')[0], object_pairs_hook=unique)
    require(literal_hosts == _config019_record_pins(CONFIG019_HOST_PINS)
            and all(value in contract for value in (CONFIG019_C, CONFIG019_B, CONFIG019_TREE, CONFIG019_RAW,
                                                    CONFIG019_ACCEPTANCE_SHA256, CONFIG019_F020)),
            '019 literals differ from immutable Curator contract')
    return CONFIG019_HOSTS


def _config019_current_pins(root, head, pins):
    """Fresh committed/index/live bytes, types and flags for a finite inventory."""
    index = {}
    for record in filter(None, _git(root, 'ls-files', '--stage', '-z').decode().split('\0')):
        meta, path = record.split('\t'); mode, blob, stage = meta.split()
        require(path not in index, '019 duplicate/unmerged index entry: ' + path)
        index[path] = (mode, blob, stage)
    tags = {r[2:]: r[0] for r in filter(None, _git(root, 'ls-files', '-v', '-z').decode().split('\0'))}
    committed = _tree(root, head)
    for path, pin in pins.items():
        require(pin['mode'] == '100644' and committed.get(path) == ('100644', 'blob', pin['blob'])
                and index.get(path) == ('100644', pin['blob'], '0'),
                '019 committed/index mode/blob substitution: ' + path)
        require(path in tags and not tags[path].islower() and tags[path] != 'S',
                '019 assume-unchanged/skip-worktree proof trap: ' + path)
        data = current_bytes(root, path)
        require(sha(data) == pin['sha256'] and data == raw_bytes(root, head, path),
                '019 committed/live digest substitution: ' + path)


@original._proof_invocation
def authenticate_config019_coexistence(root, head):
    """Only the adopted019 inventory and separately pinned current proof enter014."""
    root = Path(root).resolve(); tree = _tree(root, head)
    present = (CONFIG019_HOSTS | CONFIG019_OVERLAY_PATHS) & tree.keys()
    live = {p for p in CONFIG019_HOSTS | CONFIG019_OVERLAY_PATHS if (root / p).exists() or (root / p).is_symlink()}
    adopted = CONFIG019_ADOPTION in _git(root, 'rev-list', head).decode().split()
    introduced = (bool(_git(root, 'log', '--format=%H', CONFIG019_ADOPTION + '..' + head, '--',
                            *sorted(CONFIG019_OVERLAY_PATHS)).strip()) if adopted else False)
    # Earlier034 contexts are still valid without optional future041 objects or
    # authority. Once introduced, deleting every overlay cannot restore that route.
    if not present and not live and not introduced:
        return frozenset()
    authenticate_config019_contract(root)
    require(adopted, '019 current proof lacks adopted041 authority ancestry')
    require(set(CONFIG019_OVERLAY_PINS) == CONFIG019_OVERLAY_PATHS,
            '041 incomplete exact current overlay pins')
    current_pins = dict(CONFIG019_AUTHORITY_PINS, **CONFIG019_CURRENT_SOURCE_PINS, **CONFIG019_OVERLAY_PINS)
    # VAL045 is authorized to extend this checker while its historical fixture,
    # host, and source pins remain immutable. The outer exact path envelope and
    # committed/index/live checks authenticate the updated checker bytes.
    if has_c024_campaign(root):
        current_pins.pop(CONFIG019_CHECKER, None)
    _config019_current_pins(root, head, current_pins)
    original_hosts = CONFIG019_ORIGINAL_HOSTS & tree.keys()
    original_live = live & CONFIG019_ORIGINAL_HOSTS
    integrated = ancestor(root, CONFIG019_C, head)
    if original_hosts or original_live or integrated:
        require(integrated and original_hosts == original_live == CONFIG019_ORIGINAL_HOSTS,
                '019 incomplete original host inventory or missing immutable candidate ancestry')
        _config019_current_pins(root, head, {p: CONFIG019_HOST_PINS[p] for p in CONFIG019_ORIGINAL_HOSTS})
    overlay_path = 'docs/runtime_config/fixtures/gp_val041_usb_name_current_acceptance.json'
    record = json.loads(current_bytes(root, overlay_path), object_pairs_hook=unique)
    fixture = json.loads(raw_bytes(root, CONFIG019_C,
        'docs/calibration/fixtures/gp_config_019_usb_name_selection_characterization.json'), object_pairs_hook=unique)
    require(record['schema_name'] == 'glyph_gp_val041_usb_name_current_acceptance'
            and type(record['schema_version']) is int and record['schema_version'] == 1
            and (record['original_candidate'], record['original_base'], record['original_tree'], record['original_raw_inventory_sha256'])
            == (CONFIG019_C, CONFIG019_B, CONFIG019_TREE, CONFIG019_RAW)
            and record['accepted_source_f020'] == CONFIG019_F020
            and record['original_host_pins'] == _config019_record_pins(CONFIG019_HOST_PINS)
            and record['historical_sources'] == _config019_record_pins(CONFIG019_DEPENDENCY_PINS)
            and record['historical_fragments'] == CONFIG019_FRAGMENT_PINS
            and record['historical_expected_rows'] == fixture['expected_rows']
            and record['current_sources'] == _config019_record_pins(CONFIG019_CURRENT_SOURCE_PINS)
            and {k for k in CONFIG019_FRAGMENT_PINS if record['current_fragments'][k] != CONFIG019_FRAGMENT_PINS[k]}
                == {'acceptance'}
            and set(record['current_fragments']) == set(CONFIG019_FRAGMENT_PINS)
            and record['current_fragments']['acceptance'] == CONFIG019_ACCEPTANCE_SHA256,
            '041 current/historical proof content substitution')
    manifest_path = 'docs/runtime_config/fixtures/runtime_config_validation_manifest.json'
    manifest_raw = current_bytes(root, manifest_path)
    require(manifest_raw == raw_bytes(root, head, manifest_path)
            and _git(root, 'show', ':' + manifest_path) == manifest_raw,
            '041 manifest committed/index/live substitution')
    manifest = json.loads(manifest_raw, object_pairs_hook=unique)
    entries = [entry for entry in manifest['entries'] if entry['id'] == 'gp_config019_usb_name_selection']
    require(len(entries) == 1 and sha(json.dumps(entries[0], sort_keys=True, separators=(',', ':')).encode())
            == CONFIG019_MANIFEST_ENTRY_SHA256, '041 exact authenticated019 manifest entry mismatch')
    return CONFIG019_HOSTS if integrated else frozenset()


# Preserve the original014 callable and its closed constants for historical
# snapshots. The exact035 marker selects the separately authorized extension.
authenticate_014_original = authenticate
authenticate_config019_coexistence_014_original = authenticate_config019_coexistence

# GP-VAL-045 binds the separately reviewed GP-CONFIG-024 source candidate.
# C remains a preserved direct child of B; this route never merges it into the
# canonical source tree and never treats its host proof as hardware acceptance.
C024_C = '8ab1173b0690f5ed3e994f95af797c9e9a265525'
C024_B = 'b404453ef22cc994eec54338b8a23c3ba61df808'
C024_TREE = '15ed2d35d561d6b1709499fe42083ca4d789e920'
C024_HANDOFF = '4bfb3777a4f484f091f0d8054230e3eb9ac3dee2'
C024_PROOF = 'docs/calibration/fixtures/gp_config_024_usb_profile_identity_repair.json'
C024_MENU = 'HAL/pico/src/display/DefaultConfigMenu.cpp'
C024_CANDIDATE_PATHS = frozenset((
    C024_MENU,
    'tools/check_glyph_gp_config024_usb_profile_identity.py',
    'tools/fixtures/gp_config024_usb_profile_identity/main.cpp',
    'tools/fixtures/gp_config024_usb_profile_identity/include/host_stubs.hpp',
    'docs/calibration/gp_config_024_usb_profile_identity_repair.md',
    C024_PROOF,
    'docs/runtime_config/fixtures/runtime_config_validation_manifest.json',
    'docs/runtime_config/fixtures/glyph_checker_census.json',
    'docs/runtime_config/fixtures/runtime_config_validation_health.json',
    'docs/runtime_config/runtime_config_validation_health.md',
    C024_TRANSITIONS,
))
C024_HARDWARE_HANDOFF_PATHS = frozenset((
    'docs/agent_framework/GP_CONFIG_024_HARDWARE_PROTOCOL.md',
    'docs/calibration/gp_config_024_hardware_result.md',
    'docs/calibration/fixtures/gp_config_024_hardware_evidence.json',
))
VAL045_PATHS = frozenset((
    'tools/glyph_c014_campaign_transition.py',
    'tools/glyph_campaign_transition.py',
    'tools/test_glyph_c014_campaign_transition.py',
    'tools/check_glyph_gp_config012_button_mask_characterization.py',
    'tools/check_glyph_gp_config019_usb_name_selection.py',
    'tools/check_glyph_gp_kbd_001_keyboard_pipeline.py',
    'docs/runtime_config/gp_val045_usb_identity_correspondence.md',
    'docs/runtime_config/fixtures/gp_val045_usb_identity_correspondence.json',
    'docs/AGENT_CONTEXT.md', 'docs/CURRENT_STATE.md', 'docs/ROADMAP.md',
    'docs/project/ACTIVE_AGENT_QUEUE.md',
    'docs/runtime_config/fixtures/runtime_config_validation_manifest.json',
    'docs/runtime_config/fixtures/glyph_checker_census.json',
    'docs/runtime_config/fixtures/runtime_config_validation_health.json',
    'docs/runtime_config/runtime_config_validation_health.md',
    C024_TRANSITIONS,
))


def validate_val045_handoff_state(current_c024, current_045):
    """Gate preserved C024 activation on strict VAL045 completion."""
    require(current_c024.get('candidate_git_sha') == C024_C
            and current_c024.get('candidate_base_configurator_sha') == C024_B,
            'VAL045 C024 handoff candidate identity changed')
    require(current_c024.get('status') == 'PREAUTHORIZED'
            and current_045.get('activation_requires_new_judgment') is False,
            'VAL045 handoff authorization state changed')
    if current_045.get('status') == 'DONE':
        require(current_045.get('activation_state') == 'NOT_APPLICABLE',
                'strict VAL045 DONE must be source-free and complete')
        if current_c024.get('activation_state') == 'ACTIVATABLE':
            require(current_c024.get('hardware_evidence_dependency_satisfied') is True,
                    'newly activated C024 must have its dependencies satisfied')
        elif current_c024.get('activation_state') == 'HARDWARE_PENDING':
            expected_candidate = C024_C
            expected_artifact = '95de108f23b0d7219caa38a1f85c4dec1691f087061b29787d07b83dab0ba0e6'
            expected_locator = (
                'local_backups/hardware-artifacts/' + expected_candidate + '/'
                + expected_artifact + '/firmware.uf2')
            require(current_c024.get('hardware_evidence_dependency_satisfied') is False
                    and current_c024.get('firmware_artifact_build_path') == '.pio/build/glyph_mk6/firmware.uf2'
                    and current_c024.get('firmware_artifact_sha256') == expected_artifact
                    and current_c024.get('preserved_firmware_artifact_locator') == expected_locator
                    and current_c024.get('hardware_result') is None,
                    'C024 hardware wait must retain exact reviewed candidate and artifact')
        else:
            require(False, 'strict VAL045 DONE must activate or advance exact preserved C024')
    else:
        require(current_045.get('status') == 'PREAUTHORIZED'
                and current_045.get('activation_state') == 'ACTIVATABLE'
                and current_c024.get('activation_state') == 'WAITING',
                'C024 cannot activate before strict VAL045 DONE')

C024_HANDOFF_FIXTURE = 'docs/runtime_config/fixtures/gp_val045_usb_identity_correspondence.json'
C024_C019_ACCEPTED_EXTRA = {
    'HAL/pico/include/core/Persistence.hpp': {
        'sha256': 'eb842dd491ccb8620e76a90d664e296824b84a6294927fc87b136916fc8070e8',
        'accepted_commit': '55e2da3d264dcdb89c6d80fae8bab5629a5a662b',
    },
}
C024_ACCEPTED_PREDECESSOR_COMMITS = (
    'd786c244183343f89287a040055b7eaeae1e41f3', # C014
    '3fb0af34ba945641ba8c8be432ea4533f3abee2a', # C017
    '55e2da3d264dcdb89c6d80fae8bab5629a5a662b', # C021
    '292f27cf88a9e814b1086bd544378b7e733e25e3', # C022
    '03bbf5da14a7d450f2986b12ad69ec6b3f704bad', # C023 source validation
    'e44ec59c57c0db194381f8d2dddce08aab81b5f6', # C023
)
VAL045_FIXTURE_PATH = 'docs/runtime_config/fixtures/gp_val045_usb_identity_correspondence.json'


def has_c024_campaign(root: Path) -> bool:
    """Select only the exact adopted C024 handoff record, never a prefix."""
    root = Path(root).resolve()
    head = original._git(root, 'rev-parse', 'HEAD').decode().strip()
    tree = original._tree(root, head)
    return C024_HANDOFF_FIXTURE in tree and C024_HANDOFF_FIXTURE in VAL045_PATHS


def authenticate_c024_phase(root: Path, head: str | None = None) -> dict:
    """Authenticate source-free handoff or exact C024 source phase."""
    root = Path(root).resolve()
    head = head or original._git(root, 'rev-parse', 'HEAD').decode().strip()
    require = original.require
    get = original._git
    tree = original._tree(root, head)
    require(original.ancestor(root, C024_B, head), 'VAL045 target lacks exact C024 base ancestry')
    require(get(root, 'rev-list', '--parents', '-n', '1', C024_C).decode().split() == [C024_C, C024_B],
            'VAL045 C024 candidate parent changed')
    require(get(root, 'rev-parse', C024_C + '^{tree}').decode().strip() == C024_TREE,
            'VAL045 C024 candidate tree changed')
    require(get(root, 'rev-parse', C024_HANDOFF + '^{tree}').decode().strip() != '',
            'VAL045 handoff commit is unavailable')
    require(original.ancestor(root, C024_HANDOFF, head) or original.ancestor(root, C024_C, head),
            'VAL045 target is outside reviewed handoff/source candidate lineage')

    # The exact C24 candidate remains the adopted ten-path direct child of B.
    candidate_paths = set(filter(None, get(root, 'diff', '--no-renames', '--name-only', '-z', C024_B, C024_C).decode().split('\0')))
    require(candidate_paths == C024_CANDIDATE_PATHS, 'VAL045 C024 path envelope changed')
    source_fixture = json.loads(original.raw_bytes(root, C024_C, C024_PROOF), object_pairs_hook=unique)
    require(source_fixture['schema_name'] == 'glyph_gp_config024_usb_profile_identity_repair'
            and source_fixture['base_configurator_sha'] == C024_B
            and source_fixture['firmware_build'] == 'NOT_RUN'
            and source_fixture['hardware_acceptance'] == 'NOT_CLAIMED',
            'VAL045 C024 candidate proof fixture identity/limitations changed')
    authenticate_kbd_contract(root)
    authenticate_config019_contract(root)
    hashes = {row['path']: row['sha256'] for row in source_fixture['candidate_file_hashes']}
    require(set(hashes) == C024_CANDIDATE_PATHS - {C024_PROOF},
            'VAL045 C024 proof-file inventory changed')
    for path in C024_CANDIDATE_PATHS:
        b_entry = original._tree(root, C024_B).get(path)
        c_entry = original._tree(root, C024_C).get(path)
        require(c_entry is not None and c_entry[:2] == ('100644', 'blob'),
                'VAL045 C024 candidate mode/type changed: ' + path)
        if path in hashes:
            require(hashlib.sha256(original.raw_bytes(root, C024_C, path)).hexdigest() == hashes[path],
                    'VAL045 C024 proof-file digest changed: ' + path)
        if path == C024_MENU:
            require(b_entry is not None and b_entry[:2] == ('100644', 'blob')
                    and b_entry[2] != c_entry[2], 'VAL045 selector source delta missing')
        else:
            # Proof metadata may be new at C; the exact candidate file digest
            # above and direct reviewed commit bind it.
            pass

    # Authenticate every allowed accepted-predecessor path from fresh B.
    for row in source_fixture['authorized_predecessor_deltas']:
        path = row['path']
        require(hashlib.sha256(original.raw_bytes(root, C024_B, path)).hexdigest() == row['fresh_B_sha256'],
                'VAL045 accepted predecessor fresh-B digest changed: ' + path)
        commits = row['accepted_predecessor_commits']
        require(commits and all(original.ancestor(root, commit, C024_B) for commit in commits),
                'VAL045 accepted predecessor ancestry missing: ' + path)
        for commit in commits:
            parents = get(root, 'rev-list', '--parents', '-n', '1', commit).decode().split()
            require(len(parents) >= 2 and path in set(filter(None, get(root, 'diff', '--no-renames', '--name-only', '-z',
                        parents[1], commit, '--').decode().split('\0'))),
                    'VAL045 accepted predecessor does not change its named path: ' + path)

    handoff = json.loads(original.current_bytes(root, C024_HANDOFF_FIXTURE), object_pairs_hook=unique)
    require(handoff['schema_name'] == 'glyph_gp_val045_c024_candidate_activation'
            and handoff['candidate_git_sha'] == C024_C
            and handoff['candidate_tree'] == C024_TREE
            and handoff['candidate_base_configurator_sha'] == C024_B
            and handoff['candidate_branch'] == 'codex/gp-config-024-usb-profile-identity'
            and handoff['live_remote_verified'] is True
            and handoff['independent_source_review']['result'] == 'PASS'
            and handoff['independent_source_review']['review_sha256'] ==
                'b6645bbc5b2101394f0991e58577c6ff09b2ea5fca2237666470f3116c2abf21'
            and handoff['independent_source_applicability_review']['result'] == 'PASS'
            and handoff['independent_build_role_review']['result'] == 'PASS'
            and handoff['accepted_c019_source_lineage'] == [
                {'path': path, 'fresh_B_sha256': pin['sha256'], 'accepted_commit': pin['accepted_commit']}
                for path, pin in C024_C019_ACCEPTED_EXTRA.items()],
            'VAL045 reviewed C024 activation record changed')
    prior_c023 = original.item(root, C024_B, 'GP-CONFIG-023')
    prior_042 = original.item(root, C024_B, 'GP-VAL-042')
    require(prior_c023['status'] == prior_042['status'] == 'DONE'
            and prior_c023['hardware_result'] == 'PASS'
            and prior_c023['hardware_evidence_gaps'] == []
            and prior_c023['candidate_git_sha'] == '36bf0f314afe19fc8fcbf4caf97b5bf5f83dac39'
            and prior_c023['firmware_artifact_sha256'] ==
                '7e8833e5a83d1656e51f9ca258de78e7808eda2a6f3da918759a1553575f1224',
            'VAL045 exact accepted C023/042 predecessor state changed')
    current_c024 = original.item(root, head, 'GP-CONFIG-024')
    current_045 = original.item(root, head, 'GP-VAL-045')
    processor = None
    integrated = original.ancestor(root, C024_F, head)
    if integrated:
        # Authenticate the source-free processor at P, then admit only the exact P/F merge.
        revisions = get(root, 'rev-list', '--reverse', '--topo-order', C024_P + '..' + head).decode().split()
        merges = [revision for revision in revisions
                  if get(root, 'rev-list', '--parents', '-n', '1', revision).decode().split()[1:]
                  == [C024_P, C024_F]]
        require(len(merges) == 1, 'C024 history must contain one exact P/F integration')
        integration = merges[0]
        require(original.ancestor(root, integration, head), 'C024 exact integration is not in target ancestry')
        post_integration = get(root, 'rev-list', '--first-parent', '--reverse', integration + '..' + head).decode().split()
        post_i_validation_paths = C024_PROCESSOR_PATHS | frozenset((
            'tools/fixtures/gp_config019_usb_name_selection/include/host_stubs.hpp',
            'tools/fixtures/gp_config019_usb_name_selection/current_acceptance.cpp',
            C024_TRANSITIONS))
        for revision in post_integration:
            changed_since_i = set(filter(None, get(root, 'diff', '--name-only', '--no-renames', '-z',
                                                    integration, revision).decode().split('\0')))
            require(changed_since_i <= post_i_validation_paths,
                    'C024 post-integration change outside validation/evidence paths')
        accepted = original.item(root, C024_P, 'GP-CONFIG-024')
        integrated_expected = dict(original.critical_tree(root, C024_P))
        integrated_expected[C024_MENU] = original.critical_tree(root, C024_F)[C024_MENU]
        processor = authenticate_c024_processor(root, C024_P, accepted,
                                                original.item(root, C024_P, 'GP-VAL-045'), verify_live=False)
        completion_fields = {'status', 'done_evidence'}
        require({k:v for k,v in current_c024.items() if k not in completion_fields}
                == {k:v for k,v in accepted.items() if k not in completion_fields}
                and current_c024['status'] in {'HARDWARE_VALIDATED', 'DONE'},
                'C024 integration changed exact accepted hardware tuple')
        prior_catalog = json.loads(original.raw_bytes(root, C024_P, C024_TRANSITIONS), object_pairs_hook=unique)
        require(set(prior_catalog) == {'schema_version', 'accepted_transitions'}
                and prior_catalog['schema_version'] == 1,
                'C024 predecessor accepted catalog schema changed')
        prior_records = prior_catalog['accepted_transitions']
        expected_record = {
            'work_order': 'GP-CONFIG-024', 'candidate': C024_F, 'build': C024_F,
            'parent': C024_B, 'tree': C024_TREE, 'review_commit': C024_R,
            'evidence_commit': processor, 'integration': integration,
        }
        catalog_commit = None
        done_commit = None
        done_seen = False
        from check_glyph_agent_framework_docs import validate_completion_evidence
        for revision in post_integration:
            revision_tree = original._tree(root, revision)
            catalog = json.loads(original.raw_bytes(root, revision, C024_TRANSITIONS), object_pairs_hook=unique)
            require(set(catalog) == {'schema_version', 'accepted_transitions'}
                    and catalog['schema_version'] == 1
                    and catalog['accepted_transitions'][:len(prior_records)] == prior_records
                    and len(catalog['accepted_transitions']) in (len(prior_records), len(prior_records) + 1),
                    'C024 accepted catalog lost/replaced a predecessor or added extra rows')
            added = catalog['accepted_transitions'][len(prior_records):]
            require(not added or added == [expected_record], 'C024 accepted catalog tuple substitution')
            row = original.item(root, revision, 'GP-CONFIG-024')
            if added and catalog_commit is None:
                catalog_commit = revision
                parent = get(root, 'rev-list', '--parents', '-n', '1', revision).decode().split()
                changed_in_catalog = set(filter(None, get(root, 'diff', '--name-only', '--no-renames', '-z',
                                                         parent[1], revision).decode().split('\0')))
                require(changed_in_catalog == {C024_TRANSITIONS}
                        and row['status'] == 'HARDWARE_VALIDATED',
                        'C024 catalog must be a separate source-free-status publication')
            elif catalog_commit is not None:
                require(added == [expected_record],
                        'C024 accepted catalog removed or changed after publication')
            else:
                require(not added, 'C024 catalog row appeared without publication transition')
            if row['status'] == 'DONE':
                require(catalog_commit is not None and not done_seen
                        and revision != catalog_commit,
                        'C024 strict DONE must follow a separate accepted catalog commit')
                parents = get(root, 'rev-list', '--parents', '-n', '1', revision).decode().split()
                require(len(parents) == 2 and parents[1] == catalog_commit,
                        'C024 strict DONE must be a separate direct child of catalog publication')
                queue = parsed_queue(original.raw_bytes(root, revision, QUEUE))
                validate_completion_evidence(row, row['done_evidence'],
                    policy=queue['completion_correspondence'], publication_sha=revision, repo_root=root)
                done_commit = revision
                done_seen = True
            else:
                require(not done_seen and row['status'] == 'HARDWARE_VALIDATED',
                        'C024 status regressed or changed before strict DONE')
            require(original.critical_tree(root, revision) == integrated_expected,
                    'C024 accepted lifecycle changed integrated firmware source')
            for path, payload in ((C024_EVIDENCE, processor_payload := original.raw_bytes(root, processor, C024_EVIDENCE)),
                                  (C024_RESULT, original.raw_bytes(root, processor, C024_RESULT)),
                                  (C024_ARCHIVE, original.raw_bytes(root, processor, C024_ARCHIVE)),
                                  (C024_PROTOCOL, original.raw_bytes(root, processor, C024_PROTOCOL))):
                require(original.raw_bytes(root, revision, path) == payload,
                        'C024 accepted lifecycle replaced immutable HEP input: ' + path)
        if catalog_commit:
            require(original.ancestor(root, catalog_commit, head), 'C024 catalog commit missing from target ancestry')
        require((current_c024['status'] == 'DONE') == (done_commit is not None),
                'C024 current DONE status/history mismatch')
    elif current_c024.get('status') == 'HARDWARE_VALIDATED' or current_c024.get('hardware_result') is not None:
        processor = authenticate_c024_processor(root, head, current_c024, current_045)
    else:
        validate_val045_handoff_state(current_c024, current_045)

    # Keep the original019 observations and041 current-admission record exact.
    # The six named accepted predecessor deltas are validated below against B;
    # this block authenticates the immutable C019 objects and its unchanged
    # source-free Config-acceptance fixture without relabeling old expectations.
    base_tree = original._tree(root, C024_B)
    mutable_current_checker = 'tools/check_glyph_gp_config019_usb_name_selection.py'
    for path, pin in dict(CONFIG019_HOST_PINS, **CONFIG019_AUTHORITY_PINS,
                          **CONFIG019_OVERLAY_PINS).items():
        if path == mutable_current_checker:
            # VAL045 adds a separately authenticated current route to this
            # checker; authenticate its original historical tables below.
            continue
        expected = (pin['mode'], 'blob', pin['blob'])
        require(pin['mode'] == '100644' and base_tree.get(path) == expected
                and hashlib.sha256(original.raw_bytes(root, C024_B, path)).hexdigest() == pin['sha256'],
                'VAL045 immutable019/current overlay pin changed: ' + path)
    accepted_delta_paths = {row['path'] for row in source_fixture['authorized_predecessor_deltas']}
    predecessor_commits = C024_ACCEPTED_PREDECESSOR_COMMITS
    fixture_commits = {commit for row in source_fixture['authorized_predecessor_deltas']
                       for commit in row['accepted_predecessor_commits']}
    fixture_commits.update(pin['accepted_commit'] for pin in C024_C019_ACCEPTED_EXTRA.values())
    require(fixture_commits <= set(predecessor_commits),
            'VAL045 predecessor fixture names an unadopted integration commit')
    accepted_predecessor_sources = {}
    accepted_B_tree = original.critical_tree(root, C024_B)
    historical_tree = original.critical_tree(root, CONFIG019_F020)
    for path in sorted(set(accepted_B_tree) | set(historical_tree)):
        if accepted_B_tree.get(path) == historical_tree.get(path):
            continue
        matches = []
        for commit in predecessor_commits:
            commit_tree = original._tree(root, commit)
            parents = get(root, 'rev-list', '--parents', '-n', '1', commit).decode().split()
            require(len(parents) >= 2 and original.ancestor(root, commit, C024_B),
                    'VAL045 accepted predecessor commit ancestry changed: ' + commit)
            first_parent_tree = original._tree(root, parents[1])
            if (commit_tree.get(path) == accepted_B_tree.get(path)
                    and first_parent_tree.get(path) != commit_tree.get(path)):
                matches.append(commit)
        require(matches,
                'VAL045 critical-source drift is not an exact accepted predecessor: ' + path +
                ' F020=' + repr(historical_tree.get(path)) + ' B=' + repr(accepted_B_tree.get(path)))
        accepted_predecessor_sources[path] = matches[0]
        accepted_delta_paths.add(path)
    correspondence_rows = []
    for path, commit in sorted(accepted_predecessor_sources.items()):
        accepted_entry = original._tree(root, commit).get(path)
        base_entry = accepted_B_tree.get(path)
        historical_entry = historical_tree.get(path)
        require(accepted_entry is not None and accepted_entry == base_entry,
                'VAL045 accepted predecessor blob differs from fresh B: ' + path)
        correspondence_rows.append({
            'path': path,
            'accepted_commit': commit,
            'accepted_blob': accepted_entry[2],
            'accepted_sha256': hashlib.sha256(original.raw_bytes(root, commit, path)).hexdigest(),
            'fresh_B_blob': base_entry[2],
            'fresh_B_sha256': hashlib.sha256(original.raw_bytes(root, C024_B, path)).hexdigest(),
            'historical_F020_blob': historical_entry[2] if historical_entry else None,
        })
    val045_record = json.loads(original.current_bytes(root, VAL045_FIXTURE_PATH), object_pairs_hook=unique)
    require(val045_record.get('accepted_predecessor_source_correspondence') == correspondence_rows,
            'VAL045 persisted predecessor path/blob correspondence changed')
    for path, pin in C024_C019_ACCEPTED_EXTRA.items():
        commit = pin['accepted_commit']
        parents = get(root, 'rev-list', '--parents', '-n', '1', commit).decode().split()
        require(original.ancestor(root, commit, C024_B)
                and path in set(filter(None, get(root, 'diff', '--no-renames', '--name-only', '-z',
                    parents[1], commit, '--').decode().split('\0')))
                and hashlib.sha256(original.raw_bytes(root, C024_B, path)).hexdigest() == pin['sha256'],
                'VAL045 C019 extra accepted source lineage changed: ' + path)
        accepted_delta_paths.add(path)
    for path, pin in CONFIG019_CURRENT_SOURCE_PINS.items():
        if base_tree.get(path) != (pin['mode'], 'blob', pin['blob']):
            require(path in accepted_delta_paths,
                    'VAL045 C019 current source changed outside accepted predecessor rows: ' + path)
    manifest_path = 'docs/runtime_config/fixtures/runtime_config_validation_manifest.json'
    manifest_raw = original.current_bytes(root, manifest_path)
    manifest = json.loads(manifest_raw, object_pairs_hook=unique)
    base_manifest = json.loads(original.raw_bytes(root, C024_B, manifest_path), object_pairs_hook=unique)
    entries = [entry for entry in manifest['entries'] if entry['id'] == 'gp_config019_usb_name_selection']
    base_entries = [entry for entry in base_manifest['entries'] if entry['id'] == 'gp_config019_usb_name_selection']
    require(len(entries) == len(base_entries) == 1 and entries[0] == base_entries[0],
            'VAL045 current C019 manifest record changed')
    for path in CONFIG019_OVERLAY_PATHS:
        expected = base_tree.get(path)
        current = original.current_bytes(root, path)
        permitted_checker = path == CONFIG019_CHECKER and has_c024_campaign(root)
        require(expected is not None and expected[:2] == ('100644', 'blob')
                and (permitted_checker or current == original.raw_bytes(root, C024_B, path))
                and get(root, 'show', ':' + path) == current,
                'VAL045 immutable041 current proof changed: ' + path)

    source_base = original.critical_tree(root, C024_B)
    source_candidate = original.critical_tree(root, C024_C)
    delta = {path for path in source_base.keys() | source_candidate.keys()
             if source_base.get(path) != source_candidate.get(path)}
    require(delta == {C024_MENU}, 'VAL045 exact sole C024 critical source delta changed')
    current = original.critical_tree(root, head)
    if integrated and current == integrated_expected:
        phase = 'ACCEPTED_TRANSITION' if catalog_commit else 'CANDIDATE_VALIDATION_ONLY'
        critical = frozenset(set(accepted_predecessor_sources) | {C024_MENU})
        sources = {C024_MENU: C024_C}
    elif current == source_base:
        phase = 'SOURCE_FREE_PROCESSOR' if processor else 'SOURCE_FREE_CANDIDATE'
        critical = frozenset(accepted_predecessor_sources)
        sources = {}
        require(not original.ancestor(root, C024_C, head),
                'VAL045 source-free phase conceals C024 ancestry')
    elif current == source_candidate:
        phase = 'CANDIDATE_VALIDATION_ONLY'
        critical = frozenset(set(accepted_predecessor_sources) | {C024_MENU})
        sources = {C024_MENU: C024_C}
        require(original.ancestor(root, C024_C, head),
                'VAL045 candidate phase replays C024 source without ancestry')
    else:
        raise CorrespondenceError('VAL045 current critical tree is outside exact B/C024')

    changed = set(filter(None, get(root, 'diff', '--no-renames', '--name-only', '-z', C024_B, head).decode().split('\0')))
    allowed_target_paths = C024_CANDIDATE_PATHS | VAL045_PATHS | C024_HARDWARE_HANDOFF_PATHS | {C024_ARCHIVE, C024_TRANSITIONS}
    require(changed <= allowed_target_paths,
            'VAL045 target exceeds exact candidate/governance/hardware-handoff envelope: ' + repr(sorted(changed - allowed_target_paths)))
    for path in changed:
        entry = tree.get(path)
        require(entry is not None and entry[:2] == ('100644', 'blob'),
                'VAL045 changed path is not committed regular100644: ' + path)
        require(original.current_bytes(root, path) == original.raw_bytes(root, head, path)
                and get(root, 'show', ':' + path) == original.current_bytes(root, path),
                'VAL045 committed/index/live mismatch: ' + path)
    authorized_sources = accepted_delta_paths | {C024_MENU}
    source_candidates = {path: commit for path, commit in accepted_predecessor_sources.items()}
    source_candidates[C024_MENU] = C024_C
    return dict(phase=phase, contract='c024_selector_identity', candidate=C024_C,
                processor_evidence_commit=processor,
                base=C024_B, target=head, critical_paths=critical,
                source_candidates={**source_candidates, **sources},
                accepted_metadata_paths=(frozenset((C024_EVIDENCE, C024_RESULT, C024_ARCHIVE))
                                         if processor else frozenset()),
                authorized_source_paths=frozenset(authorized_sources),
                changed_paths=frozenset(changed))

@original._proof_invocation
def authenticate(root):
    if has_c024_campaign(Path(root)):
        return authenticate_c024_phase(Path(root))
    from glyph_c017_campaign_transition import present
    if present(Path(root)):
        from glyph_c017_campaign_transition import authenticate as neopixel
        return neopixel(root)
    return authenticate_014_original(root)

@original._proof_invocation
def authenticate_config019_coexistence(root, head):
    if has_c024_campaign(Path(root)):
        return authenticate_c024_phase(Path(root), head)
    from glyph_c017_campaign_transition import present
    if present(Path(root)):
        from glyph_c017_campaign_transition import verify019_overlay
        return verify019_overlay(root, head)
    return authenticate_config019_coexistence_014_original(root, head)


# Owner-directed C024 source-free evidence admission. This authenticates E only;
# a later tested-source I/catalog and strict DONE need their separate review.
C024_R = '36f91089ab60fb68248a2819aee5dd5082fd922c'
C024_P = '68cb0e8e7d6a0badcfaf894b188231c968d27c1d'
C024_F = '8ab1173b0690f5ed3e994f95af797c9e9a265525'
C024_EVIDENCE = 'docs/calibration/fixtures/gp_config_024_hardware_evidence.json'
C024_RESULT = 'docs/calibration/gp_config_024_hardware_result.md'
C024_PROTOCOL = 'docs/agent_framework/GP_CONFIG_024_HARDWARE_PROTOCOL.md'
C024_TRANSITIONS = 'docs/runtime_config/fixtures/gp_val042_accepted_transitions.json'
C024_ARCHIVE = 'docs/calibration/fixtures/gp_config_024_human_session_archive.json'
C024_ARCHIVE_SHA256 = '6b9979fe81876f37bbd00ff7b76c0a81bee940692aa73aeed52d7a2b9776312c'
C024_PROCESSOR_PATHS = frozenset((
    'docs/runtime_config/fixtures/glyph_checker_census.json',
    'docs/runtime_config/fixtures/runtime_config_validation_health.json',
    C024_EVIDENCE, C024_RESULT, C024_ARCHIVE,
    'docs/AGENT_CONTEXT.md', 'docs/CURRENT_STATE.md', 'docs/ROADMAP.md', QUEUE,
    'tools/glyph_c014_campaign_transition.py', 'tools/glyph_campaign_transition.py',
    'tools/test_glyph_c014_campaign_transition.py',
    'tools/check_glyph_gp_config019_usb_name_selection.py',
))
C024_ROWS = ('valid_startup', 'duplicate_or_empty_profile_selection',
             'keyboard_dinput', 'reconnect_reboot', 'restoration', 'rollback',
             'safe_stop_and_anomalies')


def validate_c024_processor_rows(record):
    require(record['result'] == 'PASS' and record['evidence_gaps'] == [],
            'C024 processor requires exact complete PASS with no gaps')
    require([row['id'] for row in record['steps']] == list(C024_ROWS),
            'C024 physical row missing/reordered')
    rows = {row['id']: row for row in record['steps']}
    require(all(rows[name]['observed'].startswith('PASS') for name in C024_ROWS
                if name not in ('keyboard_dinput', 'rollback')),
            'C024 required physical observation incomplete/failing')
    require(rows['keyboard_dinput']['observed'].startswith('NOT_TESTED / DEFERRED_POST_FIRST_PUBLIC_BETA')
            and rows['rollback']['observed'].startswith('NOT_REQUIRED'),
            'C024 deferred Keyboard or unneeded rollback misrepresented')
    require(len(record['anomalies']) == 1
            and record['anomalies'][0].startswith('NONBLOCKING_RETAINED_UNRESOLVED_NONDETERMINISTIC_ANOMALY:')
            and all(token in record['anomalies'][0] for token in (
                'failed attempt', 'exactly one authorized controlled repeat PASS',
                'NOT_REPRODUCED_ON_SINGLE_CONTROLLED_REPEAT', 'root cause UNPROVEN',
                'No fix, disproval, general stability')),
            'C024 initial freeze or bounded repeat erased/misrepresented')


def authenticate_c024_processor(root, head, state, val045, verify_live=True):
    require(val045 == item(root, C024_R, 'GP-VAL-045') and val045['status'] == 'DONE',
            'C024 E lost strict VAL045 predecessor completion')
    require(original.ancestor(root, C024_R, head), 'C024 E must follow reviewed R')
    baseline = original.critical_tree(root, C024_R)
    require(baseline == original.critical_tree(root, C024_B), 'C024 R critical baseline changed')
    pending = item(root, C024_R, 'GP-CONFIG-024')
    require(pending['status'] == 'PREAUTHORIZED' and pending['activation_state'] == 'HARDWARE_PENDING',
            'C024 R is not exact reviewed hardware wait')
    acceptance = {'status', 'activation_state', 'hardware_result',
                  'hardware_evidence_dependency_satisfied', 'hardware_evidence_gaps',
                  'hardware_evidence_record'}
    queue_R = parsed_queue(original.raw_bytes(root, C024_R, QUEUE))
    protocol = original.raw_bytes(root, C024_R, C024_PROTOCOL)
    catalogs = {p: entry for p, entry in original._tree(root, C024_R).items()
                if p.endswith('_accepted_transitions.json')}
    revisions = original._git(root, 'rev-list', '--reverse', '--topo-order', C024_R + '..' + head).decode().split()
    first = None
    latched = None
    latched_state = None
    for revision in revisions:
        tree = original._tree(root, revision)
        require(not original.ancestor(root, C024_C, revision)
                and original.critical_tree(root, revision) == baseline,
                'C024 source-free E/history conceals tested source or critical drift')
        changed = set(filter(None, original._git(root, 'diff', '--name-only', '--no-renames', '-z',
                                                C024_R, revision).decode().split('\0')))
        require(changed <= C024_PROCESSOR_PATHS, 'C024 E exceeds finite source-free envelope')
        require(all(tree.get(p, ())[:2] == ('100644', 'blob') for p in changed),
                'C024 E contains deletion or nonregular mode')
        require(original.raw_bytes(root, revision, C024_PROTOCOL) == protocol,
                'C024 immutable protocol replaced')
        require({p:entry for p,entry in tree.items() if p.endswith('_accepted_transitions.json')} == catalogs,
                'C024 E changed accepted catalog or added early I')
        queue = parsed_queue(original.raw_bytes(root, revision, QUEUE))
        require([x for x in queue['items'] if x['id'] != 'GP-CONFIG-024']
                == [x for x in queue_R['items'] if x['id'] != 'GP-CONFIG-024'],
                'C024 E changed another work order')
        current = item(root, revision, 'GP-CONFIG-024')
        if current == pending and first is None:
            continue
        require(current['status'] == 'HARDWARE_VALIDATED'
                and current['activation_state'] == 'NOT_APPLICABLE'
                and current['hardware_result'] == 'PASS'
                and current['hardware_evidence_dependency_satisfied'] is True
                and current['hardware_evidence_gaps'] == [],
                'C024 E status/acceptance missing, substituted, or regressed')
        require({k:v for k,v in current.items() if k not in acceptance}
                == {k:v for k,v in pending.items() if k not in acceptance},
                'C024 E changed non-acceptance authority or exact tuple')
        reference = current['hardware_evidence_record']
        if reference == 'repo-json:' + C024_EVIDENCE:
            evidence_root = revision
        else:
            import re
            match = re.fullmatch('git-json:([0-9a-f]{40}):' + re.escape(C024_EVIDENCE), str(reference))
            require(match is not None, 'C024 E evidence reference is not immutable supported JSON')
            evidence_root = match.group(1)
        require(original.ancestor(root, C024_R, evidence_root)
                and original.ancestor(root, evidence_root, revision),
                'C024 E evidence root outside reviewed chronology')
        from check_glyph_agent_framework_docs import validate_work_order, validate_evidence_record
        validated = dict(current, hardware_evidence_record='git-json:' + evidence_root + ':' + C024_EVIDENCE)
        validate_work_order(validated, evidence_repo_root=root)
        validate_evidence_record(validated, evidence_repo_root=root)
        payload = original.raw_bytes(root, evidence_root, C024_EVIDENCE)
        require(tree.get(C024_EVIDENCE, ())[:2] == ('100644', 'blob')
                and original.raw_bytes(root, revision, C024_EVIDENCE) == payload,
                'C024 E current evidence differs from accepted reference')
        validate_c024_processor_rows(json.loads(payload, object_pairs_hook=unique))
        archive = original.raw_bytes(root, revision, C024_ARCHIVE)
        require(hashlib.sha256(archive).hexdigest() == C024_ARCHIVE_SHA256,
                'C024 E owner/session provenance replaced')
        result = original.raw_bytes(root, revision, C024_RESULT)
        require(all(token in result.decode() for token in (
            'NONBLOCKING_RETAINED_UNRESOLVED_NONDETERMINISTIC_ANOMALY',
            'DEFERRED_POST_FIRST_PUBLIC_BETA', 'PRESERVE_ORIGINAL_RAW_KEYBOARD_OUTPUT',
            'POST_BETA_KEYBOARD_PHYSICAL_VALIDATION', 'rootcauseUNPROVEN')),
            'C024 E result loses anomaly or owner scope')
        if first is None:
            first = revision
            latched = (payload, result, archive)
            latched_state = current
        else:
            require((payload, result, archive) == latched and current == latched_state,
                    'C024 E immutable accepted evidence/status replaced')
    require(first is not None and state == latched_state,
            'C024 current acceptance lacks source-free processor E')
    for path in C024_PROCESSOR_PATHS:
        if verify_live and path in original._tree(root, head):
            require(original.current_bytes(root, path) == original.raw_bytes(root, head, path)
                    and original._git(root, 'show', ':' + path) == original.current_bytes(root, path),
                    'C024 E committed/index/live mismatch: ' + path)
    return first
