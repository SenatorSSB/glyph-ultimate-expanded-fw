# Controller ProfileStore selector: source audit

Owner-directed GP-NATIVE-002; isolated source parent
334fbd06e4541c120b0db423e5be7e112eb1f6f6, tree
0483dbb0cc8f7eb5a1c93cb1d91044f4d3dcf999. Live canonical verified
2026-10-22 as e43be478e1f267f422bb56d4619141885ac838b7 (default DNS failure,
network-enabled read-only retry succeeded). Canonical remains source-free for
this candidate. Existing root checkout edits are unrelated and preserved.

1. DefaultConfigMenu constructs Config rows; GlyphConfigMenu subsequently
   rebuilds that same page. The latter currently owns applicability filtering.
2. GlyphConfigMenu.cpp:33–49 treats empty applicable_backends as unrestricted;
   explicit lists match the current backend. A Keyboard row appears across
   USB routes and existing selection forces DInput. The shared selector policy
   must preserve that exception and hide Keyboard on non-USB routes.
3. glyph_overrides.hpp supplies thirteen bounded source-owned mode contexts;
   Ultimate admits XInput, DInput, Switch and GameCube. Native template rows
   (Ultimate + engine1) can be reused without one Config row per stored profile.
4. UltimateNativeProfile.cpp ContextDigest hashes ordered remapping/SOCD and
   mode identity, independently of profile reference/backend. Existing native
   twenty-profile fixture uses a shared context. There is no evidence requiring
   a new persisted preprocessing architecture.
5. ProfileStore::Read validates the body into the existing native candidate
   owner. Immediately ContextMatches(CandidateView(), row) can establish a
   compatible eligible pair. Activate must not be called during validation.
   Config validation alone does not establish context compatibility.
6. The old menu writes watchdog scratch, then backend_init saves during boot.
   ModeSelectionTransaction instead loads durable Config, updates the backend
   destination, validates and performs checked generation publication. Its
   committed destination marker prevents a second save during initialization.
7. Native selection must combine reference and destination in one checked
   publication. Reuse ConfigWriteCandidate and its unused embedded profile slot
   transiently; retain no additional profile body. Check store incarnation,
   read-only/recovery/uncertainty and persistence fence before proceeding.
8. A bounded menu-to-core0 request is necessary: menu controls run on core1,
   while existing checked storage/candidate owners belong to synchronous core0.
   The menu may enumerate metadata but must never run selection I/O itself.

EntryAt exposes directory order; Reorder changes rank without sorting. Order
native entries by rank with directory index as a stable tie-break. Names use
bounded copying. A virtual item accessor can retain the existing rendering and
scrolling with a compact stable-ID map rather than up to94 full MenuItems.
Empty-list control and render bounds must be fixed as part of this path.

Independent read-only source specialist: /root/selector_policy_audit. No
substantive architecture contradiction found. New source still requires READY
adoption, host/linked resource proof, fresh independent review, exact build and
owner-approved hardware packet. No physical or hardware PASS is asserted here.
