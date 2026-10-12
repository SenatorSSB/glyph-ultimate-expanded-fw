#include "host_stubs.hpp"

#include <stdexcept>

#include <pb_decode.h>
#include <pb_encode.h>

#define private public
#include "comms/ConfiguratorBackend.hpp"
#undef private

uint32_t host_millis = 0;
Persistence persistence;
ProfileStore profile_store;

class TestStream final : public Stream {
 public:
  std::vector<uint8_t> input;
  std::vector<uint8_t> output;
  size_t cursor = 0;
  int available() override { return static_cast<int>(input.size() - cursor); }
  int read() override { return cursor < input.size() ? input[cursor++] : -1; }
  int peek() override { return cursor < input.size() ? input[cursor] : -1; }
  void flush() override {}
  size_t write(uint8_t value) override { output.push_back(value); return 1; }
  size_t write(const uint8_t *data, size_t length) override {
    output.insert(output.end(), data, data + length); return length;
  }
};

static void require(bool value, const char *message) { if (!value) throw std::runtime_error(message); }

static std::vector<uint8_t> decode(const std::vector<uint8_t> &encoded) {
  require(!encoded.empty() && encoded.back() == 0, "missing COBS delimiter");
  std::vector<uint8_t> decoded;
  for (size_t offset = 0; offset + 1 < encoded.size();) {
    const uint8_t count = encoded[offset++];
    require(count != 0 && offset + count - 1 <= encoded.size(), "malformed COBS response");
    decoded.insert(decoded.end(), encoded.begin() + offset, encoded.begin() + offset + count - 1);
    offset += count - 1;
    if (count != 0xff && offset + 1 < encoded.size()) decoded.push_back(0);
  }
  return decoded;
}

static std::vector<uint8_t> status_packet() {
  ProfileStoreRequest request = ProfileStoreRequest_init_default;
  request.protocol_version = 1;
  request.operation = PROFILE_STORE_STATUS;
  size_t size = 0;
  require(pb_get_encoded_size(&size, ProfileStoreRequest_fields, &request), "status size");
  std::vector<uint8_t> raw(size);
  pb_ostream_t output = pb_ostream_from_buffer(raw.data(), raw.size());
  require(pb_encode(&output, ProfileStoreRequest_fields, &request), "status encode");
  raw.resize(output.bytes_written);
  TestStream wire;
  packetio::COBSPrint encoder(wire);
  encoder.write(static_cast<uint8_t>(CMD_PROFILE_STORE));
  encoder.write(raw.data(), raw.size());
  require(encoder.end(), "status frame end");
  return wire.output;
}

int main() {
  try {
    InputState inputs;
    Config config = Config_init_default;
    TestStream wire;
    ConfiguratorBackend backend(inputs, nullptr, 0, config, wire);
    const Config before = config;
    const uint32_t generation_before = profile_store.Generation();

    // Real COBS: code 3 decodes to command 9 plus the incomplete protobuf byte 0x08.
    wire.input = {3, static_cast<uint8_t>(CMD_PROFILE_STORE), 0x08};
    backend.SendReport();
    const std::vector<uint8_t> timeout = decode(wire.output);
    require(timeout.size() == 1 + std::strlen("Profile store frame timeout"), "timeout response shape");
    require(timeout[0] == CMD_ERROR, "timeout command");
    require(std::memcmp(timeout.data() + 1, "Profile store frame timeout", timeout.size() - 1) == 0, "timeout text");
    require(std::memcmp(&before, &config, sizeof(Config)) == 0, "timeout mutated Config");
    require(profile_store.Generation() == generation_before && profile_store.mutation_calls == 0, "timeout mutated ProfileStore");
    require(host_millis >= 5000, "virtual clock did not cross timeout");

    const std::vector<uint8_t> later = status_packet();
    wire.input.insert(wire.input.end(), 0);  // required delimiter resynchronizes the aborted frame.
    wire.input.insert(wire.input.end(), later.begin(), later.end());
    wire.output.clear();
    backend.SendReport();
    const std::vector<uint8_t> accepted = decode(wire.output);
    require(!accepted.empty() && accepted[0] == CMD_PROFILE_STORE, "later STATUS not accepted");
    ProfileStoreResponse response = ProfileStoreResponse_init_default;
    pb_istream_t input = pb_istream_from_buffer(accepted.data() + 1, accepted.size() - 1);
    require(pb_decode(&input, ProfileStoreResponse_fields, &response), "STATUS response decode");
    require(response.status == PROFILE_STORE_OK, "STATUS result");
    require(std::memcmp(&before, &config, sizeof(Config)) == 0, "STATUS changed Config");
    require(profile_store.mutation_calls == 0, "STATUS changed ProfileStore");
    return 0;
  } catch (const std::exception &error) {
    return 1;
  }
}
