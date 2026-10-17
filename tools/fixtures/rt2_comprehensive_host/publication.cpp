#include "state.hpp"
#include <cstdio>
#include <stdexcept>
#include <thread>
RecoveryTaskDiagnostics::State *subject;
unsigned seen=0;bool inject=true;
void require(bool p,const char*m){if(!p)throw std::runtime_error(m);}
bool same_task(const RecoveryTaskDiagnostics::Snapshot&a,const RecoveryTaskDiagnostics::Snapshot&b){
    for(unsigned i=0;i<8;++i)if(a.pixels[i]!=b.pixels[i])return false;
    return a.valid==b.valid&&a.entered==b.entered&&a.returned==b.returned&&a.active==b.active&&a.first_id==b.first_id&&a.latest_returned==b.latest_returned&&a.first_returned==b.first_returned&&a.total_resets==b.total_resets&&a.pre_first_resets==b.pre_first_resets&&a.first_resets==b.first_resets&&a.active_resets==b.active_resets&&a.post_first_resets==b.post_first_resets&&a.reset_completed==b.reset_completed&&a.first_reset_completed==b.first_reset_completed&&a.reset_consumed==b.reset_consumed&&a.reset_continued==b.reset_continued&&a.reset_stage==b.reset_stage&&a.processing_invocation==b.processing_invocation&&a.setup_consumed==b.setup_consumed&&a.control_began==b.control_began&&a.class_entered==b.class_entered&&a.class_returned==b.class_returned&&a.queue_attempted==b.queue_attempted&&a.queue_accepted==b.queue_accepted&&a.queue_failed==b.queue_failed&&a.reset_dropped==b.reset_dropped&&a.setup_dropped==b.setup_dropped&&a.max_occupancy==b.max_occupancy&&a.empty_reads==b.empty_reads&&a.event_flags==b.event_flags&&a.task_flags==b.task_flags&&a.raw_setup_seen==b.raw_setup_seen&&a.pullup==b.pullup&&a.configured_current==b.configured_current&&a.task_pixel==b.task_pixel&&a.progress_pixel==b.progress_pixel&&a.dashboard==b.dashboard;
}
void GlyphPublicationBoundary(unsigned phase){
    if(!inject)return;++seen;
    if(phase<=3)subject->ResetEvent();
    std::thread observer([]{require(!subject->Read().valid,"odd writer snapshot rejected without waiting for paused writer");RecoveryTaskDiagnostics::Snapshot owned;owned.valid=123;subject->ReadInto(owned);require(!owned.valid,"caller-owned snapshot clears stale valid marker during mixed publication");});observer.join();
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
    Snapshot owned;owned.valid=123;state.ReadInto(owned);require(same_task(owned,s),"ReadInto matches Read after publication retry for every scalar and dashboard field");
    require(seen>=8,"foreground producer and task publication boundaries all exercised");
    std::puts("publication_boundaries=PASS pre/active/post attribution first/later identity odd-foreground/producer/task bounded-rejection retry");return 0;
}catch(const std::exception&e){std::fprintf(stderr,"FAIL: %s\n",e.what());return 1;}}
