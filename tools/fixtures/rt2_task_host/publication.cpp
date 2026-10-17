#include "state.hpp"
#include <cstdio>
#include <stdexcept>
#include <thread>
RecoveryTaskDiagnostics::State *subject;
unsigned seen=0;
bool inject=true;
void require(bool p,const char*m){if(!p)throw std::runtime_error(m);}
void GlyphPublicationBoundary(unsigned phase){
    if(!inject)return;
    ++seen;
    // Simulate an IRQ precisely before/after active ID publication and after
    // active clear. Observer thread gets a bounded invalid snapshot during the
    // odd foreground sequence; it never spins waiting for stalled writer.
    subject->ResetEvent();
    std::thread observer([]{require(!subject->Read().valid,"odd writer snapshot rejected without spinning");});observer.join();
    (void)phase;
}
int main(){try{
    RecoveryTaskDiagnostics::State state;subject=&state;state.Enable();state.Arm();
    state.ResetEvent();require(state.Read().first_resets==0,"reset before first task excluded");
    state.Enter();auto s=state.Read();require(s.valid&&s.active==1&&s.first_resets==1&&s.active_resets==1,"pre-active reset excluded, post-active reset included");
    state.Return();s=state.Read();require(s.first_resets==1&&s.first_returned&&s.task_pixel==4,"post-clear reset excluded");
    inject=false;state.Enter();state.ResetEvent();state.ResetEvent();s=state.Read();require(s.active==2&&s.active_resets==2&&s.first_resets==1&&s.task_pixel==4,"anchored first return survives later active/reset events");
    state.Return();require(seen==3,"every exact publication hook exercised");
    std::puts("publication_boundaries=PASS before-active/after-active/after-clear odd-writer-bounded first-return-anchor");return 0;
}catch(const std::exception&e){std::fprintf(stderr,"FAIL: %s\n",e.what());return 1;}}
