#include <cstdint>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

#include "host_stubs.hpp"

namespace {
enum class FileCase { OpenFailure, SeekFailure, Empty, Payload, ReadError };
FileCase file_case = FileCase::Payload;
bool check_saved = true;
bool end_result = true;
std::vector<uint8_t> output;
enum class WriteMode { Full, Zero, Partial };
WriteMode write_mode = WriteMode::Full;

File make_file() {
    File file;
    file.valid = file_case != FileCase::OpenFailure;
    file.seek_result = file_case != FileCase::SeekFailure;
    if (file_case == FileCase::Payload) {
        file.values.assign(Persistence::config_offset, 0);
        file.values.insert(file.values.end(), {7, 8, 9});
    } else if (file_case == FileCase::ReadError) {
        file.values.assign(Persistence::config_offset, 0);
        file.values.push_back(-1);
    }
    return file;
}

class Out final : public Print {
  public:
    size_t write(uint8_t value) override {
        if (write_mode == WriteMode::Zero) return 0;
        output.push_back(value);
        return write_mode == WriteMode::Partial ? 0 : 1;
    }
    size_t write(const uint8_t *, size_t) override { return 0; }
};

void require(bool condition, const std::string &message) {
    if (!condition) throw std::runtime_error(message);
}
const char *name(FileCase current) {
    switch (current) {
        case FileCase::OpenFailure: return "open_failure";
        case FileCase::SeekFailure: return "seek_failure";
        case FileCase::Empty: return "empty_eof";
        case FileCase::Payload: return "payload_order";
        case FileCase::ReadError: return "read_error_sentinel";
    }
    return "unknown";
}
}

LittleFSStub LittleFS;
File LittleFSStub::open(const char *, const char *) const { return make_file(); }
// The host class is the narrow File/Print double for the production header.
#define _CORE_PERSISTENCE_HPP
// Literal production include: this binary executes the current LoadConfigRaw body.
#include "../../../HAL/pico/src/core/Persistence.cpp"

namespace {
void run_raw(FileCase current, bool validate, bool expected_check, bool expected_seek,
             size_t expected_result, const std::vector<uint8_t> &expected_output,
             WriteMode mode = WriteMode::Full) {
    file_case = current; check_saved = expected_check; write_mode = mode; output.clear(); Out out;
    const size_t result = persistence.LoadConfigRaw(out, validate);
    require(result == expected_result, std::string(name(current)) + ": return");
    require(output == expected_output, std::string(name(current)) + ": output");
    (void)expected_seek;
    std::cout << "case=" << name(current) << " result=PASS\n";
}
}

int main() {
    try {
        run_raw(FileCase::OpenFailure, false, true, false, 0, {});
        run_raw(FileCase::SeekFailure, false, true, false, 0, {});
        run_raw(FileCase::Empty, false, true, true, 1, {});
        run_raw(FileCase::Payload, false, true, true, 1, {7, 8, 9});
        std::cout << "case=validate_false result=PASS\n";
        run_raw(FileCase::Payload, false, true, true, 1, {}, WriteMode::Zero);
        run_raw(FileCase::Payload, false, true, true, 1, {7, 8, 9}, WriteMode::Partial);
        run_raw(FileCase::ReadError, false, true, true, 1, {});
        run_raw(FileCase::Payload, true, false, false, 0, {});
        std::cout << "production_source=HAL/pico/src/core/Persistence.cpp\n";
        std::cout << "production_method=LoadConfigRaw literal include result=PASS\n";
        return 0;
    } catch (const std::exception &error) {
        std::cerr << "result=FAIL error=" << error.what() << "\n";
        return 1;
    }
}
