# Fresh independent narrow SETUP / IRQ source review

Source APPROVED by fresh_setup_irq_review for the source snapshot pinned below. No blocking finding. Exact committed ELF/build/resource/custody review follows in the preserved handoff; this source receipt is not hardware acceptance. Root cause UNPROVEN.

The reviewer independently matched all34 harness source hashes, inspected70 ASan/UBSan runtime cases and32 negative controls, and reran the32-tuple sampler under sanitizers. Registration substitution preserves one shared slot and once forwarding. Single-writer context banks and store1 unfiltered flags are coherent. MB1 is not causal evidence. Internal handler status/early branch, sequential sampling, optical/host limits and unquantified observer timing remain explicit.

The v7 scratch word omits LF4 raw data and retains LF3/LF5 only; full Dashboard and the physical panel retain LF4. This nonblocking retention limit is documented in the contract and does not require another publication path.

Original source-review receipt SHA256 aae3e66f80167d00b4f767b51b461fcaa03385324519271f769b9a781ad9e8f5.

```json
{
  "status": "SOURCE_APPROVED_PENDING_EXACT_ELF_BUILD_CUSTODY_REVIEW",
  "reviewer": "fresh_setup_irq_review",
  "base": "3761b702ea09f50b9c98a55bea91caa337a3f62e",
  "changed_path_hashes": {
    "HAL/pico/src/comms/ConfiguratorBackend.cpp": "2b3cdeb116028e829a102780cbb2261fd853716749a138509ea2169d5b5f931e",
    "HAL/pico/src/core/RecoveryStartupDiagnostics.cpp": "e166462db99ae79f546f59413100f3f808b3f86aeb4a07778fcd8987e9892c7c",
    "HAL/pico/src/core/RecoveryUsbDiagnostics.cpp": "e0edc5dfcdb59930aebe041db14c2e1a0c407629ab427ce1b752c554aa90bca4",
    "builder_scripts/rt2_dcd_observer.py": "4e5aae2ea4273224cadea3567bbcc777fc65200499b6c1847e610de7820c598e",
    "docs/AGENT_CONTEXT.md": "f5af13718db15700d8fc7ea70df62064955a6f88f939360c00238e051825a148",
    "docs/CURRENT_STATE.md": "b670567782c4cf9d849b899f005c57048a45536bd49152603f3b19f4901c2d26",
    "docs/ROADMAP.md": "98d7626218271bea344a04c79b64205e7f5a180c22c8a34a892698cc51417d2f",
    "include/core/RecoveryStartupDiagnostics.hpp": "6af5c2f94f7be2c026d7c9ed504293324bf502e6e2a790995d80fe6af800d2c5",
    "include/core/RecoveryUsbDiagnostics.hpp": "1e93a5da2fdaaba44be83132467bcf595f927b8d5939eb8d60d277d9f0754c0a",
    "schema/haybox/config.proto": "96717bad4a9ddfdeb2c776a6bf81c39b146de5858484d4c7086746504a08cb69",
    "docs/runtime_config/profile_store_rt2_setup_irq_authority_audit.md": "7fe5d1913d5ca71dd907f8f6bcfb0cc5534d387ac518b8924dfc455cab06ae3c",
    "docs/runtime_config/profile_store_rt2_setup_irq_contract.md": "4ae50dce6124941ce8d2852623465eeecb77b11490cf41931c63c1753be251e6",
    "docs/runtime_config/profile_store_rt2_setup_irq_coverage.json": "0b602cd009a60516b3b010ce4f46f4917ddcaed1dd396398365db19f348211d6",
    "docs/runtime_config/profile_store_rt2_setup_irq_device_adjudication.md": "6222ad65edbc7dad27f3358974f0873967a384963ebecb6e12b797a5f65fb9f4",
    "docs/runtime_config/profile_store_rt2_setup_irq_hardware_packet.md": "36d86ead75f4b6109a02d65956bb2fd4fd51f3c1b9056eefc3879c755c1bf6e0",
    "docs/runtime_config/profile_store_rt2_setup_irq_physical_adjudication.json": "341dba60df226d888e712807f2d9ceb80e894851a27ac2002fdeb7e62fae20b6",
    "docs/runtime_config/profile_store_rt2_setup_irq_source_audit.md": "a15459fd3606525f67aa132133b63b70a727d7d634d61921152eaa39c9377745",
    "include/core/RecoverySetupIrqDiagnostics.hpp": "440ca8654eaf8a8995b24bba449c0ccbd19edf637c599ff06085b5b7a6cd3961",
    "tools/check_glyph_rt2_setup_irq.py": "c652f42a02841ef562090f447bd7135630f27bc867fa24cb4bc2f09b8a374bb0",
    "tools/fixtures/rt2_setup_irq_host/cases.inc": "f4ee27fe1c7bfd08f76f9dac29cdf4e971291a5341f840ba3777043034a94350",
    "tools/fixtures/rt2_setup_irq_host/sampler.cpp": "aa44c84d2253bab9daef5bf6862d868c548df1d10d1a85a997d54c53271a9b2d",
    "tools/fixtures/rt2_setup_irq_host/timing.inc": "d6c067a33e7b76a0118187b2c54e6c8fa42e00fa7061ea44c9aa895546cd21a8"
  },
  "host_report_sha256": "9566a776808299d4ffe5987f53037abcc96f7884017c836fd05053b011ecb8f9",
  "findings": [],
  "nonblocking_observations": [
    "v7 scratch word omits LF4 raw bitset by retaining former pixels0/1 fields; full panel/dashboard correct. Root notified.",
    "Snapshot banks are bounded sequential intervals, not one atomic device-state instant.",
    "Core0 handler-local status and earliest inline SETUP branch remain explicit residuals; observer perturbation unquantified."
  ],
  "verification": [
    "Independent ASan/UBSan sampler32tuples PASS",
    "Exact changed source/header/schema/builder/checker/fixtures/docs inspected",
    "Host report frozen source hashes independently matched"
  ],
  "delegation": "Already delegated independent reviewer; no nested agent. Root owns Git, build, custody and publication.",
  "hardware": "NOT_TESTED",
  "root_cause": "UNPROVEN"
}
```
