#pragma once
#include "core/InputMode.hpp"
#include "display/DisplayMode.hpp"
struct _DisplayControls {Button back,down,up,enter;};
class IntegratedDisplay {
public:
 InputMode *mode=nullptr;
 InputState inputs{};
 InputState &GetInputs() {return inputs;}
 InputMode *CurrentGameMode() {return mode;}
 void SetDisplayMode(DisplayModeId) {}
 static constexpr unsigned char font_width=4,default_color=1;
};
