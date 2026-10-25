# KazTest2 owner test sheet

Gameplay: NOT_TESTED. Host output assertions do not prove Smash command
recognition, timing, safe Shield cancel windows, charging, or ergonomics.

After a separately verified CREATE, use the controller's established normal
GameCube/Ultimate route. From the dashboard press **MB1** to open the menu;
use **MB2** (up) / **MB3** (down) to highlight **.Profile**, press **MB4** (enter),
scroll to **KazTest2** with MB2/MB3 and press MB4. Allow the selection save and
committed reboot to finish before playing. Confirm KazTest2 is displayed.
These controls are defined by `config/glyph/common/src/config.cpp` and the
existing MenuButtonHints/ConfigMenu/DefaultConfigMenu implementation.
If it is absent or selection fails, stop and report; do not recreate it or flash.
Return to the original **Kazuya** or **Ultimate** menu entry for rollback; both
working profiles must remain intact. No host reference write is needed.

Perform every directional sequence on both actual LF1 right and LF3 left;
repeat after changing facing. The profile itself never infers facing.

- RF8 alone: strong pure Down for all nine physical LF directions.
- RF8+RF7 with horizontal input: down-diagonal; release RF8 first → RF7 neutral;
  release RF7 → full horizontal. Observe Crouch Dash entry and cancel timing.
- RF8+RF7 with physical Up or Down (including diagonals): neutral preparation;
  release modifiers into forward/back/down-back/Up and assess actual cancels.
- RF8+RF5: EWGF candidate down-diagonal+A; no horizontal input gives neutral+A.
- Physical down-diagonal → RF8 Down → RF8+RF6 down-diagonal+Z: Hell's Gate.
- RF8+RF7+RF6: neutral/no Z → release RF8: full geometry/no Z → release RF7: RF6 Z.
- RF8+RF7+RF5: CDArmed/no A → release RF8: full chosen direction/no A (neutral
  physical input becomes Up) → release RF7: straight Up+A.
- Four buttons: neutral/no A/Z → release RF8: spring-loaded RF5 geometry/no A/Z
  → release RF7: Up+A. RF5 wins over RF6.
- For each spring-loaded sequence, also release RF7 first, then release both
  modifiers simultaneously. RF7-first with RF8 held intentionally exposes EWGF
  or Hell's Gate immediately. Assess accidental release orders.
- Hold ordinary RF5 for charged Up-Smash, with and without RF6 and physical directions.
- RF6 Z with physical Up-left, Up and Up-right: all give straight [128,205].
  Test the intended Up+Z/jump-squat interaction in-game.
- LT6: exact neutral+A across directions and RF combinations, including RF9;
  assess while-rising attack and independent B/Z/Shield interactions.
- LT2: double Shield with ordinary full angling; Up alone keeps Shield.
- LT2 release: RF3; executable RF5; physical Up+RF1; physical Up+RF2. LT3/LF4
  face sublayers must not prevent RF3 release. Independent LT1/RF16 still Shield.
- LT2+RF7+RF5 and LT2+RF8+RF7+RF5 retain Shield until RF7 is released. LT2 with
  RF7/RF8 alone keeps Shield; no old defensive down-back override remains.
- Check intentional rolls/spot dodges, ordinary actions out of Shield, C-stick
  transformations, retained modifiers/menu controls, and general responsiveness.

Report the selected profile name, sequence, physical side, actual result and
repeatability/timing or ergonomics issues. Nunchuk remains NOT_TESTED.
