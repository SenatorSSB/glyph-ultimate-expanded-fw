#pragma once
#include <Arduino.h>
namespace packetio {
class COBSStream : public Stream {
public:
    static constexpr int EOF = -1;
    static constexpr int EOP = -2;
    explicit COBSStream(Stream &source) : source_(source) {}
    int available() override { return source_.available(); }
    int read() override { return source_.read(); }
    int peek() override { return source_.peek(); }
    void flush() override { source_.flush(); }
    size_t write(uint8_t value) override { return source_.write(value); }
    size_t write(const uint8_t *data, size_t size) override { return source_.write(data, size); }
    void next() {}
private:
    Stream &source_;
};
}
