#include <iostream>
#include <stdexcept>
#include <vector>

bool host_getconfig_check_saved = true;
size_t host_getconfig_raw_result = 0;
std::vector<uint8_t> host_getconfig_raw_bytes;
bool host_packet_end_result = true;

#define private public
#include "../../../HAL/pico/include/comms/ConfiguratorBackend.hpp"
#undef private

namespace {
class TestStream final : public Stream {
  public:
    std::vector<uint8_t> output;
    int available() override { return 0; }
    int read() override { return -1; }
    int peek() override { return -1; }
    void flush() override {}
    size_t write(uint8_t value) override { output.push_back(value); return 1; }
    size_t write(const uint8_t *buffer, size_t size) override {
        output.insert(output.end(), buffer, buffer + size); return size;
    }
};
void require(bool condition, const char *message) {
    if (!condition) throw std::runtime_error(message);
}
}

pb_istream_t as_pb_istream(Stream &) { return {nullptr}; }
pb_ostream_t as_pb_ostream(Print &) { return {0}; }
bool pb_decode(pb_istream_t *, const void *, void *) { return true; }
Persistence persistence;
bool Persistence::SaveConfig(Config &) { return true; }

// Literal production include: this binary executes the current GetConfig body.
#include "../../../HAL/pico/src/comms/ConfiguratorBackend.cpp"

int main() {
    try {
        InputState inputs;
        Config config{};
        TestStream stream;
        ConfiguratorBackend backend(inputs, nullptr, 0, config, stream);

        host_getconfig_check_saved = false;
        host_getconfig_raw_result = 1;
        host_getconfig_raw_bytes = {9};
        require(!backend.HandleGetConfig(), "invalid check result");
        require(stream.output == std::vector<uint8_t>({CMD_ERROR, 'C', 'o', 'n', 'f', 'i', 'g', ' ', 'f', 'i', 'l', 'e', ' ', 'i', 's', ' ', 'i', 'n', 'v', 'a', 'l', 'i', 'd', 0}), "invalid check packet");

        stream.output.clear();
        host_getconfig_check_saved = true;
        host_getconfig_raw_result = 0;
        host_getconfig_raw_bytes = {7, 8};
        require(backend.HandleGetConfig(), "packet end result");
        require(stream.output == std::vector<uint8_t>({CMD_SET_CONFIG, 7, 8}), "raw packet order");

        stream.output.clear();
        host_packet_end_result = false;
        require(!backend.HandleGetConfig(), "packet end failure propagation");
        require(stream.output == std::vector<uint8_t>({CMD_SET_CONFIG, 7, 8}), "packet end failure bytes");

        std::cout << "case=invalid_check_no_raw_load result=PASS\n";
        std::cout << "case=raw_result_ignored_packet_end_wins result=PASS\n";
        std::cout << "case=packet_end_failure_propagates result=PASS\n";
        std::cout << "production_source=HAL/pico/src/comms/ConfiguratorBackend.cpp\n";
        std::cout << "production_handler_cases=2 result=PASS\n";
        return 0;
    } catch (const std::exception &error) {
        std::cerr << "result=FAIL error=" << error.what() << "\n";
        return 1;
    }
}
