# Confirmed binding JSONL handoff defect

P2/Tier2: valid normal pretty binding bytes are interpolated verbatim into the acceptance_binding journal record. Actual source emits multiline records; strict JSONL verifier refuses them. Independent actual parse+open_journal sanitized witness succeeds with zero registry/host calls, then JSON parsing fails at line2. See finding-jsonl.json and journal-witness-commands.json. No repair made by reviewer.
