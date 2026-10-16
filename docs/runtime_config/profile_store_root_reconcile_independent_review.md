# Independent root-reconciliation source review

Reviewer: fresh independent native subagent `/root/fresh_root_route_review`,
2026-10-16. The reviewer inspected source, tests and prepared procedures, ran
independent host checks, and authored only this review. No implementation edit,
device access, controller command, reset, flashing or hardware observation.

Verdict: **CONDITIONAL SOURCE APPROVAL; no actionable source finding.** This is
approval to proceed through the owner-authorized exact candidate build/custody
and handoff gates. Final handoff approval remains conditional on the exact
committed build, resource/ABI/frame evidence, preserved artifact custody and
the generated-input predecessor regression. Hardware remains NOT_TESTED;
canonical merge is not approved.

## Inspected identity

- Checkout: `/private/tmp/glyph-profile-store-root-reconcile-fault`.
- Frozen HEAD/direct parent: `4ee63e26c912a0954ab9d7028a70a04ff80ced8d`.
- Frozen parent tree: `317b262f4a980e1762d02faa1b2911963e3632b9`.
- Recorded canonical base: `6b73a7c507f35c111745c6bdd341618b490cbdcd`.
- Inspected pre-review worktree tree: `db4cf62293239a0f501912ccb83fd535f2656ec7`.
  Computed read-only using Git blob/tree encoding over tracked and nonignored
  untracked files; excludes this subsequently authored review and ignored logs.
- Tracked binary diff against frozen HEAD SHA-256:
  `bc5eb8245c08554a2b62bbc914451ffa08ad491eae14df96e1ea7f5f63781049`.
  Untracked reviewed docs/tests are covered by the tree identity above.

Exact reviewed implementation/proof blob identities:

| Path | Git blob |
| --- | --- |
| `HAL/pico/src/comms/ConfiguratorBackend.cpp` | `2ea1fd60ddd34b1de341dc0a2c9becb21151056f` |
| `include/core/ProfileStoreFaultControls.hpp` | `286eaf0f011e91e2ed5413864b2e1d7a716fde54` |
| `schema/haybox/config.proto` | `2740edf3c2d8ddf9929997871a8728d21d442757` |
| `tools/glyph_profile_store_candidate_tool.py` | `e40dbcc5ca6826faecbb4cbce21f64d54ab55b16` |
| `tools/check_glyph_profile_store_root_reconcile.py` | `6128833ebee1f29d2f122a86c43c0b1c9dd1ff01` |
| `tools/check_glyph_profile_store_reconcile_cli.py` | `1401e59e68ddf3760b414bec2ae2c7702787a8cb` |
| `tools/fixtures/profile_store_root_reconcile_host/harness.cpp` | `ec690692eabf0c31c57acb40183910b3b668d86a` |

The final fault-control comment correction was inspected and is documentation
only; executable bytes are unchanged from the independently exercised source.
The final commit must retain these reviewed blobs. This review is deliberately
precommit and does not invent a self-referential candidate SHA.

## Required answers

1. **Physical ordinary4ee ABORTED correct under v2: yes, source-consistent.**
   ARM prepares an inert rule. Frozen backend reconciliation occurs without
   activating it; phase3 with both healthy prior roots publishes the existing
   identity-only ABORTED checkpoint. The retained physical report therefore
   describes an invalid fault-test route, not a demonstrated product failure.
   I independently reproduced frozen behavior, but did not independently access
   the controller or adjudicate its current authoritative ID22 state.
2. **Ticket8 could affect ordinary QUERY: no.** Ordinary QUERY does not present
   the ticket or install the hook. Frozen QUERY with a ticket is invalid. The
   frozen host controls reproduce ABORTED with the ticket still pending/inert.
3. **Exactly one reconciliation under the new special ticket: yes.** The closed
   route bypasses the entire pre-dispatch reconciliation block and calls
   `QueryTransaction(token)` once. Its existing uncertain branch owns exactly
   one `ReconcileTransaction` invocation. This reads control and both roots;
   path2 excludes control and the one-shot rule fails the first root OpenRead.
4. **Immediate second healthy reconciliation in the same request: no.** After
   that call, the hook ends before traces44–46 and Config loading; there is no
   second store query/reconciliation. The existing UnknownOutcome maps to
   COMMIT_UNKNOWN. Physical filesystem bytes remain identical in both parity
   tests, with uncertainty/read-only/root-invalid flags retained.
5. **Restriction: yes.** Backend requires strict candidate, protocol2 QUERY,
   available storage, uncertain store and matching pending inert nonzero ticket;
   request identity then rejects zero token. The helper and immediate activation
   recheck require Root/OpenRead/Before/Fail/path2/skip0 exactly. Production and
   unsafe ticket/shape/version cases reject without activation. CLI additionally
   checks advertised candidate/protocol/fault-route capabilities and all shape
   fields, preserves an exclusive fsynced request/trace and sends once without
   retry. Exact Git/UF2 identity remains the separately pinned custody/operator
   contract; capability booleans are not cryptographic firmware identification.
6. **Ordinary QUERY/replay/mutation semantics unchanged: yes.** With no special
   predicate the prior flow is retained, including reconciliation, shared-token
   identity checks, stale-expectation replay and mutation admission. Additive
   response fields expose candidate diagnostics. Existing protocol and faulted
   mutation suites independently pass; STATUS/LIST/READ remain inert.
7. **Fault-free reboot preserves identity monotonicity: yes, within the actual
   source contract.** Both roots are reread; exactly G+1 records ABORTED, the
   attempted token/high-water and prior authoritative profile survive. Changed
   identity cannot execute, aborted CREATE's ID stays reserved, the next ID is
   greater, and another reboot does not add a checkpoint. Root0 failure can
   expose the older companion in RAM, so failed-read generation must be <=G,
   not equal to G. Authoritative revision R is restored on healthy remount.
   `Update` computes authoritative R+1; it does not globally reserve abandoned
   UPDATE revision labels. This repair makes no stronger revision claim.
8. **B1–B8 unaffected: yes at source/host scope.** ProfileStore, CheckedStorage,
   Persistence and ordinary routing remain unchanged from4ee; the predicate
   adds only the explicitly ticketed candidate QUERY path. Existing strict host,
   protocol and production Config suites pass independently. This is neither
   inherited hardware acceptance nor a new B1–B8 physical PASS.

## Independent checks and outstanding gates

All commands ran from the named candidate checkout; no serial device opened.

| Independent command | Actual result |
| --- | --- |
| `python3 tools/check_glyph_profile_store_root_reconcile.py --output-dir /private/tmp/glyph-root-reconcile-independent` | PASS, 28 cases: current24/frozen2/production2, ASan/UBSan, pinned LittleFS |
| `python3 tools/check_glyph_profile_store_reconcile_cli.py` | PASS, 19 preflight negatives, four orchestration cases, no retry, query receipt excluded from replay |
| `python3 tools/check_glyph_profile_store_strict_host.py` | PASS, 24 cases and four detected frozen production negative controls, ASan/UBSan |
| `python3 tools/check_glyph_profile_store_config_persistence.py` | PASS, 37 current production Persistence cases |
| `python3 tools/check_glyph_profile_store_strict_protocol.py` | PASS, protocol variants, actual backend RX and liveness protocol, 128 updates/1024 arm-loss cycles/7680 mixed frames |
| `git diff --check` | PASS |

The root suite explicitly tests trace failures42/43/44: scope exit always removes
the hook, does not publish a checkpoint and retains uncertain state. Its Config
mock rejects leaked hooks at load boundaries. Production Config outcome proof
comes from the separately exercised Persistence suite, not that mock.

Inspected executor regression report records19/20 PASS, with initial
`real_predecessor_config` FAIL because target generated inputs are absent.
Retain that failure and rerun after the exact committed target build; this review
does not relabel it PASS. Full global framework aggregate PASS is not claimed.
Exact candidate commit/tree/parent/live ref, committed-before-build proof,
resource/ABI/target frames and custody are still pending at this review snapshot.
The separate failed4ee adjudication and new hardware packet are prepared only.
Nunchuk NOT_TESTED. Root cause of broader historical anomalies remains unproven.
