#include "core/RecoveryTaskDiagnostics.hpp"
#include <cstdio>
#include <algorithm>
#include <map>
#include <stdexcept>
#include <utility>
using namespace RecoveryTaskDiagnostics;
void require(bool p,const char*m){if(!p)throw std::runtime_error(m);}
int main(){try{
    std::map<std::pair<unsigned,unsigned>,std::pair<unsigned,unsigned>> decoded;
    for(unsigned stage=0;stage<8;++stage)for(unsigned count=0;count<3;++count){
        State state;state.Enable();for(unsigned i=0;i<count;++i)state.ResetEvent();
        if(stage){state.QueueReadEnd(2,true);if(stage>=2&&stage<=5)state.ClassStage(stage);if(stage>=6)state.ResetCompleted();if(stage==7)state.QueueReadBegin();}
        const auto s=state.Read();require(s.valid&&s.reset_stage==stage&&s.total_resets==count,"decoder fixture retains exact independent bank stage and reset count");
        auto pair=std::minmax(s.pixels[2],s.pixels[3]);const std::pair<unsigned,unsigned> physical={pair.first,pair.second};
        // Generic RESET/UNPLUG completed+continued with no observed DCD reset
        // intentionally uses the same completed class as stage6,total0. Its
        // bank retains stage7 for optional serial detail.
        const std::pair<unsigned,unsigned> semantic={stage==7&&count==0?6u:stage,count};
        const auto found=decoded.find(physical);require(found==decoded.end()||found->second==semantic,"unordered LF4 physical pair cannot alias distinct supported semantic groups");
        decoded[physical]=semantic;
    }
    require(decoded.size()==23,"all24 combinations produce23 groups with exactly one documented completion grouping");
    std::puts("unordered_lf4_decoder=PASS combinations=24 semantic_groups=23 intentional_group=stage6/7,total0 physical_orientation=UNASSUMED");return 0;
}catch(const std::exception&e){std::fprintf(stderr,"FAIL: %s\n",e.what());return 1;}}
