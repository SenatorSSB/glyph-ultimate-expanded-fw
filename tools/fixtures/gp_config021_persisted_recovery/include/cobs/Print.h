#pragma once
#include <Arduino.h>
namespace packetio {
class COBSPrint : public Print {
public:
    explicit COBSPrint(Stream &sink) : sink_(sink) {}
    size_t write(uint8_t value) override { return sink_.write(value); }
    size_t write(const uint8_t *data, size_t size) override { return sink_.write(data, size); }
    bool end() { return true; }
private:
    Stream &sink_;
};
}
