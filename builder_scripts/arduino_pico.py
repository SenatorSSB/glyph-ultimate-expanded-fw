import subprocess

Import("env")


def before_build():
    subprocess.run(["git", "config", "--global", "core.longpaths", "true"])

    c_hash = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()
    proc = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)

    dirty = False
    if proc.stdout == None or len(proc.stdout) > 3:
        dirty = True

    if dirty:
        c_hash += "-DIRTY"
    
    version_name = "\\\"" + c_hash + "\\\""

    env.Append(CPPDEFINES=[
        ("FIRMWARE_VERSION", version_name)
    ])

before_build()
