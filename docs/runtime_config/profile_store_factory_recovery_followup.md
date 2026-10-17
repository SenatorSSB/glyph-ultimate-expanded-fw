# Factory recovery artifact follow-up

Item: **FACTORY_RECOVERY_ARTIFACT_REQUIRED**.
Status: **NONEXECUTING FOLLOW-UP — NOT IMPLEMENTED**.
Authority: direct owner `e1c7a932-d829-4a8a-ab7d-c42e6144cd0e`, **2026-10-18**.

Purpose: provide one verified Fresh/Factory Recovery artifact and procedure,
clearly distinct from an ordinary firmware update that preserves profiles.
Physical BOOTSEL/RPI-RP2 entry is owner-verified; persistent-state erasure and a
factory artifact are not. Ordinary UF2 installation is **not assumed to erase
LittleFS**.

A later bounded work order must establish:

1. Entry through the observed recessed physical BOOTSEL button and RPI-RP2 ROM
   bootloader, without depending on application startup or RT2.
2. An exact known-good firmware artifact and source/artifact custody.
3. Explicit intentional reset/erasure of **both ProfileStore and Config**,
   including relevant migration/root metadata, using source-backed behavior.
4. Restoration of known defaults and verified clean normal startup.
5. Clear destructive-loss instructions and a visible distinction from the
   ordinary profile-preserving update process.

Acceptance requires reviewable source/erase semantics, an exact artifact and a
separately authorized physical procedure with appropriate preservation/stop
rules. Do not construct an erase command from assumed UF2 behavior. This item
adds no flashing automation, device write, schema change or controller action.

This is one small safety deliverable, not another blocker on ordinary
ProfileStore implementation. It becomes a public-shipping safety gate when the
chapter is otherwise ready to ship and the product relies on destructive ROM
recovery as its catastrophic fallback. Current chapter **NOT DONE**, public
release human-owned, and [manual RT2 remains deferred](profile_store_rt2_deferred_closure.md).
The current reconciliation records this nonexecuting item only; implementation
requires separate bounded authority.
