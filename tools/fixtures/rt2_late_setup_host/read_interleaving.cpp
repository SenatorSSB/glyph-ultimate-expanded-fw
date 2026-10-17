#include "core/RecoveryPrivateDcdDiagnostics.hpp"
#include <cstdio>
#include <stdexcept>
using namespace RecoveryPrivateDcdDiagnostics;
State *subject=nullptr;unsigned selected=0,seen=0;bool fired=false;
void GlyphReadBoundary(unsigned point){
    ++seen;if(point!=selected||fired)return;fired=true;
    // A real serialized writer publishes a complete next transaction between
    // two operations of the actual production bounded reader body.
    subject->Initial(ResetBit);subject->Return(ResetBit,SetupBit,3);
}
int main(){try{
 for(unsigned point=1;point<=15;++point){
  State state;state.Enable();state.Initial(SetupBit|BuffBit);state.Return(SetupBit|BuffBit,0,1);
  subject=&state;selected=point;seen=0;fired=false;Snapshot s;state.ReadInto(s);
  if(!fired||seen!=15||s.valid)throw std::runtime_error("bounded reader accepted bank changed at actual payload load boundary");
  selected=0;state.ReadInto(s);
  if(!s.valid||s.entries!=2||s.returns!=2||s.first_late_id!=2||s.first_late_s0!=ResetBit||s.first_late_s1!=SetupBit)throw std::runtime_error("closed actual writer history not readable after rejected interleave");
 }
 std::puts("actual_reader_payload_interleavings_15=PASS");return 0;
}catch(const std::exception&e){std::fprintf(stderr,"FAIL: %s\n",e.what());return 1;}}
