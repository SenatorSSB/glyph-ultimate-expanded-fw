#!/usr/bin/env python3
"""Exact-function host traces. Render doubles, no device or physical timing claim."""
from pathlib import Path
import argparse,subprocess,tempfile,json,hashlib
p=argparse.ArgumentParser();p.add_argument('--repo',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.repo=a.repo.resolve();a.out.mkdir(parents=True,exist_ok=True)
def function(path,signature):
 s=(a.repo/path).read_text();start=s.index(signature);q=s.index('{',start);depth=1;end=q+1
 while depth:depth+=(s[end]=='{')-(s[end]=='}');end+=1
 return s[start:end]
spec=[('src/comms/IntegratedDisplay.cpp',x) for x in ['void IntegratedDisplay::SendReport(', 'void IntegratedDisplay::HandleControls(', 'void IntegratedDisplay::SetDisplayMode(', 'DisplayMode *IntegratedDisplay::GetActiveDisplayMode(']]+[
 ('config/glyph/common/src/display/MenuButtonHints.cpp','void MenuButtonHints::HandleControls('),
 ('HAL/pico/src/display/InputDisplay.cpp','void InputDisplay::HandleControls('),
 ('HAL/pico/src/display/ConfigMenu.cpp','const MenuPage::MenuItem *ConfigMenu::ResolveItem('),
 ('HAL/pico/src/display/ConfigMenu.cpp','void ConfigMenu::HandleControls('),
 ('config/glyph/common/src/display/GlyphConfigMenu.cpp','void GlyphConfigMenu::ReturnToDashboard('),
 ('config/glyph/common/src/display/GlyphConfigMenu.cpp','void GlyphConfigMenu::SetDashboardOption('),
 ('config/glyph/common/src/config.cpp','void transfer_dashboard(')]
bodies=[function(*x) for x in spec]
# All traced control/transfer functions must remain byte-for-byte baseline functions.
for (path,signature),body in zip(spec,bodies):
 baseline=subprocess.check_output(['git','-C',str(a.repo),'show','2bcb5104:'+path],text=True)
 assert body in baseline,(path,signature,'changed from protected baseline')
prefix=r'''
#include <cstdint>
#include <cstddef>
#include <string>
#include <vector>
#include <iostream>
#include <cassert>
#define max(a,b) ((a)>(b)?(a):(b))
#define min(a,b) ((a)<(b)?(a):(b))
enum Button{BTN_UNSPECIFIED,BTN_MB1,BTN_MB2,BTN_MB3,BTN_MB4};
enum DisplayModeId{DISPLAY_MODE_VIEWER,DISPLAY_MODE_CONFIG,DISPLAY_MODE_BUTTON_HINTS,DISPLAY_MODE_ABOUT};
enum CommunicationBackendId{COMMS_BACKEND_DINPUT,COMMS_BACKEND_XINPUT,COMMS_BACKEND_NINTENDO_SWITCH,COMMS_BACKEND_GAMECUBE};
enum DashboardOption{DASHBOARD_MENU_BUTTON_HINTS,DASHBOARD_INPUT_VIEWER};
struct Config{DashboardOption default_dashboard_option=DASHBOARD_MENU_BUTTON_HINTS;};
struct DisplayControls{Button back,down,up,enter;};
struct InputMode{};struct InputState{uint64_t buttons=0;};struct Adafruit_GFX{};
static uint32_t now=0;uint32_t millis(){return now;}bool time_reached(uint32_t t){return now>=t;}uint32_t make_timeout_time_ms(unsigned m){return now+m;}
bool get_button(uint64_t bits,Button b){return bits&(1ull<<b);}
class IntegratedDisplay;class DisplayMode{public:virtual DisplayModeId GetId()=0;virtual void UpdateDisplay(IntegratedDisplay*,Adafruit_GFX&)=0;virtual void HandleControls(IntegratedDisplay*,const DisplayControls&,Button)=0;};
static std::string trace;static std::vector<DisplayModeId> transfers;static unsigned marks=0;
class IntegratedDisplay{public:
 InputState _inputs;Adafruit_GFX _display;DisplayControls _controls{BTN_MB1,BTN_MB2,BTN_MB3,BTN_MB4};Button _controls_array[4]{BTN_MB1,BTN_MB2,BTN_MB3,BTN_MB4};
 static constexpr unsigned controls_count=4,button_cooldown_ms=150;uint32_t _button_cooldown_end=0;
 DisplayModeId _display_mode=DISPLAY_MODE_BUTTON_HINTS;DisplayMode **_display_modes=nullptr;size_t _display_modes_count=0;InputMode *mode=nullptr;
 InputMode*CurrentGameMode(){return mode;}void SetGameMode(InputMode*m){mode=m;}
 void(*_clear_display)();void(*_update_display)();
 void SendReport();void HandleControls(DisplayMode*);void SetDisplayMode(DisplayModeId);DisplayMode*GetActiveDisplayMode();DisplayModeId CurrentDisplayMode(){return _display_mode;}
};
struct Backend{InputMode*mode=nullptr;InputMode*CurrentGameMode(){return mode;}void SetGameMode(InputMode*m){mode=m;}CommunicationBackendId BackendId(){return COMMS_BACKEND_GAMECUBE;}};
class MenuButtonHints:public DisplayMode{public:DisplayModeId GetId(){return DISPLAY_MODE_BUTTON_HINTS;}void UpdateDisplay(IntegratedDisplay*,Adafruit_GFX&){trace+='H';}void HandleControls(IntegratedDisplay*,const DisplayControls&,Button);};
class InputDisplay:public DisplayMode{public:DisplayModeId GetId(){return DISPLAY_MODE_VIEWER;}void UpdateDisplay(IntegratedDisplay*,Adafruit_GFX&){trace+='V';}void HandleControls(IntegratedDisplay*,const DisplayControls&,Button);};
class ConfigMenu;struct MenuPage{struct MenuItem{void(*action)(IntegratedDisplay*,ConfigMenu*,Config&,uint8_t)=nullptr;MenuPage*page=nullptr;bool usb=false;uint8_t key=0;};MenuPage*parent=nullptr;MenuItem*items=nullptr;size_t items_count=0;};
class ConfigMenu:public DisplayMode{public:
 Config _config;Backend**_backends;MenuPage*_current_menu_page=nullptr,*_top_level_page=nullptr;int _current_menu_offset=0,_highlighted_menu_item=0;
 DisplayModeId GetId(){return DISPLAY_MODE_CONFIG;}
 // Render double uses the exact production menu's game-mode handoff prefix.
 void UpdateDisplay(IntegratedDisplay*instance,Adafruit_GFX&){trace+='C';if(_backends[0]!=nullptr&&_backends[0]->CurrentGameMode()!=nullptr){instance->SetGameMode(_backends[0]->CurrentGameMode());_backends[0]->SetGameMode(nullptr);}}
 const MenuPage::MenuItem*ResolveItem(MenuPage*,size_t);void HandleControls(IntegratedDisplay*,const DisplayControls&,Button);virtual void ReturnToDashboard(IntegratedDisplay*)=0;
};
class GlyphConfigMenu:public ConfigMenu{public:void ReturnToDashboard(IntegratedDisplay*);static void SetDashboardOption(IntegratedDisplay*,ConfigMenu*,Config&,uint8_t);};
IntegratedDisplay *display_backend=nullptr;bool boot_display_ready=false;uint32_t boot_start_ms=0;bool boot_state_mutex=false;
struct{uint32_t first_dashboard_ms=0;}boot_times;
void mutex_enter_blocking(bool*m){assert(!*m);*m=true;++marks;}void mutex_exit(bool*m){assert(*m);*m=false;}
struct{void display(){trace+='T';transfers.push_back(display_backend->CurrentDisplayMode());}}display;
'''
main=r'''
void clear(){trace+='c';}
int main(int argc,char**argv){assert(argc==2);bool viewer=std::string(argv[1])=="viewer";
 IntegratedDisplay screen;display_backend=&screen;MenuButtonHints hints;InputDisplay input;GlyphConfigMenu menu;Backend backend;Backend*backends[]{&backend};menu._backends=backends;
 DisplayMode* modes[]{&hints,&input,&menu};screen._display_modes=modes;screen._display_modes_count=3;screen._clear_display=clear;screen._update_display=transfer_dashboard;
 InputMode game;screen.mode=&game;backend.mode=&game;MenuPage::MenuItem item;MenuPage top{nullptr,&item,1},child{&top,&item,1};menu._current_menu_page=menu._top_level_page=&top;
 menu._config.default_dashboard_option=viewer?DASHBOARD_INPUT_VIEWER:DASHBOARD_MENU_BUTTON_HINTS;auto dashboard=viewer?DISPLAY_MODE_VIEWER:DISPLAY_MODE_BUTTON_HINTS;
 screen._display_mode=DISPLAY_MODE_CONFIG;now=10;screen.SendReport();assert(trace=="cCT"&&boot_times.first_dashboard_ms==0&&marks==0);
 screen._display_mode=dashboard;trace.clear();now=20;screen.SendReport();assert(boot_times.first_dashboard_ms==0&&marks==0);
 boot_display_ready=true;trace.clear();now=100;screen._inputs.buttons=1ull<<BTN_MB1;screen.SendReport();assert(trace==(viewer?"cVT":"cHT"));assert(screen._display_mode==DISPLAY_MODE_CONFIG&&boot_times.first_dashboard_ms==100&&marks==1);assert(transfers.back()==dashboard);
 trace.clear();now=120;screen.SendReport();assert(trace=="cCT"&&screen._display_mode==DISPLAY_MODE_CONFIG&&backend.mode==nullptr);
 now=251;screen._inputs.buttons=0;screen.SendReport();now=252;screen._inputs.buttons=1ull<<BTN_MB1;screen.SendReport();assert(screen._display_mode==dashboard&&backend.mode==&game&&transfers.back()==DISPLAY_MODE_CONFIG);
 trace.clear();now=403;screen._inputs.buttons=0;screen.SendReport();assert(trace==(viewer?"cVT":"cHT")&&transfers.back()==dashboard&&boot_times.first_dashboard_ms==100&&marks==1);
 // Nested Back returns one level; top-level action returns the chosen dashboard.
 menu._current_menu_page=&child;screen._display_mode=DISPLAY_MODE_CONFIG;menu.HandleControls(&screen,screen._controls,BTN_MB1);assert(menu._current_menu_page==&top&&screen._display_mode==DISPLAY_MODE_CONFIG);
 item.action=GlyphConfigMenu::SetDashboardOption;item.key=viewer?DASHBOARD_MENU_BUTTON_HINTS:DASHBOARD_INPUT_VIEWER;menu.HandleControls(&screen,screen._controls,BTN_MB4);auto changed=viewer?DISPLAY_MODE_BUTTON_HINTS:DISPLAY_MODE_VIEWER;assert(screen._display_mode==changed&&backend.mode==&game);
 trace.clear();now=600;screen.SendReport();assert(trace==(viewer?"cHT":"cVT")&&boot_times.first_dashboard_ms==100&&marks==1);
 screen._display_mode=DISPLAY_MODE_ABOUT;trace.clear();screen.SendReport();assert(trace.empty());
 std::cout<<(viewer?"viewer":"hints")<<" first/return/action/cooldown/transfer-once exact-function trace PASS\n";
}
'''
source=prefix+'\n'.join(bodies)+main
(a.out/'transitions.cpp').write_text(source)
for short in (False,True):
 exe=a.out/('transitions-'+('short' if short else 'default'))
 subprocess.run(['c++','-std=c++17','-fsanitize=address,undefined',*(['-fshort-enums'] if short else []),str(a.out/'transitions.cpp'),'-o',str(exe)],check=True)
 for route in ('hints','viewer'):subprocess.run([str(exe),route],check=True)
# Negative control: moving controls before transfer loses the first dashboard mark.
old='''    _clear_display();
    active_mode->UpdateDisplay(this, _display);
    _update_display();'''
mutant=source.replace(old,'HandleControls(active_mode);\n'+old,1).replace('    HandleControls(active_mode);','',1)
assert mutant!=source
(a.out/'early-controls.cpp').write_text(mutant);exe=a.out/'early-controls'
subprocess.run(['c++','-std=c++17',str(a.out/'early-controls.cpp'),'-o',str(exe)],check=True)
r=subprocess.run([str(exe),'hints'],capture_output=True,text=True);assert r.returncode!=0,'early-control mutant survived'
(a.out/'identities.json').write_text(json.dumps({path:hashlib.sha256((a.repo/path).read_bytes()).hexdigest() for path,_ in spec},indent=2)+'\n')
print('earlier-control negative detected; functions equal2bcb5104; render doubles/physical observations NOT_CLAIMED')
