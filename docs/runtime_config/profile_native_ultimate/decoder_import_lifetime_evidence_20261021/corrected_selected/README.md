# Corrected private lifetime proposal

The [selected proposal](PROPOSAL.md) and [correction record](CORRECTION.json)
preserve the same engineering hypothesis after independent scope review found
three defects in the original sealed packet. The [selected diff](selected-private.diff)
restores the whole backend suffix and migration-completion body, and explicitly
clears new dispatch metadata. The original failed packet remains separately
preserved; no old result is relabeled.

All283 sealed inputs were rehashed, and root replayed all91 component-summed
route totals and margins. The [body-diff audit](existing-body-diff-audit.json)
is an aid, not a C++ semantic proof. Both-ABI compilation/layout and limited
callback/selector regressions are engineering evidence only. Several resource
arrays equal2048; the alignment reserve and primitive/lifecycle conditions still
require actual final correspondence. No whole resource, new-source equivalence,
final build or hardware PASS is claimed here.

The [original child manifest](SEALED_MANIFEST.json) and
[compressed input archive](manifest.json) retain complete sources, attempts,
compiler commands, objects, outputs and correction chronology. Any production
implementation requires the independently adopted exact bounded amendment.
