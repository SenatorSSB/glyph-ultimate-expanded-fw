# Prepare tested USB gamepad source for first-beta canonical integration

State: PREPARED_ONLY / OWNER_AUTHORIZATION_REQUIRED. No canonical update performed.
Expected live canonical: `59870835e7cd8e7c52bd3742e4910a7083cd21f5`.
Expected candidate/build-evidence ref: `codex/final-usb-gamepad-enumeration` at
`ebde1447f5cf348b3af82240ebd95445b44cb888`. Proposed target is the exact reviewed,
published `codex/final-usb-gamepad-hardware-acceptance` tip returned in the final
owner handoff. Resolve it once and pin the full SHA; do not integrate a later moving tip.
Tested production source remains dcf6e295, tested source tree a7731388, tested UF2
2c77e2b7 (all full identities in [freeze proposal](BETA_FREEZE_PROPOSAL.json)).

Ancestry-preserving fast-forward is preferred only while the live canonical equals the
expected base and is an ancestor of the pinned reviewed acceptance tip. Stop on drift,
divergence, source/build difference, dirty checkout or unexpected tip. Never rebuild,
rebase/reimplement the candidate, force-push or create a new merge decision here.

After separate owner authorization, use a clean checkout where configurator is not
checked out elsewhere. Replace ACCEPTED_SHA with the full reviewed publication SHA
from this handoff, then run these commands. This block is instructions, not execution:

```bash
set -eu
ACCEPTED_SHA=REPLACE_WITH_REVIEWED_PUBLICATION_SHA
EXPECTED_BASE=59870835e7cd8e7c52bd3742e4910a7083cd21f5
test -z "$(git status --porcelain)"
git fetch origin configurator codex/final-usb-gamepad-enumeration codex/final-usb-gamepad-hardware-acceptance
test "$(git rev-parse origin/configurator)" = "$EXPECTED_BASE"
test "$(git rev-parse origin/codex/final-usb-gamepad-enumeration)" = ebde1447f5cf348b3af82240ebd95445b44cb888
test "$(git rev-parse origin/codex/final-usb-gamepad-hardware-acceptance)" = "$ACCEPTED_SHA"
git merge-base --is-ancestor "$EXPECTED_BASE" "$ACCEPTED_SHA"
git rev-list --left-right --count "$EXPECTED_BASE...$ACCEPTED_SHA"
for revision in $(git rev-list dcf6e29589f558a95c021bef491578f87e41750f.."$ACCEPTED_SHA"); do
  git diff --exit-code dcf6e29589f558a95c021bef491578f87e41750f "$revision" -- . ':!docs/**'
done
git switch configurator
test "$(git rev-parse HEAD)" = "$EXPECTED_BASE"
git merge --ff-only "$ACCEPTED_SHA"
git push origin HEAD:refs/heads/configurator
git ls-remote origin refs/heads/configurator
```

Run sequentially and STOP on any nonzero result; do not paste through failed guards.
A nonempty status is a stop even though status itself exits0. Before publication rerun
full exact critical/non-doc mode/blob/path and329 production-manifest correspondence
as recorded in SOURCE_EQUIVALENCE.json; the diff guard is a concise additional check,
not authorization to omit that proof. Ordinary push rejects concurrent non-fast-forward
publication. Verify live canonical equals ACCEPTED_SHA after any separately authorized
push. Do not tag, publish a beta or activate freeze automatically.
