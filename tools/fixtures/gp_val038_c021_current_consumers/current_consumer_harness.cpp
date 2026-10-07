// Reuse the frozen host transaction observations; production bodies remain literal TUs.
#define main frozen_setconfig_harness_main
#include "../gp_config021_persisted_recovery/setconfig_harness.cpp"
#undef main
#include "modes/CustomControllerMode.hpp"
#include "modes/CustomKeyboardMode.hpp"
#include "util/state_util.hpp"
#include <TUKeyboard.hpp>
class ObservedKeyboard:public CustomKeyboardMode {
public: uint64_t remapped=0,cleaned=0;
protected:
 void HandleRemap(const InputState &in,InputState &out)override{InputMode::HandleRemap(in,out);remapped=out.buttons;}
 void HandleSocd(InputState &in)override{InputMode::HandleSocd(in);cleaned=in.buttons;}
};
static uint8_t output(CustomControllerMode &mode,Button modifier){InputState in{};set_button(in.buttons,BTN_LF2,true);set_button(in.buttons,modifier,true);OutputState out{};mode.UpdateOutputs(in,out,COMMS_BACKEND_DINPUT);return out.leftStickX;}
int main(){try{
 require(persistence.SetValidator(validate_config_semantics),"install stable current callback");live=valid_config();require(persistence.SaveConfig(live),"initial real save");
 for(bool empty:{false,true})for(bool backend:{false,true})for(unsigned raw:{1u,60u,0u,61u,255u}){
  candidate=valid_config();candidate.game_mode_configs_count=2;candidate.game_mode_configs[1]=candidate.game_mode_configs[0];
  for(auto &row:candidate.game_mode_configs)std::strcpy(row.name,empty?"":"duplicate");candidate.communication_backend_configs_count=1;candidate.communication_backend_configs[0].backend_id=COMMS_BACKEND_DINPUT;
  if(backend){auto &row=candidate.communication_backend_configs[0];row.activation_binding_count=1;row.activation_binding[0]=Button(raw);}
  else{auto &row=candidate.game_mode_configs[0];row.activation_binding_count=1;row.activation_binding[0]=Button(raw);}
  const bool valid=raw==1||raw==60;candidate_check(std::string("name_binding/")+(empty?"empty/":"duplicate/")+(backend?"backend/":"mode/")+std::to_string(raw),valid,valid?"":"Config contains an invalid button binding",!valid);
  if(valid)require(std::strcmp(live.game_mode_configs[0].name,live.game_mode_configs[1].name)==0,"duplicate/empty real SET+Load preserved");
 }
 candidate=valid_config();candidate.custom_modes_count=1;auto &custom=candidate.custom_modes[0];custom.stick_range=64;custom.stick_direction_mappings_count=8;
 const Button direction[]={BTN_LF5,BTN_LF4,BTN_LF1,BTN_LF2,BTN_RF4,BTN_RF3,BTN_RF1,BTN_RF2};for(size_t i=0;i<8;++i)custom.stick_direction_mappings[i]=direction[i];
 custom.modifiers_count=1;auto &mod=custom.modifiers[0];mod.buttons_count=1;mod.buttons[0]=BTN_MB1;mod.axis=AXIS_LSTICK_X;mod.multiplier=.5;mod.combination_mode=COMBINATION_MODE_COMPOUND;candidate_check("custom_initial",true);
 CustomControllerMode mode;mode.SetConfig(live.game_mode_configs[0],live.custom_modes[0]);require(output(mode,BTN_MB1)==160,"original modifier output");unsigned char mode_before[sizeof(mode)];std::memcpy(mode_before,static_cast<const void*>(&mode),sizeof(mode));
 candidate=live;candidate.custom_modes[0].modifiers[0].buttons[0]=BTN_MB2;candidate.custom_modes[0].modifiers[0].multiplier=.25;candidate_check("custom_real_SET",true);
 require(std::memcmp(mode_before,static_cast<const void*>(&mode),sizeof(mode))==0&&mode.GetConfig()==&live.game_mode_configs[0],"SET preserves actual mode object/pointer");require(output(mode,BTN_MB1)==144,"old cached mask sees new multiplier");
 mode.SetConfig(live.game_mode_configs[0],live.custom_modes[0]);require(output(mode,BTN_MB1)==192&&output(mode,BTN_MB2)==144,"explicit SetConfig refreshes masks");
 std::memcpy(mode_before,static_cast<const void*>(&mode),sizeof(mode));candidate=live;candidate.game_mode_configs[0].custom_mode_config=256;candidate_check("custom_reject_preserves_mode",false,"Custom mode ID 256 is for game mode config 1 but only 1 custom modes are defined");require(std::memcmp(mode_before,static_cast<const void*>(&mode),sizeof(mode))==0,"rejected SET preserves consumer object");
 std::cout<<"consumer_case=custom_cache_rebind PASS\n";
 candidate=Config_init_default;candidate.game_mode_configs_count=1;candidate.game_mode_configs[0].mode_id=MODE_KEYBOARD;candidate.game_mode_configs[0].keyboard_mode_config=1;candidate.keyboard_modes_count=1;
 auto &game=candidate.game_mode_configs[0];game.button_remapping_count=1;game.button_remapping[0].physical_button=BTN_LF1;game.button_remapping[0].activates=BTN_RF1;game.socd_pairs_count=1;game.socd_pairs[0]={BTN_LF1,BTN_RF1,SOCD_NEUTRAL};
 auto &keys=candidate.keyboard_modes[0];keys.buttons_to_keycodes_count=2;keys.buttons_to_keycodes[0]={BTN_LF1,4};keys.buttons_to_keycodes[1]={BTN_RF1,7};candidate_check("keyboard_real_SET",true);
 TUKeyboard::reset();{ObservedKeyboard keyboard;keyboard.SetConfig(live.game_mode_configs[0],live.keyboard_modes[0]);InputState in{};set_button(in.buttons,BTN_LF1,true);const auto before=in.buttons;keyboard.SendReport(in);require(in.buttons==before&&keyboard.remapped==(uint64_t(1)<<(BTN_RF1-1))&&TUKeyboard::keys[4]&&!TUKeyboard::keys[7],"keyboard original input dispatch after remap");
  // Disable remapping through actual accepted SET, preserving the pointed-to row.
  candidate=live;candidate.game_mode_configs[0].button_remapping_count=0;candidate_check("keyboard_valid_disable_remap",true);set_button(in.buttons,BTN_RF1,true);keyboard.SendReport(in);require(keyboard.cleaned==0&&TUKeyboard::keys[4]&&TUKeyboard::keys[7],"keyboard original input dispatch after neutral cleaning");in.buttons=0;keyboard.SendReport(in);require(!TUKeyboard::keys[4]&&!TUKeyboard::keys[7],"keyboard released input");}
 require(TUKeyboard::begins==1&&TUKeyboard::releases==1&&!TUKeyboard::keys[4]&&!TUKeyboard::keys[7],"keyboard lifetime observations");std::cout<<"consumer_case=keyboard_original_input_dispatch PASS\n";
 std::cout<<"current_consumer_matrix name_binding=20 transaction_cases="<<cases<<" consumer_cases=2 PASS\n";return 0;
}catch(const std::exception &e){std::cerr<<e.what()<<'\n';return 1;}}
