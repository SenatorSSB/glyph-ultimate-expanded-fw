# Existing Configurator menu entry: limited source qualification

F334f source supports the owner's known “menu → Configurator mode” path. In
`HAL/pico/src/display/DefaultConfigMenu.cpp:154–181`, the named menu action
finds an existing Configurator backend row, disconnects USB, writes its one-based
backend index to watchdog scratch0 and calls `reboot_firmware()`. This is a real
firmware restart and requires the proposed separate explicit physical-entry
approval. It is not a host reset command or a request to Save Config, and the
entire menu source is byte-identical to accepted307d7234 and baseline976ba2195.

The ordinary selector in `HAL/pico/src/comms/backend_init.cpp:310–339` applies the
scratch index and can change `config.default_usb_backend_config` in live RAM.
That selector is byte-identical across those three sources. The backend-init
watchdog branch at F123–146 specially excludes
`COMMS_BACKEND_CONFIGURATOR` before returning its Save action. Accepted307d and
976 carry the same exclusion around their direct `persistence.SaveConfig(config)`;
F outlined the Save call into returned phase dispatch. Thus the general warning
that other watchdog backend switches can save Config must not be applied as if
this known Configurator branch necessarily saves its temporary default. This
qualification is limited to a successfully selected Configurator destination;
it does not approve another backend switch or a guessed entry chord.

F `ConfiguratorBackend.cpp:317–332` verifies normal/recovery availability and
saved Config validity, writes the response command and streams
`persistence.LoadConfigRaw(_out,false)`. It does not protobuf-encode the live RAM
Config with its temporary Configurator default. The handler, LoadConfigRaw and
its filename selector are byte-identical to accepted307d and976. LoadConfigRaw
opens the selected existing current/prior/legacy Config file with mode`r`, seeks
past the Config header and streams saved protobuf bytes. The backup is durable
public Config payload, not a raw flash/filesystem snapshot. Source selection
can choose a prior compact or legacy source according to existing admission;
do not call it a confirmed normal compact-v2 original until actual backup/status
eligibility verifies that fact. Validate exact received bytes/protobuf completeness,
custody and checksum using the pinned existing tool; a successful framing alone
does not overcome a refused or incomplete saved Config read.

`TinyUSBDevice.setID(0x2E8A,0x1092)` is the F Configurator identity. Positively
mapping that USB identity/interface to one actual CDC port and the owner-identified
unit is required before the existing bounded read-only requests. VID/PID alone
does not attest the installed firmware or F. Installed firmware is currently
unknown; normal startup can perform existing recovery/migration/bookkeeping.
The menu-source comparison therefore supports the bounded backup-entry proposal
but cannot promise a byte-identical persistent state across restart. If selection
does not enter the identified ordinary Configurator session, it is a stop, not
permission to reboot again, select a different backend or use recovery.

The limited proposed entry and already-approved reads are consistent with
original-data preservation at these source boundaries. Preserve actual post-entry
normal Config/ProfileStore state before any later mutation; record any recovery,
migration or unexpected condition as a stop. No raw rollback claim, source change,
new device operation, actual restart or approval is created by this report.
