#include "core/ColdRecoveryIntent.hpp"
#include <cstdio>
#include <stdexcept>
#include <cstring>
#include <initializer_list>
static void need(bool b,const char*m){if(!b)throw std::runtime_error(m);}
int main(){try{
 using namespace ColdRecoveryIntent;
 unsigned cases=0;
 volatile uint32_t s[8]={};
 for(unsigned i=3;i<8;++i)s[i]=0x100+i;
 need(Arm(s)&&s[2]==0x43525432u,"one unique CRT2 arm");++cases;
 need(!Arm(s),"arm cannot overwrite existing intent");++cases;
 need(Consume(s,1)&&s[2]==0,"watchdog timer consumes before recovery");++cases;
 need(!Consume(s,1),"one-shot second consume fails");++cases;
 for(unsigned reason:{0u,2u,3u,0xffffffffu}){s[2]=kMagic;need(!Consume(s,reason)&&s[2]==0,"own stale tag cleared for wrong reason");++cases;}
 for(unsigned word:{0u,1u,2u}){s[word]=7;need(!Arm(s)&&s[word]==7,"foreign mode route conflict untouched");s[word]=0;++cases;}
 for(uint32_t tag:{0u,1u,0x4d445354u,0x525c0000u,0x525d0000u,0xffffffffu,kMagic^1u}){s[2]=tag;need(!Consume(s,1)&&s[2]==tag,"foreign/random/diagnostic marker never authorizes");++cases;}
 for(unsigned word:{0u,1u}){s[0]=s[1]=0;s[2]=kMagic;s[word]=1;need(!Consume(s,1)&&s[2]==0&&s[word]==1,"malformed own tag clears and preserves conflicting selectors");++cases;}
 for(unsigned i=3;i<8;++i)need(s[i]==0x100+i,"scratch3 diagnostic and4-7 boot ROM routing untouched");++cases;
 std::printf("actual_intent_cases=%u PASS\n",cases);return 0;
 }catch(const std::exception&e){std::fprintf(stderr,"FAIL: %s\n",e.what());return 1;}}
