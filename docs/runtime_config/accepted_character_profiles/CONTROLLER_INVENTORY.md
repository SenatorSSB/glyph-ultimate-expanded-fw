# Read-only preparation inventory

Snapshot:27 total records,5 native and22 unrelated/legacy preserved. No controller mutations in this chapter. A future execution must take a new full preflight.

| ID | Current name | Rev | Rank | Wrapper SHA-256 | Body SHA-256 | Role | Referenced? | Delete? |
| ---: | --- | ---: | ---: | --- | --- | --- | --- | --- |
| 27 | Ultimate | 1 | 0 | `30d43278fee3a835ca006f4b5df67963c8e9b11ef059ab3b49329b65c7934c6b` | `ca9985997471f247d2f44ba1290e95197393a6c6bdf80a5e59a357f2d6c3e5ee` | golden permanent owner Pikachu / archival Ultimate | NO | NO: keep as Pikachu |
| 48 | Kazuya | 1 | 2 | `60f1715738fb5a46f8ac7cde326a3178e4560e52a8489da54e3a435eb70fd3e8` | `44fa76903206c7a86a9f5d5a19c0be5f237e1c7e631dd5adf21cdb27eb3e4405` | original Kazuya v1 experiment | NO | Only after separate approval and exact fresh unreferenced proof |
| 49 | KazTest2 | 1 | 152 | `b43f5fa595582b076e9af6794a42fd01579eed6931b38da8f92c1537b1fcfa24` | `9658566f59fd2bb058282b53b4f86610c2ff870a1492c4377ea143ce9cf1f91f` | Kazuya v2 experiment | NO | Only after separate approval and exact fresh unreferenced proof |
| 50 | KazTest3 | 1 | 153 | `1f919177691afc7ba35621229301169f710540c5e74952487b25ed3db0782131` | `22263a77a2f6b2555747381634ec1f80c5b96e81f793e2aea4027ed5fb142e3d` | Kazuya v3 pure-Up experiment | NO | Only after separate approval and exact fresh unreferenced proof |
| 51 | KazTest4 | 1 | 154 | `46084bbcf55646819ab0ce824b9de9ac778d3bc4d9344a8c8bcbfe5d15f6142c` | `a8b03ed4952f4ea81317ca2053830925e751a2647b05a5777b01a82d40e349d2` | accepted Kazuya v4 | YES | NO: keep as Kazuya |

The only current native reference is acceptedID51. All three superseded candidates are unreferenced. Every current wrapper matches its source and sealed installation lineage; see [CONTROLLER_PLAN.json](CONTROLLER_PLAN.json). StableIDs and full hashes determine identity; names and creation order alone never authorize deletion. All22 legacy records, including the independently referenced legacyID3, remain preserved. No additional native/SEL/Ultimate Runtime entries were found; any unknown future native record stops the packet.
