# Successful SetConfig runtime-rebinding characterization

Status: `SOURCE_CHARACTERIZED_IMPLEMENTATION_NOT_AUTHORIZED`.

GP-CONFIG-008 records the sequential, source-backed boundaries after a
successful `HandleSetConfig`: the persisted `Config` object becomes visible
through the existing reference, while activation masks, selected-mode
singletons, custom-mode cached masks, communication-backend construction, and
NeoPixel/display bindings are updated only by their existing selection, boot,
or display paths.

This is characterization only. It does not select a runtime repair, add a
reboot policy, or claim cross-core atomicity, timing/visibility guarantees,
physical behavior, or a performed reboot.

<!-- setconfig-rebinding-coverage:start -->
| Boundary | Current source-backed observation |
| --- | --- |
| live `Config` reference | successful `HandleSetConfig` assigns `_config = candidate` after `SaveConfig` |
| activation masks | `setup_mode_activation_bindings` builds fixed masks; `select_mode` consumes them and suppresses same-index reselection |
| selected mode | `set_mode` configures mode singletons and installs the backend pointer; no automatic post-SetConfig reselection is present |
| generic `InputMode` | `SetConfig` replaces the mode's config pointer; output processing reads the pointed-to config sequentially |
| custom mode | `CustomControllerMode::SetConfig` replaces the custom-config pointer and rebuilds modifier/combo masks |
| backend selection | `initialize_backends` selects/constructs backends during initialization; SetConfig does not reinitialize them |
| NeoPixel | `SetGameMode` caches RGB config and button colors; `SendReport` reads the constructor-bound brightness reference |
| display | display mode and menu bindings are updated by explicit display/menu paths, not by SetConfig |
| unknown | cross-core timing/atomicity, physical output, and reboot reconstruction remain `UNKNOWN` |
<!-- setconfig-rebinding-coverage:end -->

No firmware source, protocol, persistence, backend reinitialization, display,
LED, device, or hardware behavior is changed by this record.
