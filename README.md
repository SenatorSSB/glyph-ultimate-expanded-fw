# Glyph firmware

Customizable Glyph controller firmware for Super Smash Bros. Ultimate players,
based on HayBox. Design raw stick outputs and coordinated button rules for your
own profiles.

> **Availability:** This community fork is being prepared for its public beta/release.
> Selected firmware routes have physical qualification; documentation and
> productization are ongoing. This is not yet a final public release.

## Build your own controls

- **Profile flexibility.** Config supports a maximum of **30 profile rows total**:
  a shared 30-row budget. Retained stock and other mode rows consume that budget.
  A row owns its remaps and SOCD settings; a native Ultimate profile owns its
  coordinate tables and rules. Backend destinations, overall brightness and some
  mode options are device-global. A complete managed package brings the paired
  row and native record together, with its plate and RGB configuration.
- **Nine-way modifier outputs.** Each native coordinate table contains all nine
  direction states, including **5 / no direction**:

  ```text
  7 8 9
  4 5 6
  1 2 3
  ```

  Every entry can hold any valid raw stick coordinate (`x,y` from 0 to 255).
  Holding RIGHT while a modifier is active may intentionally output DOWN-LEFT,
  or another chosen coordinate. Input direction does not have to match output
  direction; direction 5 may also output a non-center coordinate. There is no
  automatic character-facing awareness.
- **One input, coordinated roles.** A physical input can participate independently
  in a digital binding, a modifier/table-selection condition, a subsystem/layer
  activation condition and analogue effect gating. Ordinary remapping itself
  does not provide unrestricted duplicate fanout.
- **Subsystems / sublayers.** Conditions and rules can activate coordinated groups
  of mappings and effects. This is a finite deterministic rule system, without
  arbitrary nested scripting, persistent toggles, timers, macros or automated
  input sequences.

For a **neutral-B style rule**, a chosen physical input can request B while also
selecting or gating a left-stick output rule. Held direction buttons then need
not produce their ordinary directional stick output. Design the exact coordinate
and competing rules for the intended context: this is no promise of a particular
move for every character or game state, and supplies no Smash thresholds.

## Find your next step

- [Players and users: current usage](docs/USAGE.md)
- [Features and limits](docs/CAPABILITIES.md)
- [Current physical qualification and exact tested firmware](docs/CURRENT_STATE.md)
- [Native profile authors: start with v1](profiles/README.md)
- [Documentation index and glossary](docs/README.md)
- [Roadmap](docs/ROADMAP.md)
- [Developers: build, test and contribute](docs/DEVELOPMENT.md)
- [Coding agents: repository instructions](AGENTS.md)

Offline profile authoring exists. Installation, recovery and ordinary managed
selection still have product limitations; see the usage guide before proceeding.
The firmware's Configurator transport is distinct from the retired official
configurator website, which is not a development dependency.

## Credits and license

Glyph firmware builds on [HayBox by JonnyHaystack](https://github.com/JonnyHaystack/HayBox)
and the upstream Glyph work by Limit Labs and contributors. This community fork
is not presented as an official Limit Labs release. Please consider supporting
HayBox upstream. Licensed under [GNU GPL version 3](LICENSE); retain upstream
copyright and license notices. See [third-party notices](THIRD_PARTY_NOTICES.md)
for bundled attribution and declared build dependencies.
