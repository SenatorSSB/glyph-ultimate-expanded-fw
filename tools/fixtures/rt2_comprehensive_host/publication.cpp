#include "state.hpp"
#include <cstdio>
#include <stdexcept>
#include <thread>
RecoveryTaskDiagnostics::State *subject;
unsigned seen=0;bool inject=true;
void require(bool p,const char*m){if(!p)throw std::runtime_error(m);}
void GlyphPublicationBoundary(unsigned phase){
    if(!inject)return;++seen;
    if(phase<=3)subject->ResetEvent();
    std::thread observer([]{require(!subject->Read().valid,"odd writer snapshot rejected without waiting for paused writer");});observer.join();
}
int main(){try{
    using namespace RecoveryTaskDiagnostics;
    State state;subject=&state;state.Enable();state.Arm();
    state.ResetEvent();require(state.Read().first_resets==0,"pre-task reset excluded from first task");
    state.Enter();auto s=state.Read();require(s.valid&&s.active==1&&s.first_id==1&&s.first_resets==1&&s.active_resets==1&&s.pre_first_resets==2,"reset attribution follows exact active publication linearization");
    state.Return();s=state.Read();require(s.first_resets==1&&s.first_returned&&s.latest_returned==1&&s.pixels[0]==Green,"first returned anchor survives post-clear reset");
    inject=false;state.Enter();state.ResetEvent();state.ResetEvent();s=state.Read();require(s.active==2&&s.active_resets==2&&s.first_resets==1&&s.pixels[0]==White&&s.post_first_resets==3,"later active independent of anchored first return");state.Return();
    inject=true;state.QueueSent(1,1,false,16);state.QueueReadBegin();state.QueueReadEnd(1,true);
    state.ClassStage(2);state.ClassStage(3);state.ClassStage(4);state.ClassStage(5);state.ResetCompleted();state.QueueReadBegin();
    s=state.Read();require(s.valid&&s.queue_failed==1&&s.reset_dropped==1&&s.max_occupancy==16&&s.reset_consumed==1&&s.reset_completed==1&&s.reset_continued==1,"bounded producer/task snapshots retry after interrupted publication");
    require(seen>=8,"foreground producer and task publication boundaries all exercised");
    std::puts("publication_boundaries=PASS pre/active/post attribution first/later identity odd-foreground/producer/task bounded-rejection retry");return 0;
}catch(const std::exception&e){std::fprintf(stderr,"FAIL: %s\n",e.what());return 1;}}
