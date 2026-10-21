# Read-sum arithmetic correction,2026-10-21

I made a100-byte sum error in the earlier copy/read and exact-linked appendices. The listed linked frames and call edges were correct; their read lookup total was not.

88+16+80+96+152+72+64=**568**, not668. Adding read callback8 and ROM<=12 gives **588**, not688. Checked Stat's analogous sum is532, not632. Historical reports remain unchanged; this erratum supersedes those numbers and their downstream read sums.

Corrected source-accounting witnesses: existing Identity under Prepare **2068** (formerly2168), published Identity under Execute **2100** (formerly2200). Both still exceed2048 under their documented predicates; this is not a physical overflow observation. Corrected conservative uppers: Identity Prepare2136, Identity Execute2168; direct hash Prepare1856, direct hash Execute1888; hypothetical measured Identity8-wrapper Execute1896. The smaller Identity-only lifetime hypothesis therefore retains its justification, with152 bytes conditional margin rather than52.

Copy2308, boot IRQ300, CDC IRQ340 and all source/ELF branch predicates are unchanged. No source/build/device mutation or new acceptance claim. Exact ELF remains ef22/SHA5d3f25e40b1b3765f891f3bc8f3fa16ff3c67483104c6f08f609a8569bede78f. The adjacent JSON calculates every corrected sum from its terms. Root, sole writer and independent reviewer were informed immediately; subsequent inner-bound calculations use programmatic sums.
