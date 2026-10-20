"""Mk6 retained diagnostic source label and external entry interception only."""
import subprocess
from pathlib import Path


def source_identity(root, runner=subprocess.run):
    def git(*args):
        result=runner(['git',*args],cwd=root,capture_output=True,text=True)
        if result.returncode: raise RuntimeError('native diagnostic Git verification failed')
        return result.stdout.strip()
    sha=git('rev-parse','HEAD')
    if len(sha)!=40 or any(c not in '0123456789abcdef' for c in sha):
        raise RuntimeError('native diagnostic requires complete source Git SHA')
    if git('status','--porcelain','--untracked-files=normal'):
        raise RuntimeError('native diagnostic requires clean committed source')
    # Match the existing build identity's hidden tracked-file integrity rule.
    import sys
    tools=str(Path(root)/'tools')
    if tools not in sys.path:sys.path.insert(0,tools)
    from glyph_tracked_worktree_integrity import tracked_worktree_divergence
    if tracked_worktree_divergence(root):raise RuntimeError('native diagnostic tracked source differs from HEAD')
    return sha


def configure(env):
    if env.subst('$PIOENV')!='glyph_mk6':return
    root=Path(env.subst('$PROJECT_DIR'));sha=source_identity(root)
    generated=Path(env.subst('$BUILD_DIR'))/'native_target_metrics';generated.mkdir(parents=True,exist_ok=True)
    values=','.join('0x'+sha[i:i+2] for i in range(0,40,2))
    text='#pragma once\n#include <cstdint>\nconstexpr uint8_t kNativeTargetSourceSha[20]={'+values+'};\nconstexpr uint16_t kNativeTargetSourceFlags=3;\n'
    header=generated/'native_target_source.hpp'
    if not header.exists() or header.read_text()!=text:header.write_text(text)
    env.Append(CPPPATH=[str(generated)],CPPDEFINES=[('GLYPH_NATIVE_TARGET_METRICS',1)],
               LINKFLAGS=['-Wl,--wrap=main','-Wl,--wrap=multicore_launch_core1'])


try:
    Import('env')
except NameError:
    pass
else:
    configure(env)
