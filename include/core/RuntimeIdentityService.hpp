#pragma once
#include "core/RuntimeIdentity.hpp"

namespace runtime_identity {
class Service {
  public:
    template<class Wire>
    void Poll(Wire &wire, CommunicationBackend *primary, const Config &config,
              const ProfileStore &store, const Ultimate &ultimate, uint32_t now) {
        // This reader exists only in the current primary XInput session.
        if (!primary || primary->BackendId() != COMMS_BACKEND_XINPUT) return;
        _parser.Expire(now);
        for (unsigned consumed = 0; consumed < 32 && wire.available() > 0; ++consumed) {
            const int byte = wire.read();
            if (byte < 0) return;
            uint64_t token = 0;
            if (!_parser.Consume(static_cast<uint8_t>(byte), now, token)) continue;
            // Complete admission before digest work or transmission. Leave the
            // existing viewer's admission reserve and never wait for the host.
            if (wire.availableForWrite() >= static_cast<int>(kResponseBytes + 32)) {
                uint8_t response[kResponseBytes];
                EncodeResponse(token, Observe(primary, config, store, ultimate), response);
                wire.write(response, sizeof(response));
            }
            return;
        }
    }
  private:
    RequestParser _parser;
};
} // namespace runtime_identity
