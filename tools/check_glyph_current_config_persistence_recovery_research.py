#!/usr/bin/env python3
"""Offline GP-PERSIST-001 current-Config source and immutable research correspondence.

Does not execute upstream code, contact a network, mount a filesystem, access
config.bin or a device, build firmware, or choose a recovery mechanism.
"""
from __future__ import annotations

import copy
import hashlib
import json
import re
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "docs/runtime_config/fixtures/current_config_persistence_recovery_research.json"
DOC = ROOT / "docs/runtime_config/current_config_persistence_recovery_research.md"

# Immutable facts and granular reviewed evidence catalog from the independent
# 2026-09-06 source capture. This is offline correspondence, not a live lookup.
BASE = '1a4b9311c8f7ae6d7cbf0a8680cd976499112f03'

SOURCE_IDENTITIES = {'HAL/pico/src/core/Persistence.cpp': ('907e6ca3d84fc414aa67dadfcbf4f60d1e1200a7',
                                       '941cc54f0fb762e6067db338601325d33cf7f980148a59caa1d61f226e140955'),
 'HAL/pico/include/core/Persistence.hpp': ('43cbd3f39b4c9a09ecc855b0f2704b2081a45981',
                                           '56d8c3281b54a6d8168a7e8d04d31c0c2b20d1c2223b21b77a9a1549460a669d'),
 'config/glyph/common/src/config.cpp': ('701e4ac8c0a635b77ef4282f29109f7bb0bea726',
                                        'bde443c7eceb417494ae71191a2076c0ab251e987706f30a757b14aaf16ad0e5'),
 'HAL/pico/src/comms/ConfiguratorBackend.cpp': ('80c8a891bcb7d13b9b072de4a8ec490fa25ceb94',
                                                '5d4091bc86c46b0d61ce2384e40d36ff19f283d1fe94c1d15148762b18a4942b'),
 'HAL/pico/src/comms/backend_init.cpp': ('f7726a0063dd05409d7464d947a47efc675bdbef',
                                         '8cbd355e6323a775ab88aacef2ca07d2cad88232790f9d8b8d3f2f686875e2ea'),
 'platformio.ini': ('4d56f8630c1b12e84cd12f40ce05a4dc71b9362e',
                    '99fc26f84f4cf2c118d08fde7269a13b9b37f6ed1efb2d32291ba9f0b8e780e9'),
 'docs/runtime_config/runtime_config_storage_fallback_source_authority.md': ('27d0ce05248cbacc3ed5a75215ddf2d2f2a7dd73',
                                                                             '14ecb8d78b2289055be655d7ed4121665066fed6e9fcad6ce1c34bbcf840b8c8'),
 'docs/runtime_config/runtime_config_storage_fallback_architecture.md': ('4b47afd874534bb12e286294667f072bf77f4da3',
                                                                         'b85bb657596b34e71dc2e497935dde2d57ccb75f8818eb1a3e05cf1584b08215'),
 'tools/glyph_runtime_config_storage_simulator.py': ('902f9d9d0cb972a867e1de58526c95665d757408',
                                                     'e56f32b3717a2c6d17cebbfe387554859ddf22eed9961a03c10adcf7b557282f')}

REPOSITORY_IDENTITIES = {'arduino_pico': ('https://github.com/earlephilhower/arduino-pico.git',
                  '32e74d024e5e3ee5e7ec9593f5a4101641c61897',
                  '1092683c3dde85659bca81441b1fbd91a2284e86'),
 'littlefs': ('https://github.com/littlefs-project/littlefs.git',
              '6a53d76e90af33f0656333c1db09bd337fa75d23',
              '0aaa773e30366b34b36e6a60c9776a0755eb5c3c')}

BLOB_IDENTITIES = {'arduino_pico:.gitmodules': ('a754388fde16464d414423684b6dd71b86c728ee',
                              '786388fac4fb09a1f50f13e1a1c386eb33a0e1db5d8dff609a60b9f301c98e27'),
 'arduino_pico:cores/rp2040/FS.cpp': ('8a25e225551473e2af889877b6d4e8d493d86441',
                                      'cfde210641c927435f7ba828c9062e42150d586329f14442246832ba6ab8de50'),
 'arduino_pico:cores/rp2040/FS.h': ('0ea617aaa8ca548735df335ef4ac686655167617',
                                    'c188a6b49d593855d839162dd112c6a81ef4142dd5da82d59dcb983916521763'),
 'arduino_pico:libraries/LittleFS/src/LittleFS.cpp': ('a6299da36aa62fd0d628ce17d2a25e611e3b9a24',
                                                      'dfc032cc49b5254abc204b67a2aa56156d28e39b5adbb3b70c2e291667c70e5d'),
 'arduino_pico:libraries/LittleFS/src/LittleFS.h': ('53e8637b3675a13ede044ddc513a79658ea3f373',
                                                    '6036f92f824ee8257da051ed37fe01e7dfdedece33c772ae6321036dc0f412f9'),
 'arduino_pico:libraries/LittleFS/src/lfs.c': ('63bebe1965d127bb220db7a520e06de3c107391b',
                                               '3ede3a5ee496159150b9f5a1bacac98d157eb1f761e19d7d58a9b0fa4528ca6e'),
 'littlefs:DESIGN.md': ('1d02ba3bfcc37303fe3251acf3047fa2974fc498',
                        '80d3311b045d2c3555d0ba64bbbbfd8f5742db1d3ca082c915fc922c28108649'),
 'littlefs:README.md': ('32b3793f37360e2c467dd929f07c162ccf1ce6d4',
                        '411841c4ef6a58f97bc2628ff33147f7ef320eea6ba9af32f4f09fd371cc3f18'),
 'littlefs:SPEC.md': ('3663ea54425f9054196dcd9b42ab205726078f5e',
                      'b8201b4b4ea66ff0ae9b487a4aecb6c47f43af658f5d61f5e180a61f7c3b7514'),
 'littlefs:bd/lfs_testbd.c': ('1f0877d43aa0c20d08ff94ccf090a79b5d1db7d5',
                              'ccdfd0740fee110d54ac0606948d5625be87aae79eef9c745d3d74282b9c7fed'),
 'littlefs:bd/lfs_testbd.h': ('61679e5e026aecfe2981efb918102e9a09b80b74',
                              '8a9731c0cf3898e12ea4d5aeeb94305c5a3d357684a7cf783545e12131daebce'),
 'littlefs:lfs.c': ('26280fa89509bb4f94ced008ac02cd60b5c2cff8',
                    '8c28c80018293820d5400759f4918359b09d869c1a1240959b0647cc844783b5'),
 'littlefs:lfs.h': ('2bce17f5ccb91236341f30994c1b8ff42fc06872',
                    'bece5357a4721c826c3d25ffab83962986a92f929fcf2d06bc9d66b5be2a3f3a'),
 'littlefs:tests/test_files.toml': ('565e665bc9f999554d12dfe29b43926b56d870aa',
                                    '805100143ddd894b916b133e511a877c04adbfeb6b77557bfa632e26217716ac'),
 'littlefs:tests/test_move.toml': ('bb3b713f1013ac79e50c0f12aa1442477f21e3f0',
                                   'c47a85c4aba4a23bcb81d6c2db54583b011d79982138e4c452aaf8173663de92')}

EXCERPT_IDENTITIES = {'arduino_pico:.gitmodules:10': ('arduino_pico:.gitmodules',
                                 10,
                                 12,
                                 '6998357ba4737d81bb6856047b888f3dcf8196156753dcd938351669b966fc27'),
 'arduino_pico:cores/rp2040/FS.cpp:60': ('arduino_pico:cores/rp2040/FS.cpp',
                                         60,
                                         79,
                                         '5aa5893d920de32e0e3da70853ac5890b34a5104f8653239533e3a52cc6d52b5'),
 'arduino_pico:cores/rp2040/FS.cpp:125': ('arduino_pico:cores/rp2040/FS.cpp',
                                          125,
                                          131,
                                          '6d44869df915c0604d7f21ef02282aa92093607369fa7e7c3a3fa5b22cf5959c'),
 'arduino_pico:cores/rp2040/FS.cpp:481': ('arduino_pico:cores/rp2040/FS.cpp',
                                          481,
                                          509,
                                          'af4db16bb1fe35c6d570d7c829950ff22895b268d7f15e42c81f54feeb3a3fd2'),
 'arduino_pico:cores/rp2040/FS.h:70': ('arduino_pico:cores/rp2040/FS.h',
                                       70,
                                       100,
                                       'f35dc09f3276160d446f689ba0bcf8a96e8d172041641a791f9418aeefc59be4'),
 'arduino_pico:libraries/LittleFS/src/LittleFS.cpp:44': ('arduino_pico:libraries/LittleFS/src/LittleFS.cpp',
                                                         44,
                                                         104,
                                                         '3aff2af1a6f2713c04973268cdb8ecf2134d6bee82c43e69d8761906b6d1f47f'),
 'arduino_pico:libraries/LittleFS/src/LittleFS.cpp:173': ('arduino_pico:libraries/LittleFS/src/LittleFS.cpp',
                                                          173,
                                                          215,
                                                          '34901918dd7a5f1c785df4950872206af81a4dae7715074d435cdf2b4c37c1a8'),
 'arduino_pico:libraries/LittleFS/src/LittleFS.h:40': ('arduino_pico:libraries/LittleFS/src/LittleFS.h',
                                                       40,
                                                       70,
                                                       '2f56dee63980d8d512783a2328656c8bc5797320cf679c7ca9e821ffea0660da'),
 'arduino_pico:libraries/LittleFS/src/LittleFS.h:93': ('arduino_pico:libraries/LittleFS/src/LittleFS.h',
                                                       93,
                                                       106,
                                                       'af2faa49c7a06022a5182c3d7227236e413801b4d8b398cffb0b56ab39094dbb'),
 'arduino_pico:libraries/LittleFS/src/LittleFS.h:175': ('arduino_pico:libraries/LittleFS/src/LittleFS.h',
                                                        175,
                                                        195,
                                                        '962c966ab35b916d049fb3823c3f9ef1e8a67829aec8a3868b787b9e0724e39a'),
 'arduino_pico:libraries/LittleFS/src/LittleFS.h:288': ('arduino_pico:libraries/LittleFS/src/LittleFS.h',
                                                        288,
                                                        321,
                                                        'f86a2b44a2929ec5b58a7971bda85908c781529f0307d6d68b0f75bda93b98d0'),
 'arduino_pico:libraries/LittleFS/src/LittleFS.h:362': ('arduino_pico:libraries/LittleFS/src/LittleFS.h',
                                                        362,
                                                        418,
                                                        '4b8c567e06a07f87fd9bb86dde0c5d7a9a0113c3c36b59b96fbf9e459775c41e'),
 'arduino_pico:libraries/LittleFS/src/LittleFS.h:449': ('arduino_pico:libraries/LittleFS/src/LittleFS.h',
                                                        449,
                                                        470,
                                                        '9fc436152db83f132301411eccbb4325e747e6046c02f8003c2cffc5a48247e2'),
 'arduino_pico:libraries/LittleFS/src/lfs.c:1': ('arduino_pico:libraries/LittleFS/src/lfs.c',
                                                 1,
                                                 10,
                                                 '3ede3a5ee496159150b9f5a1bacac98d157eb1f761e19d7d58a9b0fa4528ca6e'),
 'littlefs:DESIGN.md:1': ('littlefs:DESIGN.md',
                          1,
                          24,
                          '1f5290ba797be58f3f96b8e6c33e31537d026f4cceda93533da932cea7bf2c2b'),
 'littlefs:README.md:12': ('littlefs:README.md',
                           12,
                           21,
                           'd935b83f80cb3c1790ba196cdd255965ea29ca44f66cb1c681a980226baa6fa0'),
 'littlefs:README.md:112': ('littlefs:README.md',
                            112,
                            135,
                            '796e3d389e17ccb870844ef9793599110870ef161e11a051a898bc0f12a75a50'),
 'littlefs:README.md:139': ('littlefs:README.md',
                            139,
                            150,
                            'f5f8d1b4a5936912706e0c3f25dd8b7d072a9a337c1cc96fc276ae016d4febb8'),
 'littlefs:SPEC.md:1': ('littlefs:SPEC.md',
                        1,
                        18,
                        '687ca0ebf6f1fc48f9c919855f6a864d3a8f2dd74565c88775cb158204529198'),
 'littlefs:bd/lfs_testbd.c:198': ('littlefs:bd/lfs_testbd.c',
                                  198,
                                  216,
                                  '7ea199190540f1d1a6de62a0a5052456ed66e8389d150e31802c6c899ea97515'),
 'littlefs:bd/lfs_testbd.c:245': ('littlefs:bd/lfs_testbd.c',
                                  245,
                                  263,
                                  '5918ca96e16819d060eda54893aa73e1d86400c45cf6f6ab9ba13a72b108e56d'),
 'littlefs:bd/lfs_testbd.h:53': ('littlefs:bd/lfs_testbd.h',
                                 53,
                                 65,
                                 '47be12d657a0c0e7060a208517eb57818018728eefa0fbc044c481dacd53bbeb'),
 'littlefs:lfs.c:2905': ('littlefs:lfs.c',
                         2905,
                         2910,
                         '89f27ea3cc904a2431e9a7f880767c62440de2affe19fcd6776cfceaf8489979'),
 'littlefs:lfs.h:209': ('littlefs:lfs.h',
                        209,
                        217,
                        '45196e2e87449de765b6eca1036d7e4943d8423183beae929f1fc8878a76e071'),
 'littlefs:lfs.h:462': ('littlefs:lfs.h',
                        462,
                        469,
                        'cb3dd942c29bd3768abf2f732b43de5f79d29e0e16ac35a10730133322cfc6b8'),
 'littlefs:lfs.h:545': ('littlefs:lfs.h',
                        545,
                        575,
                        '92b1aa28958473ff93c42f8cdc4121fb8613d015730acc7518b487be0e3fa3f4'),
 'littlefs:tests/test_files.toml:288': ('littlefs:tests/test_files.toml',
                                        288,
                                        299,
                                        'a2bdedde10fd8dad811607992f9195db573518d903877ce11904f98e4edf0b56'),
 'littlefs:tests/test_files.toml:336': ('littlefs:tests/test_files.toml',
                                        336,
                                        358,
                                        'bf0db3d72f14069f0cd98257a6a3f0b67b85e14a3138eefae3e65446dfc2b098'),
 'littlefs:tests/test_move.toml:338': ('littlefs:tests/test_move.toml',
                                       338,
                                       349,
                                       '2033971494cd885294021946aae1487c646cf65b93fe74d4c00ee0d50b8cb561')}

STEP_IDENTITIES = {'lifecycle.mount': ('lifecycle',
                     'HAL/pico/src/core/Persistence.cpp',
                     'Persistence::Persistence()',
                     'bool Persistence::SaveConfig',
                     'LittleFS.begin();',
                     'IGNORED'),
 'lifecycle.unmount': ('lifecycle',
                       'HAL/pico/src/core/Persistence.cpp',
                       'Persistence::Persistence()',
                       'bool Persistence::SaveConfig',
                       'LittleFS.end();',
                       'VOID'),
 'save.size': ('save',
               'HAL/pico/src/core/Persistence.cpp',
               'bool Persistence::SaveConfig',
               'bool Persistence::LoadConfig',
               'if (!pb_get_encoded_size(&encoded_size, Config_fields, &config)) {\n'
               '        return false;\n'
               '    }',
               'CHECKED'),
 'save.open': ('save',
               'HAL/pico/src/core/Persistence.cpp',
               'bool Persistence::SaveConfig',
               'bool Persistence::LoadConfig',
               'File config_file = LittleFS.open(config_filename, "w+");\n'
               '    if (!config_file) {\n'
               '        return false;\n'
               '    }',
               'CHECKED'),
 'save.placeholder': ('save',
                      'HAL/pico/src/core/Persistence.cpp',
                      'bool Persistence::SaveConfig',
                      'bool Persistence::LoadConfig',
                      'ConfigHeader header = { .config_size = 0, .config_crc = 0 };',
                      'NOT_APPLICABLE'),
 'save.header_write': ('save',
                       'HAL/pico/src/core/Persistence.cpp',
                       'bool Persistence::SaveConfig',
                       'bool Persistence::LoadConfig',
                       'config_file.write((uint8_t *)&header, sizeof(ConfigHeader));',
                       'IGNORED'),
 'save.stream': ('save',
                 'HAL/pico/src/core/Persistence.cpp',
                 'bool Persistence::SaveConfig',
                 'bool Persistence::LoadConfig',
                 'pb_ostream_t ostream = as_pb_ostream(config_file);',
                 'NOT_APPLICABLE'),
 'save.encode': ('save',
                 'HAL/pico/src/core/Persistence.cpp',
                 'bool Persistence::SaveConfig',
                 'bool Persistence::LoadConfig',
                 'if (!pb_encode(&ostream, Config_fields, &config)) {\n'
                 '        config_file.close();\n'
                 '        return false;\n'
                 '    }',
                 'CHECKED'),
 'save.seek_body': ('save',
                    'HAL/pico/src/core/Persistence.cpp',
                    'bool Persistence::SaveConfig',
                    'bool Persistence::LoadConfig',
                    'config_file.seek(config_offset);',
                    'IGNORED'),
 'save.crc_init': ('save',
                   'HAL/pico/src/core/Persistence.cpp',
                   'bool Persistence::SaveConfig',
                   'bool Persistence::LoadConfig',
                   'CRC32 crc;',
                   'NOT_APPLICABLE'),
 'save.read_crc': ('save',
                   'HAL/pico/src/core/Persistence.cpp',
                   'bool Persistence::SaveConfig',
                   'bool Persistence::LoadConfig',
                   'while ((value = config_file.read()) != -1) {\n        crc.update((uint8_t)value);\n    }',
                   'SENTINEL_ONLY'),
 'save.length': ('save',
                 'HAL/pico/src/core/Persistence.cpp',
                 'bool Persistence::SaveConfig',
                 'bool Persistence::LoadConfig',
                 'header.config_size = ostream.bytes_written;',
                 'NOT_APPLICABLE'),
 'save.crc_final': ('save',
                    'HAL/pico/src/core/Persistence.cpp',
                    'bool Persistence::SaveConfig',
                    'bool Persistence::LoadConfig',
                    'header.config_crc = crc.finalize();',
                    'NOT_APPLICABLE'),
 'save.seek_header': ('save',
                      'HAL/pico/src/core/Persistence.cpp',
                      'bool Persistence::SaveConfig',
                      'bool Persistence::LoadConfig',
                      'config_file.seek(0);',
                      'IGNORED'),
 'save.header_rewrite': ('save',
                         'HAL/pico/src/core/Persistence.cpp',
                         'bool Persistence::SaveConfig',
                         'bool Persistence::LoadConfig',
                         'config_file.write((uint8_t *)&header, sizeof(ConfigHeader));',
                         'IGNORED'),
 'save.close': ('save',
                'HAL/pico/src/core/Persistence.cpp',
                'bool Persistence::SaveConfig',
                'bool Persistence::LoadConfig',
                'config_file.close();',
                'VOID'),
 'save.success': ('save',
                  'HAL/pico/src/core/Persistence.cpp',
                  'bool Persistence::SaveConfig',
                  'bool Persistence::LoadConfig',
                  'return true;',
                  'NOT_APPLICABLE'),
 'load.open': ('load',
               'HAL/pico/src/core/Persistence.cpp',
               'bool Persistence::LoadConfig',
               'bool Persistence::CheckSavedConfig()',
               'File config_file = LittleFS.open(config_filename, "r");\n'
               '    if (!config_file) {\n'
               '        return false;\n'
               '    }',
               'CHECKED'),
 'load.validate': ('load',
                   'HAL/pico/src/core/Persistence.cpp',
                   'bool Persistence::LoadConfig',
                   'bool Persistence::CheckSavedConfig()',
                   'if (!CheckSavedConfig(config_file)) {\n'
                   '        config_file.close();\n'
                   '        return false;\n'
                   '    }',
                   'CHECKED'),
 'load.seek': ('load',
               'HAL/pico/src/core/Persistence.cpp',
               'bool Persistence::LoadConfig',
               'bool Persistence::CheckSavedConfig()',
               'if (!config_file.seek(config_offset)) {\n'
               '        config_file.close();\n'
               '        return false;\n'
               '    }',
               'CHECKED'),
 'load.reset': ('load',
                'HAL/pico/src/core/Persistence.cpp',
                'bool Persistence::LoadConfig',
                'bool Persistence::CheckSavedConfig()',
                'config = Config_init_default;',
                'NOT_APPLICABLE'),
 'load.stream': ('load',
                 'HAL/pico/src/core/Persistence.cpp',
                 'bool Persistence::LoadConfig',
                 'bool Persistence::CheckSavedConfig()',
                 'pb_istream_t istream = as_pb_istream(config_file, (size_t)config_file.available());',
                 'NOT_APPLICABLE'),
 'load.decode': ('load',
                 'HAL/pico/src/core/Persistence.cpp',
                 'bool Persistence::LoadConfig',
                 'bool Persistence::CheckSavedConfig()',
                 'if (!pb_decode(&istream, Config_fields, &config)) {\n'
                 '        config_file.close();\n'
                 '        return false;\n'
                 '    }',
                 'CHECKED'),
 'load.close': ('load',
                'HAL/pico/src/core/Persistence.cpp',
                'bool Persistence::LoadConfig',
                'bool Persistence::CheckSavedConfig()',
                'config_file.close();',
                'VOID'),
 'load.success': ('load',
                  'HAL/pico/src/core/Persistence.cpp',
                  'bool Persistence::LoadConfig',
                  'bool Persistence::CheckSavedConfig()',
                  'return true;',
                  'NOT_APPLICABLE'),
 'check.size': ('check',
                'HAL/pico/src/core/Persistence.cpp',
                'bool Persistence::CheckSavedConfig(File &config_file)',
                None,
                'size_t file_size = config_file.size();',
                'NOT_APPLICABLE'),
 'check.header': ('check',
                  'HAL/pico/src/core/Persistence.cpp',
                  'bool Persistence::CheckSavedConfig(File &config_file)',
                  None,
                  'size_t bytes_read = config_file.read((uint8_t *)&header, sizeof(ConfigHeader));\n'
                  '    if (bytes_read < sizeof(ConfigHeader)) {\n'
                  '        return false;\n'
                  '    }',
                  'CHECKED'),
 'check.length': ('check',
                  'HAL/pico/src/core/Persistence.cpp',
                  'bool Persistence::CheckSavedConfig(File &config_file)',
                  None,
                  'size_t config_size = file_size - config_offset;\n'
                  '    if (config_size != header.config_size) {\n'
                  '        return false;\n'
                  '    }',
                  'CHECKED'),
 'check.read_crc': ('check',
                    'HAL/pico/src/core/Persistence.cpp',
                    'bool Persistence::CheckSavedConfig(File &config_file)',
                    None,
                    'while ((value = config_file.read()) != -1) {\n'
                    '        crc.update((uint8_t)value);\n'
                    '    }',
                    'SENTINEL_ONLY'),
 'check.crc': ('check',
               'HAL/pico/src/core/Persistence.cpp',
               'bool Persistence::CheckSavedConfig(File &config_file)',
               None,
               'if (crc.finalize() != header.config_crc) {\n        return false;\n    }',
               'CHECKED'),
 'check.success': ('check',
                   'HAL/pico/src/core/Persistence.cpp',
                   'bool Persistence::CheckSavedConfig(File &config_file)',
                   None,
                   'return true;',
                   'NOT_APPLICABLE'),
 'boot.default': ('boot',
                  'config/glyph/common/src/config.cpp',
                  'Config config = glyph_default_config();',
                  'void loop() {',
                  'Config config = glyph_default_config();',
                  'NOT_APPLICABLE'),
 'boot.load_save': ('boot',
                    'config/glyph/common/src/config.cpp',
                    'Config config = glyph_default_config();',
                    'void loop() {',
                    'if (!persistence.LoadConfig(config)) {\n        persistence.SaveConfig(config);\n    }',
                    'CHECKED_LOAD_IGNORED_SAVE'),
 'boot.backends': ('boot',
                   'config/glyph/common/src/config.cpp',
                   'Config config = glyph_default_config();',
                   'void loop() {',
                   'backend_count = initialize_backends(',
                   'NOT_APPLICABLE'),
 'setconfig.reset': ('setconfig',
                     'HAL/pico/src/comms/ConfiguratorBackend.cpp',
                     'bool ConfiguratorBackend::HandleSetConfig()',
                     'bool ConfiguratorBackend::HandleUnknownCommand',
                     '_config = Config_init_default;',
                     'NOT_APPLICABLE'),
 'setconfig.stream': ('setconfig',
                      'HAL/pico/src/comms/ConfiguratorBackend.cpp',
                      'bool ConfiguratorBackend::HandleSetConfig()',
                      'bool ConfiguratorBackend::HandleUnknownCommand',
                      'pb_istream_t istream = as_pb_istream(_in);',
                      'NOT_APPLICABLE'),
 'setconfig.decode': ('setconfig',
                      'HAL/pico/src/comms/ConfiguratorBackend.cpp',
                      'bool ConfiguratorBackend::HandleSetConfig()',
                      'bool ConfiguratorBackend::HandleUnknownCommand',
                      'if (!pb_decode(&istream, Config_fields, &_config)) {',
                      'CHECKED'),
 'setconfig.decode_error': ('setconfig',
                            'HAL/pico/src/comms/ConfiguratorBackend.cpp',
                            'bool ConfiguratorBackend::HandleSetConfig()',
                            'bool ConfiguratorBackend::HandleUnknownCommand',
                            'WritePacket(CMD_ERROR, (uint8_t *)errmsg, errmsg_len);',
                            'IGNORED'),
 'setconfig.restore': ('setconfig',
                       'HAL/pico/src/comms/ConfiguratorBackend.cpp',
                       'bool ConfiguratorBackend::HandleSetConfig()',
                       'bool ConfiguratorBackend::HandleUnknownCommand',
                       'persistence.LoadConfig(_config);\n        return false;',
                       'IGNORED'),
 'setconfig.backend_bound': ('setconfig',
                             'HAL/pico/src/comms/ConfiguratorBackend.cpp',
                             'bool ConfiguratorBackend::HandleSetConfig()',
                             'bool ConfiguratorBackend::HandleUnknownCommand',
                             'if (_config.default_backend_config > '
                             '_config.communication_backend_configs_count) {',
                             'CHECKED'),
 'setconfig.mode_bound': ('setconfig',
                          'HAL/pico/src/comms/ConfiguratorBackend.cpp',
                          'bool ConfiguratorBackend::HandleSetConfig()',
                          'bool ConfiguratorBackend::HandleUnknownCommand',
                          'if (default_mode_id > _config.game_mode_configs_count) {',
                          'CHECKED'),
 'setconfig.keyboard_type': ('setconfig',
                             'HAL/pico/src/comms/ConfiguratorBackend.cpp',
                             'bool ConfiguratorBackend::HandleSetConfig()',
                             'bool ConfiguratorBackend::HandleUnknownCommand',
                             'if (keyboard_mode_id > 0 && gamemode_config.mode_id != MODE_KEYBOARD) {',
                             'CHECKED'),
 'setconfig.custom_type': ('setconfig',
                           'HAL/pico/src/comms/ConfiguratorBackend.cpp',
                           'bool ConfiguratorBackend::HandleSetConfig()',
                           'bool ConfiguratorBackend::HandleUnknownCommand',
                           'if (custom_mode_id > 0 && gamemode_config.mode_id != MODE_CUSTOM) {',
                           'CHECKED'),
 'setconfig.keyboard_bound': ('setconfig',
                              'HAL/pico/src/comms/ConfiguratorBackend.cpp',
                              'bool ConfiguratorBackend::HandleSetConfig()',
                              'bool ConfiguratorBackend::HandleUnknownCommand',
                              'if (keyboard_mode_id > _config.keyboard_modes_count) {',
                              'CHECKED'),
 'setconfig.custom_bound': ('setconfig',
                            'HAL/pico/src/comms/ConfiguratorBackend.cpp',
                            'bool ConfiguratorBackend::HandleSetConfig()',
                            'bool ConfiguratorBackend::HandleUnknownCommand',
                            'if (custom_mode_id > _config.custom_modes_count) {',
                            'CHECKED'),
 'setconfig.save': ('setconfig',
                    'HAL/pico/src/comms/ConfiguratorBackend.cpp',
                    'bool ConfiguratorBackend::HandleSetConfig()',
                    'bool ConfiguratorBackend::HandleUnknownCommand',
                    'if (!persistence.SaveConfig(_config)) {\n'
                    '        char errmsg[] = "Failed to save config to memory";\n'
                    '        WritePacket(CMD_ERROR, (uint8_t *)errmsg, sizeof(errmsg));\n'
                    '        return false;\n'
                    '    }',
                    'CHECKED_SAVE_IGNORED_PACKET'),
 'setconfig.success': ('setconfig',
                       'HAL/pico/src/comms/ConfiguratorBackend.cpp',
                       'bool ConfiguratorBackend::HandleSetConfig()',
                       'bool ConfiguratorBackend::HandleUnknownCommand',
                       'WritePacket(CMD_SUCCESS, nullptr, 0);\n    return true;',
                       'IGNORED_PACKET'),
 'additional_save.save': ('additional_save',
                          'HAL/pico/src/comms/backend_init.cpp',
                          '        if(backend_config.backend_id != COMMS_BACKEND_CONFIGURATOR)',
                          None,
                          'if(temp_backend_index > 0 || temp_gamemode_index > 0) {\n'
                          '                persistence.SaveConfig(config);\n'
                          '            }',
                          'IGNORED')}

REVIEWED_RECORDS = {'claims': [('header_abi', 'be7493c8575a4fc33fc9ad43281de84e7cec675d9ed9451af9ea6b4bda344287'),
            ('wrapper_truncate_sync', 'f632b36133eec314a803677f62b02474567fee23e0ca1ea17cf6936db029b57a'),
            ('atomicity_boundary', '990c359e448bfdfb99746d441d8fb8b830b4ee06775bef0df38d7f8ab4d25f81'),
            ('rename_constraints', '81794e311c3ed139ce88ae6a32e9734a012999c66749c8be6a3b6f246c0109b6'),
            ('read_and_close', '7d14785ba263bf4bf16707c8b2416e06b1cd9368081d75dd815d493d69be861b'),
            ('autoformat', '3bf080ef91663a63ee86466bcb21e0ea9fcb12062ef5628b97e91df5e9d51acd'),
            ('flash_callbacks', '99a6693f50552e2ad0c5f5e574e2c83e584e28d3d2e600a9c4f31c523efacf9f'),
            ('wear_and_capacity', 'd0371b576ed57c48505ee6d19f80851661cbedf16db3367a5e9a1d6ffe17a87a'),
            ('boot_decode_failure', 'c23f92389e59cbcad7d0a3c98d075b657034f4676d5785d9d9f69806aff19010'),
            ('testability', '3d0babf659032e1f2afeb7fc93567f850678e29cbc9f0f1b28026189e95f7888'),
            ('device_outcomes', '2859e8db36a03f8dd025ed5ef7e2579bcdbbf026a0aebe80c643e9206a694a52')],
 'failure_windows': [('encode_preflight', 'ef04326b3b576c8335b698e60705d9d25591f1551dfbce50cf8d435dc5cbaf8c'),
                     ('mount_open', '4a17439512b8c001e41db2ff105c29f0f88a533c1b5fc9ab872056b76d375d46'),
                     ('truncate_sync', 'e2399a2a09890681e109407267d7b808f70c856e36f5f95e3ebcb021ae6fa59f'),
                     ('placeholder_write',
                      '75207b2dc1095e97f3c2b90c85511ceaeb3b21dbf5d199afd09c5af63285d579'),
                     ('body_encode', '5aa82bd2ed5dc15b760c15d8c9ff06fc3005cf7ebb9c895646136a935c7079f0'),
                     ('seek_read_crc', 'cfc25ada7fbd84727e573af4ab1875e16ca790435a6ca339e91c3dfdb50520dc'),
                     ('header_rewrite', '4b087cc0b1b83b92b4986a7d084244393a57ff4feb2e13d21db00d1885e0fb55'),
                     ('close_sync', '0cfe28430cb1672f1d5a9175ece75bde8af36a63a9713be8f4b1727d520fbfd3'),
                     ('load_integrity', '5c36d815488529ac188a4f88734c7fa6855534ef30710f0307d0fad467cdf272'),
                     ('load_decode', 'e0de146c272db1b6db84ddb19ec9dc5a955714e1c4a03e2fd8ac6994b06b24f3'),
                     ('setconfig_failure',
                      'c2421941b0e6172285612f7a4e3db2891b33cb3ed222566a9b0fc99608187b00'),
                     ('device_limits', '1cdfeaa1ab82063965f5d4e4b931f5beef6ec3d7851ba9e75bc3cd8c4bb136c9')],
 'alternatives': [('temp_and_rename', 'b38d9adcc4f4b90a72f500261a90a20e29c7c24ac0d3055e6f3b6a15f92a0545'),
                  ('temp_plus_backup', '9b7236a7ea8eec28a5786b6bd8edcc448e8d3ebdb09a5a772c1e1bd761a2a665'),
                  ('two_slot_generation',
                   '353148c13ba8900c14fa960ed80831cd6dd4d457cc9c10a1afcf8b110fb98090')],
 'decision_gates': [('recovery_invariant',
                     '5608cc3e110e57c5d90d2d8d0ce36135c2e206453d070f83850b10994724ecdf'),
                    ('stale_state_cleanup',
                     'aaf154817eaf6bdbc51177013cadc0b72927770e234c2ad98b455755cbf2f461'),
                    ('boot_default', '5abd1d4cd08151d5f6ef045b84954035423af82c1782decb60d8d298f7e42423'),
                    ('autoformat', '511d762dca56994408099523ec3dd987970c1e2a90f8f7e5f7723f9de9204b67'),
                    ('migration_compatibility',
                     '06d72e7372066612662b0a3568367931bb98d73032c1cbeaa32cffa271e69752'),
                    ('rename_replacement',
                     '36fb7a8f676cb9756304ceb170d607af0194ed9c27cf9a62482994dac58eda54'),
                    ('readback_diagnostics',
                     'feb612ecd59ef48b392343927c65d562def93a521b3e83016264fe24169f624c'),
                    ('concurrency', 'c704b0dc9070db826d8ce9935aaca63116c3f9fee21b98bd4beaea9ab317380f'),
                    ('capacity_wear_save_cadence',
                     'b2e07eefa50ca6dc5fa507873cf5c1e5fb082a8235f40e19cd7a7fd87bec59b9'),
                    ('update_preservation',
                     '2393b64c0774458342cd57c6461f4644ea482b213db15ba7c2c119a9c6413d58'),
                    ('fault_injection', 'e829cecec86e0d5248a0c64ad744724080f7f2cdde3c0f177c9245f8d19c7969'),
                    ('physical_recovery_acceptance',
                     '560f70424af174352a159938377c2d8977abe3ab83dfe41cffeff6779c6456c8')],
 'future_validation_gates': [('authority',
                              '2ab927d4a3ccd1fe55cb2424af603b40a9b982f4b7633214ddc911fe32b2a740'),
                             ('offline', 'eac2055d2a4cd140f7e346e2e59dfd6dc29e43420a7e0002a6be0b6cb3657826'),
                             ('review', '16ea61e7c46c48246c1a466910cebb9f34fa17c210afb03b8a1c874ee1dd8ef7'),
                             ('build', '7134057d50d13faa303c2450e258c731fd1c25bab63461ec2ee5e3c10d00a4da'),
                             ('custody', '21b58b4700cfe5e02c3c5264ff64cb738fcf7f31b2483c66d9aa2c914b97e455'),
                             ('hardware',
                              '6e7da51125095ebe5141245c001ec0f3a91a22b20daefc9a68ffe666afd38271')],
 'searches': [('current_path', 'dfd4a75bbc05a495dc2e7a4b1de01f627b856775b433a9ba175fa6634399e860'),
              ('upstream_identity', '9831e28b5e784c4224c16e7e053b18375f016b6bd0b6f7afe07168aed0179f1b'),
              ('fault_tests', '08f5cc99e361452188431947fa09dd35e42e2978417818ea0c63c77d33f006d2')]}

LIMITS = {'firmware_runtime_source_changed': False,
 'build_performed': False,
 'firmware_artifact_produced': False,
 'config_bin_accessed': False,
 'filesystem_mounted': False,
 'device_touched': False,
 'hardware_tested': False,
 'upstream_code_executed': False,
 'checker_network_access': False,
 'recovery_implementation_authorized': False,
 'runtime_loaded_config_implemented': False,
 'gameplay_semantics_claimed': False,
 'nunchuk': 'NOT_TESTED',
 'root_cause': 'UNPROVEN'}

TOP_KEYS = ['schema_name',
 'schema_version',
 'work_order',
 'research_base_commit',
 'status',
 'selected_recovery_mechanism',
 'repository_sources',
 'platform_selector',
 'upstream_repositories',
 'upstream_blobs',
 'upstream_excerpts',
 'current_steps',
 'claims',
 'failure_windows',
 'alternatives',
 'decision_gates',
 'future_cut_points',
 'future_validation_gates',
 'research_limits',
 'searches']

LOOKUP_TIMES = {'arduino_pico': '2026-09-06T00:28:49.697580+00:00',
 'littlefs': '2026-09-06T00:28:50.014061+00:00',
 'arduino_pico:.gitmodules': '2026-09-06T00:27:10.977803+00:00',
 'arduino_pico:cores/rp2040/FS.cpp': '2026-09-06T00:27:11.187302+00:00',
 'arduino_pico:cores/rp2040/FS.h': '2026-09-06T00:27:11.407780+00:00',
 'arduino_pico:libraries/LittleFS/src/LittleFS.cpp': '2026-09-06T00:27:11.633413+00:00',
 'arduino_pico:libraries/LittleFS/src/LittleFS.h': '2026-09-06T00:27:11.977378+00:00',
 'arduino_pico:libraries/LittleFS/src/lfs.c': '2026-09-06T00:27:12.280711+00:00',
 'littlefs:DESIGN.md': '2026-09-06T00:28:01.817339+00:00',
 'littlefs:README.md': '2026-09-06T00:28:02.029931+00:00',
 'littlefs:SPEC.md': '2026-09-06T00:28:02.276812+00:00',
 'littlefs:bd/lfs_testbd.c': '2026-09-06T00:28:02.509258+00:00',
 'littlefs:bd/lfs_testbd.h': '2026-09-06T00:28:02.729375+00:00',
 'littlefs:lfs.c': '2026-09-06T00:28:03.022623+00:00',
 'littlefs:lfs.h': '2026-09-06T00:28:03.269613+00:00',
 'littlefs:tests/test_files.toml': '2026-09-06T00:28:03.560264+00:00',
 'littlefs:tests/test_move.toml': '2026-09-06T00:28:03.782300+00:00'}

STEP_CONSEQUENCES = {'lifecycle.mount': '595770ee38380a91a69a273bb45f0084c74396693beb4d392037540bab1fb090',
 'lifecycle.unmount': 'e089f9d574fac03e3309e36f9010a5daa11c2e891e61644d52abeaddc1220852',
 'save.size': '84c2250385b31596e9dff4d32186d8738cdf518d7f14d1f9197e960d9bf73332',
 'save.open': 'fc8821cf9ecc2ba5751145124b5762573167883f176230eb00944eba4ae49e33',
 'save.placeholder': '7f5edb7bbbf1b08f953e10480e11a88a7a9a627c3c411a4ac566c698fcf59090',
 'save.header_write': '1cacb06196a89130dd2b3198855bbbbc77229ae1c2bff1193560f6cc51dd83b0',
 'save.stream': '3b58d929ad2e8885aeb934ae3d7198a5531dd53d04c6081cbb6a428ad1dbfee1',
 'save.encode': 'e4ce6cc6c23a31a8d6921d6371fb28c29b64a4c7be07f7605a7a1b0682d02fdc',
 'save.seek_body': '257d6a7f735fed5dc9cae567103380f4ed23d5669b640cf4351ea94eb15d0ea6',
 'save.crc_init': '65f4636cbf5e8c033951482d2b99047a1437ff7feaa85d3ea4aab0fba007cf71',
 'save.read_crc': 'fc23ae31e3626e292505c51f2a183ff8b138817a6d38dcdc2daf447fd52e644c',
 'save.length': '4d47a69926a10ed9621b0b57521f4fd3e04795cf38818ebb29e05f0b1c0e8306',
 'save.crc_final': '1a0ca12d50d0bc115c2dc82aff7793a1826bd756a2b77399819b656a51023910',
 'save.seek_header': 'bee74a079ab7381f9320f814762a69f98a12d3906f0b1e18ef804035a3ecc62b',
 'save.header_rewrite': '29f91fe1489f477d104db776823127d542042d20f505bb43b0bee3c36ec22445',
 'save.close': '239de38c2205b8508d787d1656acd1de4e3806196377feef2d06336d07164167',
 'save.success': '2d92f7e904680e17d0a3f22a028ea22c88531760b0c599f09e71b088d10ae34b',
 'load.open': '96b40eeef0393667810305102402e8fa0e2d92709972466ca7470a352f50355b',
 'load.validate': '2396322257bcf86e68d258684648444dc258fdfc5ce86f7417a9f3db77d6ca6f',
 'load.seek': '2435ad0277248194b3995c9a753859c7a5c4a3cb317955aa5ee33e1355629712',
 'load.reset': '54213a5c0ba8b5559b7bb0edfc23e5e10f94e2de81aed1a76f91b38d9629c5fe',
 'load.stream': '3682e0ea3710709cc337764ae64a426613d86b53c16c0cb69d53d0ce2088e9b5',
 'load.decode': '184f5f2383f0a2c99d61555bf2fcb238780f546a3de8915f7e1f47f830c4b123',
 'load.close': '02a2ab1f605a3c85ba983be108a83d009393b824fab97adb8fc9b80d05724cb9',
 'load.success': '0ddaac7104341075dbcdcc26d1ac420dbc7668c3cf00de699d0f58718f0961d1',
 'check.size': '35e93257ee0de3ae3601bba746b7176c4d062059e2231be4aa70741018678247',
 'check.header': '28ef4e2a97ef5797215b6e4bf3febdae857a8fbf06785ee7f0da9e1c72516c33',
 'check.length': '875dc232f31b2aad1f8fc2ff7ecaa4a514b1784ca9b56dd51e069039b5d06932',
 'check.read_crc': 'ad19e930462eb807d904ebfe8ef534c45d1f6326fde1b4344d11446ca29c2288',
 'check.crc': '00ec797bd199e33f80e0a756daa2d0be907b567eb920e0082ee2fb81af9f6549',
 'check.success': '30219d60c16c02762fd66265ae03c66dad699a6be68ba267b0be691484fdb05a',
 'boot.default': '1dbce4f36fa643e2d280259c928e643de12d0d62913ce9635eccff14a383101b',
 'boot.load_save': 'a87f05d4f900d335ae56bc6016d7ad80d3c355ec9ee22ed7439c817556d2c9c0',
 'boot.backends': '057ff452f5aa80e2614b1c42400f272acb3a1c78353f731d84dea80fc41fd96f',
 'setconfig.reset': '3946a32e220582adc79b22df77f39aa0abcbaf7f48230d5ada3ca9dfbf632278',
 'setconfig.stream': 'ffd9645ca45e7a27507a552ee814d5eff8a7cd69c06492b40bcddc44b40a8555',
 'setconfig.decode': '210159a60f246be4f7dca9e49af713bacc009ed7bbf654ab3cefc07b103ec9e3',
 'setconfig.decode_error': 'd80f89fe2a4c88f4e19d801236f3698b7753107e718987707d95930d7e4c37c7',
 'setconfig.restore': '8b10ed9af96edfc07b4f78120f27a62904dd16459fe73c48ec7087af7d207b92',
 'setconfig.backend_bound': '9d7000fd3f163efcee352b6e4010864d4918d3450459bd787958ec073017ab9f',
 'setconfig.mode_bound': 'de25a4cce7028aef87f7e112e92490daea22d158a6040825e4bab4725c27cd8d',
 'setconfig.keyboard_type': '5d83cebc3de93676a8706d002d7506209d88ceb29237e2c6f5f2d9de8062aad4',
 'setconfig.custom_type': 'f8554e36ed654704025b9cea27d1dcdd0faf5d57a2cc84bef5ce2662e7f3634a',
 'setconfig.keyboard_bound': '26ed19d12d75998c3c7b65f8e01aca717f40dbdeb866bf207a684414166f8403',
 'setconfig.custom_bound': '95149468e2c45740f1c9ef47eef96a500554924bf9b514540070bec71464a7cf',
 'setconfig.save': '316b2659be6df402eec35867281f3a8c06ad0e9a8f340d3236ccb5c5bb0eb23c',
 'setconfig.success': '22567d0ecb803cea4ee02ed63e763bb24321e6f648d40af640418d41d0518dfd',
 'additional_save.save': '3d326b02fc30c5fda3f72e7f04bc1f4021d82ab858b577ca8e5263fbdf2cbf2b'}


class ResearchError(ValueError):
    """A frozen source/evidence/authority contract does not correspond."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ResearchError(message)


def exact(value: object, keys: list[str], label: str) -> dict:
    require(type(value) is dict and list(value) == keys, f"{label}: exact fields/order required")
    return value


def pairs(items: list[tuple[str, object]]) -> dict:
    result = {}
    for key, item in items:
        require(key not in result, f"duplicate JSON key: {key}")
        result[key] = item
    return result


def load_text(text: str) -> dict:
    return json.loads(text, object_pairs_hook=pairs)


def seal(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def sha(value: object, size: int, label: str) -> None:
    require(type(value) is str and re.fullmatch(r"[0-9a-f]{%d}" % size, value) is not None,
            f"{label}: full lowercase immutable hash required")


def utc(value: object, label: str) -> None:
    require(type(value) is str and value.endswith("+00:00"), f"{label}: UTC timestamp required")
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError as exc:
        raise ResearchError(f"{label}: invalid timestamp") from exc
    require(parsed.utcoffset() == timedelta(0), f"{label}: UTC required")


def ordered(value: object, ids: list[str], label: str) -> list:
    require(type(value) is list and all(type(r) is dict for r in value), f"{label}: object list required")
    require([r.get("id") for r in value] == ids, f"{label}: complete unique reviewed order required")
    return value


def source_bytes(root: Path = ROOT) -> dict[str, bytes]:
    result = {}
    for path in SOURCE_IDENTITIES:
        file = root / path
        require(file.is_file() and not file.is_symlink(), f"source must remain regular: {path}")
        result[path] = file.read_bytes()
    return result


def validate(value: dict, sources: dict[str, bytes]) -> None:
    exact(value, TOP_KEYS, "research")
    require(value["schema_name"] == "glyph_current_config_persistence_recovery_research" and
            type(value["schema_version"]) is int and value["schema_version"] == 1,
            "research schema identity")
    require(value["work_order"] == "GP-PERSIST-001" and value["research_base_commit"] == BASE,
            "research work-order/base identity")
    require(value["status"] == "EVIDENCE_COMPLETE_IMPLEMENTATION_NOT_AUTHORIZED" and
            value["selected_recovery_mechanism"] is None, "research cannot authorize implementation")
    require(list(sources) == list(SOURCE_IDENTITIES), "closed current-source set")
    for record in ordered(value["repository_sources"], list(SOURCE_IDENTITIES), "repository_sources"):
        exact(record, ["id", "path", "mode", "blob", "sha256"], "repository source")
        path = record["id"]
        blob, digest = SOURCE_IDENTITIES[path]
        require(record["path"] == path and record["mode"] == "100644", "source path/mode")
        sha(record["blob"], 40, path); sha(record["sha256"], 64, path)
        require((record["blob"], record["sha256"]) == (blob, digest), "source provenance drift")
        data = sources[path]
        require(hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest() == blob and
                hashlib.sha256(data).hexdigest() == digest, f"current source bytes drift: {path}")
    selector = exact(value["platform_selector"], ["path", "fragment"], "platform selector")
    require(selector == {"path": "platformio.ini", "fragment":
            "framework-arduinopico@https://github.com/earlephilhower/arduino-pico.git#3.6.3"},
            "exact configured framework selector")
    require(sources["platformio.ini"].decode().count(selector["fragment"]) == 1, "unique selector correspondence")

    for record in ordered(value["upstream_repositories"], list(REPOSITORY_IDENTITIES), "upstream_repositories"):
        exact(record, ["repository", "commit", "tree", "method", "lookup_timestamp", "commit_api", "id",
                       "selector_observation", "parent_gitlink"], "upstream repository")
        identity = record["id"]
        repository, commit, tree = REPOSITORY_IDENTITIES[identity]
        sha(record["commit"], 40, identity); sha(record["tree"], 40, identity)
        require((record["repository"], record["commit"], record["tree"]) == (repository, commit, tree),
                "authoritative full upstream identity drift")
        slug = repository.removeprefix("https://github.com/").removesuffix(".git")
        require(record["commit_api"] == f"https://api.github.com/repos/{slug}/git/commits/{commit}",
                "immutable authoritative commit API")
        require(record["method"] == "HTTPS GitHub Git commit/tree API, immutable raw source SHA-1 object rehash",
                "lookup method drift")
        utc(record["lookup_timestamp"], identity)
        require(record["lookup_timestamp"] == LOOKUP_TIMES[identity], "frozen lookup timestamp drift")
        if identity == "arduino_pico":
            require(record["selector_observation"] == "refs/tags/3.6.3" and record["parent_gitlink"] is None,
                    "selector observation is not immutable authority")
        else:
            require(record["selector_observation"] is None, "littlefs identity comes from gitlink")
            exact(record["parent_gitlink"], ["repository", "path", "mode", "commit"], "gitlink")
            require(record["parent_gitlink"] == {"repository": "arduino_pico",
                    "path": "libraries/LittleFS/lib/littlefs", "mode": "160000", "commit": commit},
                    "parent gitlink must bind exact incorporated littlefs identity")
    for record in ordered(value["upstream_blobs"], list(BLOB_IDENTITIES), "upstream_blobs"):
        exact(record, ["id", "repository", "path", "mode", "type", "blob", "sha256", "immutable_url",
                       "lookup_timestamp", "lookup_method"], "upstream blob")
        identity = record["id"]
        repo, path = identity.split(":", 1)
        require(record["repository"] == repo and record["path"] == path and
                record["mode"] == "100644" and record["type"] == "blob", "regular exact upstream source/doc/test")
        sha(record["blob"], 40, identity); sha(record["sha256"], 64, identity)
        require((record["blob"], record["sha256"]) == BLOB_IDENTITIES[identity], "frozen upstream blob identity")
        repository, commit, _ = REPOSITORY_IDENTITIES[repo]
        slug = repository.removeprefix("https://github.com/").removesuffix(".git")
        require(record["immutable_url"] == f"https://raw.githubusercontent.com/{slug}/{commit}/{path}",
                "mutable or incorrect upstream locator")
        utc(record["lookup_timestamp"], identity)
        require(record["lookup_timestamp"] == LOOKUP_TIMES[identity], "frozen blob lookup timestamp")
        require(record["lookup_method"] == "HTTPS immutable raw source; Git blob SHA-1 and SHA-256 recomputed",
                "blob lookup method")
    for record in ordered(value["upstream_excerpts"], list(EXCERPT_IDENTITIES), "upstream_excerpts"):
        exact(record, ["id", "blob", "line_start", "line_end", "text"], "upstream excerpt")
        blob, first, last, digest = EXCERPT_IDENTITIES[record["id"]]
        require(type(record["line_start"]) is int and type(record["line_end"]) is int and
                (record["blob"], record["line_start"], record["line_end"]) == (blob, first, last), "excerpt range/identity")
        require(type(record["text"]) is str and len(record["text"].splitlines()) == last-first+1 and
                hashlib.sha256(record["text"].encode()).hexdigest() == digest, "reviewed immutable source excerpt drift")

    positions = {}
    for record in ordered(value["current_steps"], list(STEP_IDENTITIES), "current_steps"):
        exact(record, ["id", "group", "source", "function_start", "function_end", "fragment", "line_start",
                       "line_end", "return_handling", "consequence"], "current step")
        group, path, begin, end, fragment, handling = STEP_IDENTITIES[record["id"]]
        require((record["group"], record["source"], record["function_start"], record["function_end"],
                 record["fragment"], record["return_handling"]) == (group, path, begin, end, fragment, handling),
                "source operation/return handling drift")
        require(type(record["consequence"]) is str and
                hashlib.sha256(record["consequence"].encode()).hexdigest() == STEP_CONSEQUENCES[record["id"]],
                "reviewed operation consequence drift")
        text = sources[path].decode()
        start = text.index(begin)
        stop = text.index(end, start) if end else len(text)
        position = text.find(fragment, positions.get(group, start), stop)
        require(position >= 0, f"exact ordered source operation missing: {record['id']}")
        positions[group] = position + len(fragment)
        require(type(record["line_start"]) is int and type(record["line_end"]) is int and
                record["line_start"] == text[:position].count("\n")+1 and
                record["line_end"] == text[:position+len(fragment)].count("\n")+1, "source line correspondence")

    row_keys = {
        "claims": ["id", "classification", "evidence", "statement"],
        "failure_windows": ["id", "classification", "evidence", "current_consequence", "hardware_observation"],
        "alternatives": ["id", "selected", "description", "decisions"],
        "decision_gates": ["id", "status", "question"],
        "future_validation_gates": ["id", "requirement"],
        "searches": ["id", "method", "outcome", "limitation"],
    }
    known_evidence = set(SOURCE_IDENTITIES) | set(BLOB_IDENTITIES) | set(STEP_IDENTITIES) | {
        row[0] for row in REVIEWED_RECORDS["claims"]}
    gate_ids = {row[0] for row in REVIEWED_RECORDS["decision_gates"]}
    for section, contracts in REVIEWED_RECORDS.items():
        for record, (identity, digest) in zip(ordered(value[section], [r[0] for r in contracts], section), contracts):
            exact(record, row_keys[section], identity)
            if section in ("claims", "failure_windows"):
                require(record["classification"] in ("SOURCE_BACKED", "INFERRED", "UNKNOWN"), "claim classification")
                refs = record["evidence"]
                require(type(refs) is list and refs and all(type(r) is str and r in known_evidence for r in refs)
                        and len(set(refs)) == len(refs), "exact nonduplicate evidence references required")
            if section == "failure_windows":
                require(record["hardware_observation"] == "UNKNOWN", "no physical outcome inferred")
            if section == "alternatives":
                require(record["selected"] is False, "no recovery alternative selected")
                refs = record["decisions"]
                require(type(refs) is list and refs and all(type(r) is str and r in gate_ids for r in refs)
                        and len(set(refs)) == len(refs), "alternative decision gates")
            if section == "decision_gates":
                require(record["status"] == "UNRESOLVED_H3_NOT_SELECTED", "future authority remains unresolved")
            # Seal each reviewed evidence claim, not the entire fixture; schema,
            # references, source identity/order and authority are checked separately.
            require(seal(record) == digest, f"reviewed evidence or classification drift: {identity}")
    require(value["future_cut_points"] == list(STEP_IDENTITIES) + ["wrapper_truncate_sync", "autoformat"],
            "complete ordered future fault cut points")
    exact(value["research_limits"], list(LIMITS), "research limits")
    require(all(type(value["research_limits"][k]) is type(expected) and
                value["research_limits"][k] == expected for k, expected in LIMITS.items()), "non-authority/nonclaim boundary")


def validate_git_sources(root: Path = ROOT) -> None:
    # One local read-only object query. No refs other than the immutable source
    # base are needed; no network, ignored cache, or device path is consulted.
    output = subprocess.check_output(["git", "ls-tree", BASE, "--", *SOURCE_IDENTITIES], cwd=root, text=True)
    actual = {}
    for line in output.splitlines():
        metadata, path = line.split("\t", 1)
        mode, kind, blob = metadata.split()
        actual[path] = (mode, kind, blob)
    require(actual == {p: ("100644", "blob", blob) for p, (blob, _) in SOURCE_IDENTITIES.items()},
            "immutable repository base source objects unavailable or drifted")


def coverage(value: dict) -> str:
    out = ["<!-- persistence-coverage:start -->", "| Step | Handling | Source |", "| --- | --- | --- |"]
    for row in value["current_steps"]:
        out.append(f"| `{row['id']}` | {row['return_handling']} | `{row['source']}:{row['line_start']}` |")
    out += ["", "| Failure window | Classification | Current consequence |", "| --- | --- | --- |"]
    for row in value["failure_windows"]:
        out.append(f"| `{row['id']}` | {row['classification']} | {row['current_consequence']} |")
    out += ["", "| Future H3 decision | Exact question |", "| --- | --- |"]
    for row in value["decision_gates"]:
        out.append(f"| `{row['id']}` | {row['question']} |")
    return "\n".join(out + ["<!-- persistence-coverage:end -->"])


def validate_doc(text: str, value: dict) -> None:
    require(text.count("<!-- persistence-coverage:start -->") == 1 and
            text.count("<!-- persistence-coverage:end -->") == 1 and coverage(value) in text,
            "document coverage table must match reviewed fixture")
    for phrase in (BASE, "EVIDENCE_COMPLETE_IMPLEMENTATION_NOT_AUTHORIZED", "Single-byte File::read()",
                   "buffered reads report counts or zero", "torn program/erase", "No filenames",
                   "Nunchuk stays NOT_TESTED", "root cause unproven", "not whole SaveConfig atomicity"):
        require(phrase in text, f"required evidence caveat absent: {phrase}")


def adversarial(value: dict, sources: dict[str, bytes]) -> int:
    tests = []
    def changed(path: tuple, replacement: object) -> dict:
        candidate = copy.deepcopy(value)
        current = candidate
        for key in path[:-1]:
            current = current[key]
        current[path[-1]] = replacement
        return candidate
    for path, replacement in [
        (("schema_version",), True), (("status",), "DONE"),
        (("selected_recovery_mechanism",), "temp_and_rename"),
        (("research_base_commit",), BASE[:8]),
        (("repository_sources", 0, "blob"), "0"*40),
        (("repository_sources", 0, "path"), "config.bin"),
        (("repository_sources", 0, "mode"), "120000"),
        (("platform_selector", "fragment"), "framework-arduinopico#latest"),
        (("upstream_repositories", 0, "commit"), "0"*40),
        (("upstream_repositories", 0, "commit"), "32e74d0"),
        (("upstream_repositories", 0, "repository"), "https://github.com/untrusted/fork.git"),
        (("upstream_repositories", 1, "parent_gitlink", "commit"), "0"*40),
        (("upstream_repositories", 0, "lookup_timestamp"), "2026-99-99T00:00:00+00:00"),
        (("upstream_blobs", 0, "immutable_url"), "https://raw.githubusercontent.com/earlephilhower/arduino-pico/3.6.3/.gitmodules"),
        (("upstream_blobs", 0, "type"), "commit"),
        (("upstream_blobs", 0, "blob"), "0"*40),
        (("upstream_excerpts", 0, "text"), "invented guarantee\n"),
        (("current_steps", 0, "fragment"), "invented();"),
        (("current_steps", 0, "return_handling"), "CHECKED"),
        (("current_steps", 0, "line_start"), True),
        (("current_steps", 0, "consequence"), "guaranteed power-loss safety"),
        (("claims", 8, "classification"), "SOURCE_BACKED"),
        (("claims", 0, "evidence"), ["missing"]),
        (("claims", 0, "evidence"), ["save.size", "save.size"]),
        (("failure_windows", 0, "hardware_observation"), "PASS"),
        (("failure_windows", 2, "classification"), "SOURCE_BACKED"),
        (("alternatives", 0, "selected"), True),
        (("alternatives", 0, "decisions"), []),
        (("decision_gates", 0, "status"), "APPROVED"),
        (("research_limits", "hardware_tested"), True),
        (("research_limits", "checker_network_access"), 0),
        (("research_limits", "nunchuk"), "PASS"),
        (("future_cut_points",), []),
    ]:
        tests.append((str(path), changed(path, replacement)))
    for section in ("repository_sources", "upstream_blobs", "current_steps", "failure_windows", "decision_gates"):
        tests.append((f"missing {section}", changed((section,), value[section][1:])))
        tests.append((f"duplicate {section}", changed((section,), value[section]+[value[section][0]])))
    tests.append(("wrong operation order", changed(("current_steps",), value["current_steps"][::-1])))
    extra = copy.deepcopy(value); extra["unexpected"] = True
    tests.append(("unknown field", extra))
    extra = copy.deepcopy(value); extra["upstream_blobs"][0]["unexpected"] = True
    tests.append(("unknown nested field", extra))
    missing = copy.deepcopy(value); del missing["research_limits"]
    tests.append(("missing field", missing))
    for name, candidate in tests:
        try:
            validate(candidate, sources)
        except ResearchError:
            continue
        raise ResearchError(f"negative fixture accepted: {name}")
    tampered = dict(sources)
    first = next(iter(sources)); tampered[first] += b"\n"
    try:
        validate(value, tampered)
    except ResearchError:
        pass
    else:
        raise ResearchError("current source mutation accepted")
    for text in ('{"schema_version":1,"schema_version":1}', '{"nested":{"id":1,"id":2}}'):
        try:
            load_text(text)
        except ResearchError:
            continue
        raise ResearchError("duplicate JSON key accepted")
    for text in (coverage(value).replace("IGNORED", "CHECKED", 1), ""):
        try:
            validate_doc(text, value)
        except ResearchError:
            continue
        raise ResearchError("drifted/missing document coverage accepted")
    return len(tests) + 5


def main() -> int:
    try:
        value = load_text(FIXTURE.read_text(encoding="utf-8"))
        sources = source_bytes()
        validate(value, sources)
        validate_git_sources()
        validate_doc(DOC.read_text(encoding="utf-8"), value)
        count = adversarial(value, sources)
        print(f"glyph_current_config_persistence_recovery_research: PASS; {len(STEP_IDENTITIES)} ordered steps; "
              f"{len(BLOB_IDENTITIES)} immutable upstream blobs; {count} negative cases; H1 research only")
        return 0
    except (OSError, ValueError, subprocess.CalledProcessError) as exc:
        print(f"glyph_current_config_persistence_recovery_research: FAIL: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
