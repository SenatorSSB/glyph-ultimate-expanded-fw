#!/usr/bin/env python3
"""Replay frozen B1-R2 component oracles against this repository's sources."""
import argparse, hashlib, json, os, pathlib, shlex, subprocess, sys, tempfile

HERE = pathlib.Path(__file__).resolve().parent / "fixtures/glyph_package_v1"
ROOT = pathlib.Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser()
p.add_argument('--repo', default=ROOT, type=pathlib.Path)
p.add_argument('--corpus', required=True, type=pathlib.Path)
p.add_argument('--cxx', default=os.environ.get('CXX', 'c++'))
p.add_argument('--python', default=sys.executable)
p.add_argument('--littlefs', type=pathlib.Path,
               help='LittleFS lib/littlefs directory; auto-detected in repo when omitted')
p.add_argument('--research-dir', type=pathlib.Path,
               help='read-only oracle adapter directory; defaults to sibling repository tools/research')
p.add_argument('--reference-root', type=pathlib.Path,
               help='read-only repository containing contracts/glyph-reference-v1; defaults to --repo')
p.add_argument('--build-dir', type=pathlib.Path)
a = p.parse_args()
repo, corpus = a.repo.resolve(), a.corpus.resolve()
research = (a.research_dir or corpus.parents[1]/'tools/research').resolve()
reference_root = (a.reference_root or corpus.parents[1]).resolve()
assert (repo/'include/core/ConfigWireValidator.hpp').is_file(), 'repo lacks package component sources'
assert (corpus/'source-manifest.json').is_file(), 'corpus must be the immutable glyph-package-v1 corpus'
assert (corpus/'proof/glyph_package_storage.py').is_file(), 'corpus proof package missing'
manifest = json.loads((corpus/'source-manifest.json').read_text())
assert manifest.get('status') == 'B1R2_SOURCE_CORRESPONDENCE', 'unexpected B1R2 corpus status'
assert manifest.get('accepted_pin') == 'a6e3bc885d46e2a7412ec697aa822bcd8c4ce495', 'unexpected accepted source pin'
tree = hashlib.sha256()
for path in sorted(x for x in corpus.rglob('*') if x.is_file() and '__pycache__' not in x.parts and x.suffix != '.pyc'):
    rel = path.relative_to(corpus).as_posix().encode(); blob = path.read_bytes()
    tree.update(len(rel).to_bytes(4, 'big')); tree.update(rel)
    tree.update(len(blob).to_bytes(8, 'big')); tree.update(blob)
assert tree.hexdigest() == '44824eba94344b04fbfce4dd9431d81c03ead6e00f365b63e4ec3882d2103d10', 'immutable B1R2 corpus tree hash mismatch'
print('B1R2 corpus identity PASS:', tree.hexdigest())
temporary = tempfile.TemporaryDirectory(prefix='glyph-package-components-') if a.build_dir is None else None
build = a.build_dir.resolve() if a.build_dir else pathlib.Path(temporary.name)
build.mkdir(parents=True, exist_ok=True)
inc = repo/'include'; src = repo/'src/core'
def run(cmd, **kwargs):
    print('+', shlex.join(map(str, cmd)), flush=True)
    subprocess.run(list(map(str, cmd)), check=True, **kwargs)
def compile_cpp(out, sources, extra=()):
    run([a.cxx, '-std=c++17', '-O1', '-Wall', '-Wextra', '-Werror', '-I', inc,
         *extra, *sources, '-o', out])

# Strict Config differential suite: immutable frozen oracle vectors, actual selected
# repository ConfigWireValidator.cpp, and the retained source-native oracle.
probe = build/'config-probe'
compile_cpp(probe, [HERE/'config_probe.cpp', src/'ConfigWireValidator.cpp'])
env = dict(os.environ, GLYPH_PACKAGE_REPO=str(reference_root), GLYPH_PACKAGE_CORPUS=str(corpus),
           GLYPH_PACKAGE_RESEARCH=str(research),
           CONFIG_WIRE_PROBE=str(probe), GLYPH_PACKAGE_TEST_OUTPUT=str(build), PYTHONDONTWRITEBYTECODE='1')
run([a.python, HERE/'verify_config.py'], env=env)

# Format controls compile the actual repository format implementation and compare
# the retained vector set against the independent immutable Python oracle.
shared_suffix = '.dylib' if sys.platform == 'darwin' else '.so'
shared_flags = ['-dynamiclib'] if sys.platform == 'darwin' else ['-shared', '-fPIC']
ffi = build/('format'+shared_suffix)
run([a.cxx, '-std=c++17', '-O1', '-Wall', '-Wextra', '-Werror', *shared_flags, '-I', inc,
     HERE/'format_ffi.cpp', src/'PackageStorageFormat.cpp', '-o', ffi])
portable = HERE/'verify_format.py'
env['GLYPH_PACKAGE_FORMAT_LIB'] = str(ffi)
run([a.python, portable], env=env)

# Differential storage/classifier replay uses the actual repository observer and
# format sources, with immutable oracle expectations and real source validators.
classifier = build/('classifier'+shared_suffix)
run([a.cxx, '-std=c++17', '-O1', '-Wall', '-Wextra', '-Werror', *shared_flags, '-I', inc,
     HERE/'classifier_ffi.cpp', src/'PackageNamespaceClassifier.cpp', src/'PackageStorageFormat.cpp', '-o', classifier])
env['GLYPH_PACKAGE_CLASSIFIER_LIB'] = str(classifier)
run([a.python, HERE/'verify_classifier.py'], env=env)

# The checked-storage harness is compiled against repository CheckedStorage and
# PackageStorageFence plus the selected pinned LittleFS sources. Four positive/
# negative state scenarios and two repaired adversarial controls are replayed.
lfs = a.littlefs.resolve() if a.littlefs else next((x for x in repo.glob('.platformio-home/**/lib/littlefs') if (x/'lfs.c').is_file()), None)
if lfs is None:
    print('GAP: LittleFS source not found; pass --littlefs', file=sys.stderr); raise SystemExit(2)
checked = repo/'HAL/pico/src/core/CheckedStorage.cpp'
fence = build/'fence-harness'
lo, lu = build/'lfs.o', build/'lfs_util.o'
run([os.environ.get('CC','cc'), '-std=c99', '-O1', '-DLFS_NAME_MAX=32', '-I', lfs, '-c', lfs/'lfs.c', '-o', lo])
run([os.environ.get('CC','cc'), '-std=c99', '-O1', '-DLFS_NAME_MAX=32', '-I', lfs, '-c', lfs/'lfs_util.c', '-o', lu])
compile_cpp(fence, [HERE/'fence_harness.cpp', checked, src/'PackageStorageFence.cpp', lo, lu],
            ['-DGLYPH_PACKAGE_V1=1', '-DGLYPH_CHECKED_STORAGE_TEST_MOUNT=1', '-DLFS_NAME_MAX=32', '-I', lfs])
for scenario in ('unclassified', 'failed-mount', 'healthy', 'revoked-dirty', 'sync-before', 'close-before'):
    run([fence, scenario])
print('PASS glyph_package_components; immutable corpus unchanged; hardware=NOT_TESTED')
