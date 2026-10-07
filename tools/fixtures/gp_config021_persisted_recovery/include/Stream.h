#pragma once
#include "Print.h"
class Stream : public Print {
public:
    virtual int available() = 0;
    virtual int read() = 0;
    virtual int peek() = 0;
    virtual void flush() = 0;
    virtual size_t readBytes(uint8_t *data, size_t length) {
        size_t n = 0;
        for (; n < length; ++n) {
            int byte = read();
            if (byte < 0) break;
            data[n] = static_cast<uint8_t>(byte);
        }
        return n;
    }
};
