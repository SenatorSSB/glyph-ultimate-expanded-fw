I select Option 1: retain the broader currently accepted filesystem support domain.
GP-NATIVE-001 must preserve compatibility with filesystem states currently admitted by the existing firmware, including unrelated directories and applicable pending orphan/PENDING_MOVE recovery states.
Do not narrow the support contract to a closed firmware-owned flat-file history.
Requirements
1. Preserve the existing supported filesystem, ProfileStore, checked-storage, recovery, and transactional semantics.
2. Do not introduce a requirement that an existing controller prove a pristine filesystem history before using its existing supported ProfileStore functionality.
3. Do not silently refuse, erase, reformat, quarantine, or reinterpret previously supported states merely to eliminate a difficult stack path.
4. Distinguish genuinely supported states from malformed, corrupt, or already unsupported states. This direction does not require accepting arbitrary filesystem corruption.
5. Retain the existing 2,048-byte per-core stack limits, static RAM budget, filesystem partition, recovery reserve, and storage capacity constraints. No limit increase is authorized.
Required continuation
Treat the resource gate as an engineering problem requiring a source-grounded solution, not as permission to reduce compatibility.
First establish exact feasible call-chain and interrupt co-liveness using the final linked source/ELF. Exclude only paths proven mutually unreachable, not paths that are merely unlikely.
Then investigate bounded lifetime, frame-isolation, call-structure, and workspace-reuse approaches that preserve existing behavior.
The previous finite probes and their negative results remain evidence. Do not simply repeat unsuccessful approaches without a materially different hypothesis.
For any source change outside the current READY order, obtain the necessary bounded Curator authorization and independent review.
Acceptance
The resource gate remains open until there is a defensible complete stack/resource argument for the supported execution paths within the unchanged limits, together with all directly applicable validation.
Runtime watermark observations may supplement this proof, but cannot substitute for unresolved feasible static paths.
If the broader support domain genuinely cannot be implemented within the existing limits, return a concrete engineering finding with measured or source-proven constraints, available alternatives, and their compatibility implications. Do not autonomously narrow the supported domain.
Authority boundaries
This is a substantive owner decision resolving the filesystem-domain choice.
It does not authorize flashing, controller mutation, filesystem erasure, resource-limit increases, or hardware acceptance.
Preserve the exact existing failed/incomplete evidence, candidate identity, build custody, and governance state.
Proceed autonomously through authorized analysis, implementation, testing, review, and governance. Return only at a genuine new substantive blocker or the next required hardware approval gate.
