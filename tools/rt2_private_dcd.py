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
MARKERS = ("STATUS", "SOF_DONE", "BUFF_DONE", "SETUP_TEST",
           "SETUP_ENTERED", "SETUP_POINTER_ACQUIRED", "PID_DONE", "BEFORE_EVENT",
           "AFTER_EVENT", "BEFORE_CLEAR", "AFTER_CLEAR", "RETURN")
HEADER = '#include "core/RecoveryPrivateDcdMarkers.h"\r\n'


def verify_pin(data, label="source"):
    actual = sha256(data).hexdigest()
    if actual != PINNED_SHA256:
        raise ValueError(f"{label}: pinned DCD SHA-256 mismatch: {actual}")


def _once(data, old, new):
    old, new = old.encode(), new.encode()
    if data.count(old) != 1:
        raise ValueError(f"expected one exact insertion anchor: {old!r}")
    return data.replace(old, new, 1)


def marker(name, value="0", indent="  "):
    if name == "STATUS":
        return f"{indent}GlyphDcdPrivateStatus({value});\r\n"
    return f"{indent}GlyphDcdPrivateMarker(GLYPH_DCD_PRIVATE_{name}, {value});\r\n"


def handler_text(source):
    text = source.decode()
    begin = text.index("static void __tusb_irq_path_func(dcd_rp2040_irq)(void)")
    end = text.index("\r\n#define USB_INTS_ERROR_BITS", begin)
    return text[begin:end]


def _transform_source(pristine):
    verify_pin(pristine, "pristine source")
    data = _once(pristine, '#include "device/dcd.h"\r\n',
                 '#include "device/dcd.h"\r\n' + HEADER)
    anchor = "  uint32_t const status = usb_hw->ints;\r\n"
    data = _once(data, anchor, anchor + marker("STATUS", "status"))
    anchor = "    dcd_event_sof(0, usb_hw->sof_rd & USB_SOF_RD_BITS, true);\r\n"
    data = _once(data, anchor, anchor + marker("SOF_DONE", indent="    "))
    anchor = "    hw_handle_buff_status();\r\n"
    data = _once(data, anchor, anchor + marker("BUFF_DONE", indent="    "))
    anchor = "  if ( status & USB_INTS_SETUP_REQ_BITS )\r\n  {\r\n"
    data = _once(data, anchor,
                 marker("SETUP_TEST", "(status & USB_INTS_SETUP_REQ_BITS) != 0") +
                 anchor + marker("SETUP_ENTERED", indent="    "))
    anchor = "    uint8_t const * setup = remove_volatile_cast(uint8_t const*, &usb_dpram->setup_packet);\r\n"
    data = _once(data, anchor, anchor + marker("SETUP_POINTER_ACQUIRED", indent="    "))
    anchor = "    reset_ep0_pid();\r\n"
    data = _once(data, anchor, anchor + marker("PID_DONE", indent="    "))
    anchor = "    dcd_event_setup_received(0, setup, true);\r\n"
    data = _once(data, anchor, marker("BEFORE_EVENT", indent="    ") + anchor +
                 marker("AFTER_EVENT", indent="    "))
    anchor = "    usb_hw_clear->sie_status = USB_SIE_STATUS_SETUP_REC_BITS;\r\n"
    data = _once(data, anchor, marker("BEFORE_CLEAR", indent="    ") + anchor +
                 marker("AFTER_CLEAR", indent="    "))
    anchor = '    panic("Unhandled IRQ 0x%x\\n", (uint) (status ^ handled));\r\n  }\r\n'
    data = _once(data, anchor, anchor + marker("RETURN"))
    return data


def patch_source(pristine):
    data = _transform_source(pristine)
    validate_patched(data)
    return data


def validate_patched(data):
    """Fail closed for every missing/reordered/modified marker or source byte."""
    body = handler_text(data)
    # Hard entry boundary: even a helper, barrier, atomic or marker before this
    # exact original read is forbidden. Do not infer safety from marker order.
    first = ("static void __tusb_irq_path_func(dcd_rp2040_irq)(void)\r\n{\r\n"
             "  uint32_t const status = usb_hw->ints;\r\n" + marker("STATUS", "status"))
    if not body.startswith(first):
        raise ValueError("private handler must begin with original INTS load then local STATUS marker")
    expected = list(MARKERS)
    found = re.findall(r"GlyphDcdPrivate(?:Status\((?=status\))|Marker\(GLYPH_DCD_PRIVATE_(\w+),)", body)
    found = [name or "STATUS" for name in found]
    if found != expected:
        raise ValueError(f"private marker order/count mismatch: {found}")
    stripped = re.sub(rb"^ *GlyphDcdPrivateStatus\(status\);\r\n", b"", data, flags=re.M)
    stripped = re.sub(rb"^ *GlyphDcdPrivateMarker\(GLYPH_DCD_PRIVATE_\w+, [^\r\n]*\);\r\n",
                      b"", stripped, flags=re.M)
    if stripped.count(HEADER.encode()) != 1:
        raise ValueError("private marker include missing or duplicate")
    stripped = stripped.replace(HEADER.encode(), b"", 1)
    verify_pin(stripped, "source after removing diagnostic lines")
    if marker("STATUS", "status") not in body or marker("SETUP_TEST", "(status & USB_INTS_SETUP_REQ_BITS) != 0") not in body:
        raise ValueError("marker must consume the actual private local status")
    if body.count("usb_hw->ints") != 1:
        raise ValueError("private handler must retain exactly one original status read")
    if _transform_source(stripped) != data:
        raise ValueError("private marker placement/arguments differ from exact insertion-only transform")


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
