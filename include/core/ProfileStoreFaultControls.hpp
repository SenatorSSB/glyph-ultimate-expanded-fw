#pragma once
#include <cstring>
#include "core/CheckedStorage.hpp"
#include "core/ResourceDiagnostics.hpp"

// Volatile, single-shot controls in the conspicuously marked acceptance
// candidate only. No arbitrary path, persisted arming, reset or device action.
namespace ProfileStoreFaultControls {
struct State { bool armed=false,triggered=false;unsigned kind=0,operation=0,phase=0,result=0,path_class=0,skip=0; };
inline State &Current(){static State state;return state;}
inline bool PathMatches(unsigned path_class,const char *path){
    if(!path)return false;if(*path=='/')++path;
    switch(path_class){
      case 1:return std::strncmp(path,"ultimate-",9)==0&&((path[9]>='0'&&path[9]<='9')||(path[9]>='a'&&path[9]<='f'));
      case 2:return std::strncmp(path,"ultimate-v2-",12)==0;
      case 3:return std::strcmp(path,"ultimate-v2.ctrl")==0||std::strcmp(path,"ultimate-v2.ctmp")==0;
      case 4:return std::strncmp(path,"config-v2.",10)==0;
      default:return false;
    }
}
inline CheckedStorage::Fault Hook(CheckedStorage::Kind kind,CheckedStorage::Operation operation,
                                   CheckedStorage::Phase phase,const char *path){
    auto &state=Current();
    if(!kStrictHardeningCandidate||!state.armed||static_cast<unsigned>(kind)+1!=state.kind||
       static_cast<unsigned>(operation)!=state.operation||static_cast<unsigned>(phase)+1!=state.phase||
       !PathMatches(state.path_class,path))return CheckedStorage::Fault::None;
    if(state.skip){--state.skip;return CheckedStorage::Fault::None;}
    state.armed=false;state.triggered=true;
    return state.result==1?CheckedStorage::Fault::Fail:CheckedStorage::Fault::LostAcknowledgement;
}
inline bool Arm(unsigned kind,unsigned operation,unsigned phase,unsigned result,unsigned path_class,unsigned skip,bool clear){
    static_assert(static_cast<unsigned>(CheckedStorage::Operation::Rename)==10,"fault operation wire mapping changed");
    if(!kStrictHardeningCandidate)return false;
    if(clear){Current()={};CheckedStorage::SetFaultHook(nullptr);return true;}
    if(Current().armed||kind<1||kind>3||operation<1||operation>10||skip>8||
       !((phase==1&&result==1)||(phase==2&&result==2))||path_class<1||path_class>4)return false;
    if((path_class==1&&kind!=1)||((path_class==2||path_class==3)&&kind!=2)||(path_class==4&&kind!=3))return false;
    if(operation==static_cast<unsigned>(CheckedStorage::Operation::Remove)&&path_class!=1)return false;
    Current()={true,false,kind,operation,phase,result,path_class,skip};
    CheckedStorage::SetFaultHook(Hook);return true;
}
}
