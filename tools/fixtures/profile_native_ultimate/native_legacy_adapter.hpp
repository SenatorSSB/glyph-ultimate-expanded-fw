#pragma once
// Test-only capture/replay adapter. The unmodified Stage-C assertions and input
// vectors run through the production native codec/evaluator on replay. Capture
// records actual supplied profile/context values, never resolver semantics.
#include "modes/Ultimate.hpp"
#include "modes/UltimateNativeProfile.hpp"
#include "core/Sha256.hpp"
#include <pb_encode.h>
#include <pb_decode.h>
#include <cstdlib>
#include <cstdio>
#include <fstream>
#include <iterator>
#include <vector>
#include <string>

class NativeActual {
 public:
    void SetConfig(GameModeConfig &config,const UltimateProfile *selected) {
        const std::string directory=std::getenv("GLYPH_NATIVE_REPLAY_DIR");
        const bool capture=std::getenv("GLYPH_NATIVE_CAPTURE")!=nullptr;
        // An absent legacy reference is a source-owned baseline control in the
        // original oracle. Replay uses an explicit conversion of those same
        // baseline tables, never the native-unavailable runtime fallback.
        static UltimateProfile fallback;
        if(!selected) {
            std::ifstream input(directory+"/fallback-legacy.pb",std::ios::binary);
            std::vector<uint8_t> bytes((std::istreambuf_iterator<char>(input)),{});
            auto decoder=pb_istream_from_buffer(bytes.data(),bytes.size());
            if(!pb_decode(&decoder,UltimateProfile_fields,&fallback)) std::abort();
        }
        const auto &p=selected?*selected:fallback;
        size_t size=0;if(!pb_get_encoded_size(&size,UltimateProfile_fields,&p))std::abort();
        std::vector<uint8_t> bytes(size);auto encoder=pb_ostream_from_buffer(bytes.data(),bytes.size());
        if(!pb_encode(&encoder,UltimateProfile_fields,&p))std::abort();
        uint8_t context[32],digest[32];if(!ultimate_native::ContextDigest(config,context))std::abort();
        Sha256 h;h.Update(bytes.data(),bytes.size());h.Update(context,32);h.Final(digest);
        char key[65];for(unsigned i=0;i<32;++i)std::snprintf(key+i*2,3,"%02x",digest[i]);
        const std::string prefix=directory+"/"+key;
        if(capture) {
            std::ofstream profile(prefix+".legacy.pb",std::ios::binary);profile.write(reinterpret_cast<const char *>(bytes.data()),bytes.size());profile.close();
            if(!pb_get_encoded_size(&size,GameModeConfig_fields,&config))std::abort();bytes.resize(size);encoder=pb_ostream_from_buffer(bytes.data(),bytes.size());
            if(!pb_encode(&encoder,GameModeConfig_fields,&config))std::abort();
            std::ofstream row(prefix+".context.pb",std::ios::binary);row.write(reinterpret_cast<const char *>(bytes.data()),bytes.size());
            actual.SetConfig(config,selected);return;
        }
        std::ifstream input(prefix+".native.pb",std::ios::binary);bytes.assign(std::istreambuf_iterator<char>(input),{});
        ultimate_native::PayloadLease lease;
        if(!ultimate_native::DecodeProfile(bytes.data(),bytes.size(),profile,lease)||!ultimate_native::ValidProfile(profile)||
           !ultimate_native::CopyProgram(ultimate_native::CandidateView(),owned,++generation,true)||
           !ultimate_native::BindOwned(profile,owned,owned_lease))std::abort();
        lease.Release();configuration=config;configuration.ultimate_profile_engine=1;
        actual.SetConfig(configuration,&profile,&owned.view);
        if(actual.ActiveEngine()!=Ultimate::Engine::NativeAbi1)std::abort();
    }
    void UpdateOutputs(const InputState &in,OutputState &out,CommunicationBackendId backend) {actual.UpdateOutputs(in,out,backend);}
 private:
    Ultimate actual;
    GameModeConfig configuration{};
    UltimateProfile profile{};
    ultimate_native::OwnedProgram owned;
    ultimate_native::PayloadLease owned_lease;
    uint32_t generation=0;
};
