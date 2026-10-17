# 895109eb large-READ hardware gate

Result: `MULTI_PROFILE_STORE_895_READ_GATE_HARDWARE_PASS`

- Candidate: `895109eb662a8ad6b6c99889cb37a254dce49998`
- Tree: `94d572cd23bd862a80d7891cd81c994a38f2c5a8`
- Custody UF2: `firmware.uf2`, 980480 bytes,
  SHA-256 `62eef01798782459750cb300071564a45f366fe6da94116d21b6db29d861c6f5`
- Device revision: `895109eb`
- Store: incarnation 1, generation 160; no fault pending or armed.

Immediate traced ID1 READ returned `PROFILE_STORE_OK`, revision 2, canonical
payload SHA-256 `8b38da6ca253e48bb54e9a14a9e06dbff214f6c5544c98c00724761ff80db185`.
Its traced terminal stage was 24, with a 2002-byte final response attempt.
Immediate traced ID3, ID4 and ID22 reads also reached stage 24 and matched
their retained payloads; ID22 remained revision 130.

Twenty independent open/close cycles each completed pulse, STATUS, paged LIST
(0/8/16), and reads of IDs 1/3/4/22: 80 successful cycle reads, 84 successful
reads including the four immediate reads. No timeout, malformed response, or
generation drift was observed. All 20 cycle ID1 traces reached stage 24.

Final read-only capture: Config deterministically re-encoded, raw Config body
was 251 bytes with SHA-256
`09cea792bd78eb50231de58d84a7605c0a68e8a0cb7cc500f6fa506e4f2c6ff9`.
Final STATUS remained generation 160. Minimum observed core0/core1 free-stack
margins were 1936/3716 bytes; maximum heap arena peak was 9048 of 74584 bytes.

No persistent mutation was made in this gate. `d59684b` remains permanently a
hardware failure; this gate does not establish its exact physical blocked PC.
