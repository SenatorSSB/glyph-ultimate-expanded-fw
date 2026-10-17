"""Only strict Mk6 candidates interpose seven read-only USB observation wrappers."""
Import("env")
DEFINES=env.ParseFlags(env.get("BUILD_FLAGS",[])).get("CPPDEFINES",[])
if any(isinstance(item,(tuple,list)) and item[0]=="GLYPH_STRICT_HARDENING_CANDIDATE" and str(item[1])=="1" for item in DEFINES):
    env.Append(LINKFLAGS=["-Wl,--wrap="+name for name in (
        "tud_control_xfer","dcd_set_address","dcd_edpt0_status_complete",
        "tud_task_ext","usbd_control_reset","user_irq_claim_unused","_Z23TinyUSB_Port_InitDeviceh")])
