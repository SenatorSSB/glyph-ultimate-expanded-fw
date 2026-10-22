# GP_NATIVE_002_RECOVERY_V1 — read-only preflight approval packet

Prepared only. No device I/O has been executed by this repair run. Treat current
postfailure state as UNKNOWN. Explicit owner approval and identification of the
same physical Mk6, its current connection/backend and explicit current CDC port
are required before this packet executes. Do not blind-probe ports or create a
host disconnect/no-poll condition. No flash, cleanup, CREATE/UPDATE/DELETE,
Config SET, restoration, reset command or fixture recreation belongs here.

## Frozen evidence and expected inventory

Failed exact source4898951994bcabcaef2846145de2922a674656f8 and
UF2 SHA2567ab99a2f4461c5002c9f71b29f3b7bfe9c87f404970ecd3048e73f8ed885a81e
remain unchanged. Historical source-free failure publication is3a7a8174.
Twenty owned fixtures IDs28–47 are expected retained. SEL01 is ID28/r1/schema5;
SEL20 is ID47/r1/schema5. Earlier owner XInput output observations were LF1
(53,0)/(72,0), release(0,0). Those observations are not current identity or a
GameCube hidden-field oracle. Original record wrappers/directory metadata and
Config must be compared against the exact owner-held pre-campaign backups and
fixture receipts, not recreated from names or inferred from recovery.

## Bounded authorized read sequence after approval

1. Owner identifies unit and already available connection/backend. Preserve
   pre-existing private backups; create a fresh private run directory. Record
   timestamp, source/tool identities and known installed firmware identity.
   If read access requires changing route or reconnecting, stop for a concrete
   owner-approved connection step before proceeding; no implicit reconfiguration.
2. Use existing identity-only reader in its actual supported context, once.
   Capture raw response and decoded active ID/revision/schema/name/hash/backend.
   GameCube identity where unsupported remains UNKNOWN; no inference from USB.
3. Through an owner-established Configurator connection only, read current
   Config with existing glyph_serial_config_tool.py --read --backup-out and
   preserve the exact returned API/protobuf bytes plus decoded JSON and hashes.
   Do not use the unrelated dirty root-checkout tool; use exact reviewed repair
   tool source unchanged from48989519. The read may not claim raw filesystem
   Config integrity beyond what the existing API returns.
4. Run one production STATUS, then paginated LIST (page-size8; stop at actual
   directory completion, bounded by64 entries), using
   glyph_profile_store_production_tool.py with explicit --port, --journal-out,
   --output. READ each listed ID once, at most64, preserving full wrappers and
   returned identity/generation metadata. No operation in MUTATIONS is allowed.
   A failed/timeout/non-OK read stops; do not retry or manufacture completion.
5. Offline compare all original records against the retained pre-campaign full
   wrappers, revisions, IDs, names, ranks and payloads. Compare fixture IDs28–47
   against exact creation receipts. Compare current Config against last known
   approved selector destination, allowing only the explicitly exercised
   reference/default-mode/default-backend fields and checked publication
   metadata documented by the existing tools. Determine whether the final
   failed transition committed; either known prior or intended final destination
   needs explicit adjudication against receipts. Do not call an unknown state
   expected merely because both destinations are syntactically valid.
6. Hash all raw backups, manifests and journals and retain them privately.
   Publish only hashes/bounded assessment; original Config and profile bodies
   and device identifiers remain private. No overwrite of old evidence.

## Gate before repaired installation

Any missing record, changed original wrapper/revision, unexpected Config field,
identity mismatch, fenced/uncertain storage, non-OK result or insufficient exact
backup stops for owner adjudication. No automatic recovery, restore, deletion,
fixture cleanup or flash follows. A complete matching readback is prerequisite
to the separate exact repaired candidate approval packet. This packet itself is
not approval to install any firmware, nor evidence that readback has passed.
