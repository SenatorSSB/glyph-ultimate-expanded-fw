// Reuse the established production dispatch/storage seam and its hard failures.
#define main preserved_profile_store_main
#include "../profile_store_timeout_host/timeout_harness.cpp"
#undef main
#include "core/RuntimeIdentityWire.hpp"

int main(int argc, char **argv) {
    try {
        require(argc == 2, "fixture argument");
        static Config config = Config_init_default; seed(argv[1], &config);
        const auto before = config_bytes(config); const auto files = storage.files;
        const auto generation = profile_store.Generation(); const auto token = profile_store.LastTransactionToken();
        const unsigned saves = persistence.save_calls;
        InputState inputs; DuplexStream wire; ConfiguratorBackend backend(inputs, nullptr, 0, config, wire);
        uint8_t query[16] = {0xa5, 'G', 'R', 'I', 1, 1, 16, 0, 42};
        auto submit = [&](size_t length) {
            wire.clear(); packetio::COBSPrint out(wire); out.write(uint8_t(CMD_RUNTIME_IDENTITY));
            out.write(query, length); require(out.end(), "identity COBS request");
            const auto frame = wire.tx; wire.tx.clear(); wire.append(frame); backend.SendReport();
        };
        submit(sizeof(query)); auto result = decode(wire.tx);
        require(result.size() == 73 && result[0] == CMD_RUNTIME_IDENTITY && result[17] == 2 && result[9] == 42,
                "Configurator identity is neutral in current context");
        require(std::all_of(result.begin()+25, result.end(), [](uint8_t b){return b==0;}), "neutral has no persistent claim");
        backend.SetRecoveryState(true, false); submit(sizeof(query)); result=decode(wire.tx);
        require(result[17] == 3, "explicit recovery truth");
        for (unsigned index : {4u, 5u, 6u, 8u}) {
            const auto saved = query[index]; query[index] = 0; submit(sizeof(query));
            require(wire.tx.empty(), "malformed identity rejected"); query[index] = saved;
        }
        submit(15); require(wire.tx.empty(), "short request rejected");
        // Its existing reader times out and resynchronizes; never reports success.
        wire.clear(); wire.append({3, uint8_t(CMD_RUNTIME_IDENTITY), 0xa5}); backend.SendReport();
        require(wire.tx.empty(), "partial request never success");
        require(config_bytes(config)==before && storage.files==files && profile_store.Generation()==generation &&
                profile_store.LastTransactionToken()==token && persistence.save_calls==saves, "identity dispatch must not mutate");
        std::puts("runtime_identity_configurator_neutral_recovery_malformed_no_mutation=PASS");
        return 0;
    } catch(const std::exception &e) { std::fprintf(stderr, "%s\n", e.what()); return 1; }
}
