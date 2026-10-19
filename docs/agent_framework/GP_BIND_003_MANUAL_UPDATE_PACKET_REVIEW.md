# GP-BIND-003 manual-update packet independent review

Subject: `GP_BIND_003_MANUAL_UPDATE_PACKET.md` at commit
`3767c3d853f8258f9ef7a13e5471c2b0aece43b9`.

Classification: `SOURCE_FREE_INDEPENDENT_REVIEW`.

Result: `APPROVE`.

The review independently verified that the corrected packet has exactly one
human physical action: entering RPI-RP2.  It then permits only passive volume
inventory and one copy of the exact candidate UF2, ending at the expected
automatic return to ordinary controller operation.  It no longer requires an
unspecified Configurator mode transition.

The reviewer verified the following exact bindings:

- candidate `307d72347653c079ec8ec6e9b6ecae3c30ae536c`, tree
  `56d9622d2e91174be1395a5234097ab6ef1739ac`, and canonical-base ancestry;
- candidate UF2 `83aa255a7843fbc96af37c679e92408808d9de0f004271315f968db73c37747b`,
  `979456` bytes;
- rollback UF2 `e68105ff1fa033308ec9761d87260908a1cd145068e73eb2df516e34ee2e0fe5`,
  `796672` bytes;
- both copies of the fresh pre-update capture manifest
  `92bb28327c1da028a93222b543db014223fe9da2b2fca3845356ab08553dd399`,
  including the 252-byte raw Config digest
  `54fda3988c30e03b653153ec23d0623674da3649492caa75da8aa08fbce6b460`.

No Config/ProfileStore mutation, retry after uncertainty, automatic rollback,
merge, or hardware-acceptance assertion is authorized.  The review accessed
no controller and records no hardware outcome.  Any later Configurator
transition or post-update query requires its own action-specific packet.
