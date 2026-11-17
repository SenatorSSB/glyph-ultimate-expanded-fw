#include "comms/N64Backend.hpp"
#include "comms/NesBackend.hpp"
#include "comms/SnesBackend.hpp"
#include <cassert>
#include <cstdio>
static unsigned reports=0;
N64Console::N64Console(uint, PIO, int, int) {}
N64Console::~N64Console() {}
bool N64Console::Detect() { return false; }
bool N64Console::WaitForPoll() { return false; }
void N64Console::SendReport(n64_report_t*) { ++reports; }
int N64Console::GetOffset() { return 0; }
NesConsole::NesConsole(uint,uint,uint,PIO,int,int) {}
NesConsole::~NesConsole() {}
bool NesConsole::Detect() { return false; }
void NesConsole::SendReport(nes_report_t&) { ++reports; }
int NesConsole::GetOffset() { return 0; }
SnesConsole::SnesConsole(uint,uint,uint,PIO,int,int) {}
SnesConsole::~SnesConsole() {}
bool SnesConsole::Detect() { return false; }
void SnesConsole::SendReport(snes_report_t&) { ++reports; }
int SnesConsole::GetOffset() { return 0; }
int main(){InputState s{}; N64Backend n(s,nullptr,0,8); NesBackend e(s,nullptr,0,1,2,3); SnesBackend x(s,nullptr,0,1,2,3);
assert(n.BackendId()==COMMS_BACKEND_N64 && e.BackendId()==COMMS_BACKEND_NES && x.BackendId()==COMMS_BACKEND_SNES);
assert(n.GetOffset()==0 && e.GetOffset()==0 && x.GetOffset()==0);
n.SendReport();e.SendReport();x.SendReport();assert(reports==3);std::puts("PASS actual N64/NES/SNES constructors, identities, dispatch; physical PIO boundary doubles, no USB symbols linked");}
