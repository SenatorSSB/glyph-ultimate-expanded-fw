"""Verify one retained Mk6 candidate without opening any device."""
import argparse
import gzip
import hashlib
import json
import struct
from pathlib import Path


def verify(directory, expected_source):
    manifest = json.loads((directory / "manifest.json").read_text())
    if manifest["source"] != expected_source or len(expected_source) != 40:
        raise ValueError("candidate source differs")
    artifacts = {}
    for name, entry in manifest["files"].items():
        path = directory / entry["stored"]
        data = path.read_bytes()
        if path.suffix == ".gz":
            data = gzip.decompress(data)
        if len(data) != entry["bytes"] or hashlib.sha256(data).hexdigest() != entry["sha256"]:
            raise ValueError(f"artifact identity differs: {name}")
        artifacts[name] = data
    uf2 = artifacts["firmware.uf2"]
    binary = artifacts["firmware.bin"]
    count, remainder = divmod(len(uf2), 512)
    if remainder or count != (len(binary) + 255) // 256:
        raise ValueError("UF2 block count differs from binary")
    for block in range(count):
        offset = block * 512
        header = struct.unpack_from("<8I", uf2, offset)
        expected = (0x0A324655, 0x9E5D5157, 0x2000, 0x10000000 + block * 256,
                    256, block, count, 0xE48BFF56)
        payload = binary[block * 256:(block + 1) * 256].ljust(256, b"\x00")
        if (header != expected or uf2[offset + 32:offset + 288] != payload
                or struct.unpack_from("<I", uf2, offset + 508)[0] != 0x0AB16F30):
            raise ValueError(f"UF2 target, order or content differs: block {block}")
    if not artifacts["firmware.elf"].startswith(b"\x7fELF") or not artifacts["firmware.map"]:
        raise ValueError("missing linked artifact")
    return f"{expected_source}: {count} verified Mk6 UF2 blocks, {len(binary)} binary bytes"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    parser.add_argument("expected_source")
    args = parser.parse_args()
    print(verify(args.directory, args.expected_source))
