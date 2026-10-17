"""Pinned, insertion-only private-DCD diagnostic source transform.

The pristine CRLF bytes, including the complete MIT notice, are retained. No
installed package is modified; removing just the added lines recovers the pin.
"""
from hashlib import sha256
from pathlib import Path
import re

PINNED_SHA256 = "92a74cc04eef498a9523b3980c4b6b704990bff40531e23bb7ca490dd3358b12"
PRISTINE_RELATIVE = "vendor/diagnostics/tinyusb-0.16.0/rp2040/dcd_rp2040.c"
INSTALLED_RELATIVE = "libraries/Adafruit_TinyUSB_Arduino/src/portable/raspberrypi/rp2040/dcd_rp2040.c"
GENERATED_RELATIVE = ".pio/rt2-private-dcd/dcd_rp2040.c"
MARKERS = ("STATUS", "RETURN")
HEADER = '#include "core/RecoveryPrivateDcdMarkers.h"\r\n'
INITIAL_READ = "  uint32_t const status = usb_hw->ints;\r\n"
INITIAL_CALL = "  GlyphDcdPrivateStatus(status);\r\n"
LATE_READ = "  uint32_t const late_status = usb_hw->ints;\r\n"
RETURN_CALL = "  GlyphDcdPrivateReturn(status, late_status);\r\n"


def verify_pin(data, label="source"):
    actual = sha256(data).hexdigest()
    if actual != PINNED_SHA256:
        raise ValueError(f"{label}: pinned DCD SHA-256 mismatch: {actual}")


def _once(data, old, new):
    old, new = old.encode(), new.encode()
    if data.count(old) != 1:
        raise ValueError(f"expected one exact insertion anchor: {old!r}")
    return data.replace(old, new, 1)


def handler_text(source):
    text = source.decode()
    begin = text.index("static void __tusb_irq_path_func(dcd_rp2040_irq)(void)")
    end = text.index("\r\n#define USB_INTS_ERROR_BITS", begin)
    return text[begin:end]


def _transform_source(pristine):
    verify_pin(pristine, "pristine source")
    data = _once(pristine, '#include "device/dcd.h"\r\n',
                 '#include "device/dcd.h"\r\n' + HEADER)
    data = _once(data, INITIAL_READ, INITIAL_READ + INITIAL_CALL)
    anchor = '    panic("Unhandled IRQ 0x%x\\n", (uint) (status ^ handled));\r\n  }\r\n'
    return _once(data, anchor, anchor + LATE_READ + RETURN_CALL)


def patch_source(pristine):
    data = _transform_source(pristine)
    validate_patched(data)
    return data


def validate_patched(data):
    """Exact inverse pin and transform reject all changed USB behavior/placement."""
    body = handler_text(data)
    first = ("static void __tusb_irq_path_func(dcd_rp2040_irq)(void)\r\n{\r\n"
             + INITIAL_READ + INITIAL_CALL)
    if not body.startswith(first):
        raise ValueError("private handler must begin with original S0 then exact local publication")
    if not body.endswith(LATE_READ + RETURN_CALL + "}\r\n"):
        raise ValueError("S1 read and return publication must be final normal-return statements")
    if body.count("usb_hw->ints") != 2:
        raise ValueError("private handler requires exactly original S0 and diagnostic S1 reads")
    stripped = data
    for statement in (INITIAL_CALL, LATE_READ, RETURN_CALL, HEADER):
        if stripped.count(statement.encode()) != 1:
            raise ValueError("missing, modified or duplicate diagnostic statement: " + statement.strip())
        stripped = stripped.replace(statement.encode(), b"", 1)
    verify_pin(stripped, "source after removing diagnostic lines")
    if _transform_source(stripped) != data:
        raise ValueError("private diagnostic differs from exact insertion-only S0/S1 transform")


def prepare(root, installed):
    pristine = (Path(root) / PRISTINE_RELATIVE).read_bytes()
    verify_pin(Path(installed).read_bytes(), "installed framework source")
    patched = patch_source(pristine)
    generated = Path(root) / GENERATED_RELATIVE
    generated.parent.mkdir(parents=True, exist_ok=True)
    if not generated.exists() or generated.read_bytes() != patched:
        generated.write_bytes(patched)
    return generated, patched


def validate_routing(installed, expected, seen, original_object_present=False):
    if Path(installed).resolve() != Path(expected).resolve() or seen != 1 or original_object_present:
        raise ValueError("private DCD routing requires exactly one replacement and no original object")
