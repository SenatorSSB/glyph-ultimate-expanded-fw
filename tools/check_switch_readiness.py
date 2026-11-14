"""Run the production Switch backend and IntegratedDisplay with a deterministic host endpoint."""
from pathlib import Path
import os
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
PARENT = "84556d904f067bda5a101e6297689239ecd04aae"
BACKEND = "HAL/pico/src/comms/NintendoSwitchBackend.cpp"
FIXTURE = Path("tools/fixtures/switch_readiness")


def build(source, binary):
    includes = [FIXTURE / "include", "tools/fixtures/stage_c_ultimate_profiles_host/include",
                "include", "HAL/pico/include", "tools/fixtures/gp_config012_button_host/generated",
                "tools/fixtures/gp_config012_button_host/nanopb"]
    subprocess.run([os.environ.get("CXX", "c++"), "-std=gnu++17", "-fshort-enums", "-DNDEBUG",
                    *["-I" + str(path) for path in includes], source, FIXTURE / "main.cpp",
                    "src/core/CommunicationBackend.cpp", "src/core/InputSource.cpp",
                    "src/comms/IntegratedDisplay.cpp", "-o", binary], check=True, cwd=ROOT)


def main():
    with tempfile.TemporaryDirectory() as directory:
        folder = Path(directory)
        executable = folder / "fixture"
        original = folder / "original.cpp"
        original.write_bytes(subprocess.check_output(["git", "show", f"{PARENT}:{BACKEND}"], cwd=ROOT))
        build(original, executable)
        subprocess.run([executable, "ready"], timeout=5, check=True)
        try:
            subprocess.run([executable, "stall"], timeout=2, capture_output=True, check=True)
        except subprocess.TimeoutExpired as error:
            if b"stalled before FAST" not in (error.stdout or b""):
                raise RuntimeError("parent did not reach the targeted stall") from error
        else:
            raise RuntimeError("parent unexpectedly returned")
        print("PASS original ready bytes and pre-FAST stall negative control", flush=True)
        build(BACKEND, executable)
        subprocess.run([executable], timeout=5, check=True)


if __name__ == "__main__":
    main()
