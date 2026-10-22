#include "modes/Ultimate.hpp"
#include "modes/UltimateNativeEvaluator.hpp"
#include <fstream>
#include <iterator>
#include <vector>
#include <cstdio>
#include <cstdlib>
unsigned native_socd_visits=0;
static void require(bool yes,const char *label){if(!yes){std::fprintf(stderr,"FAIL %s\n",label);std::exit(1);}}
int main(int argc,char **argv){
 require(argc==2,"mutation control profile");std::ifstream f(argv[1],std::ios::binary);std::vector<uint8_t> raw((std::istreambuf_iterator<char>(f)),{});
 static UltimateProfile p;ultimate_native::PayloadLease lease;require(ultimate_native::DecodeProfile(raw.data(),raw.size(),p,lease)&&ultimate_native::ValidProfile(p),"mutation fixture admitted");
 static ultimate_native::OwnedProgram active;ultimate_native::PayloadLease owned;require(ultimate_native::CopyProgram(ultimate_native::CandidateView(),active,7,true)&&ultimate_native::BindOwned(p,active,owned),"owned publication");
 GameModeConfig context{};context.mode_id=MODE_ULTIMATE;context.ultimate_profile_engine=1;context.socd_pairs_count=1;context.socd_pairs[0]={static_cast<Button>(49),BTN_LF2,static_cast<SocdType>(1)};
 Ultimate mode;mode.SetConfig(context,&p,&active.view);require(mode.ActiveEngine()==Ultimate::Engine::NativeAbi1,"actual native engine bound");
 auto output=[&](uint64_t bits){InputState input{};input.buttons=bits;OutputState o{};mode.UpdateOutputs(input,o,COMMS_BACKEND_XINPUT);return o;};
 auto out=output(uint64_t{1}<<48);require(out.a,"original-domain binding reads carrier49 exact bit48");
 require(native_socd_visits==1,"exactly one SOCD execution per input frame");
 out=output((uint64_t{1}<<48)|2);require(out.a,"original A survives post-SOCD cancellation");
 out=output(uint64_t{1}<<1);require(!out.a,"old intrinsic carrier2 has no extra native action");
 out=output((uint64_t{1}<<50)|(uint64_t{1}<<51));require(out.leftStickX==13&&out.leftStickY==43,"unique table priority wins independently of serialized order");
 out=output(uint64_t{1}<<51);require(out.leftStickX==14&&out.leftStickY==44,"losing or inactive table has no influence");
 auto copy=active.view;Ultimate borrowed;borrowed.SetConfig(context,&p,&copy);require(borrowed.ActiveEngine()==Ultimate::Engine::NativeUnavailable,"copied view cannot impersonate owned active view");
 ++active.view.generation;out=output(uint64_t{1}<<48);require(!out.buttons&&out.leftStickX==128&&out.leftStickY==128,"latched active generation rejects stale program");
 std::puts("PASS named native source mutation control assertions");
}
