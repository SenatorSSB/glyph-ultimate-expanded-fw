# GP-CONFIG-024 USB profile identity repair

## Result

The ordinary USB selector now identifies the selected profile by the exact
`GameModeConfig` row returned by `InputMode::GetConfig()`. It validates backend
and profile counts against the generated array extents before indexing. If the
backend, display, current mode, config pointer, profile count, or row identity is
invalid, the selector returns without disconnecting, delaying, writing
watchdog scratch values, rebooting, saving, or changing Config.

For a matched row, the existing action order remains: disconnect, wait 500 ms,
write one-based profile and backend values to watchdog scratch, wait 30 ms, and
reboot. The function returns if reboot returns. Menu options, eligibility,
filtering, labels, defaults, and profile contents are unchanged. `sameName`
remains available to the preserved GP-CONFIG-019 host proof.

## Exact candidate proof

Fresh canonical base B is `b404453ef22cc994eec54338b8a23c3ba61df808`, published
after C023 strict DONE. The candidate is a direct child of B and changes only
the ten paths listed in the adopted C024 work order. The checker binds all 19
source-annex rows at B, the exact production method, host stubs, host harness,
report, and regenerated runtime-config census/manifest/health artifacts.

The literal `InputMode::GetConfig`, `InputMode::SetConfig`, and relevant
`set_mode` overloads are compiled with the exact selector body. Both ordinary
and short-enum host modes use AddressSanitizer and UndefinedBehaviorSanitizer.
The harness asserts the expected enum widths in each compiler mode; this is a
focused enum-mode check, not a complete target Config ABI layout proof.
Cases cover unique names, every row under duplicate and empty names, duplicate
mode IDs, reordered rows, both empty-name controller/Keyboard orderings,
17-character and post-NUL bytes, and `SIZE_MAX` current-mode index during actual
mode setup. Null display/current-mode/config, invalid backend, zero and
out-of-extent counts, uncounted/detached pointers all refuse without effects.
Returning and terminating reboot spies verify exact ordered scratch/reboot
actions, one action, and unchanged Config contents.

These host checks establish selector behavior at the method boundary. They do
not claim physical menu behavior, controller acceptance, firmware build, or
hardware acceptance. The candidate remains unbuilt and unmerged until the sole
ordinary GP-VAL-045 successor reaches strict DONE.

Nunchuk remains NOT_TESTED; root cause remains UNPROVEN.
