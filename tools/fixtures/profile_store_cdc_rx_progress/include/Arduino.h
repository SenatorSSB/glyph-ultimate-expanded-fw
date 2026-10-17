#pragma once
#include <cstdint>
#include <cstddef>
class Print {
public:
 virtual ~Print() = default;
 virtual size_t write(uint8_t) = 0;
 virtual size_t write(const uint8_t *p, size_t n) { size_t k=0; while(k<n && write(p[k])) ++k; return k; }
};
class Stream : public Print {
public:
 virtual int available() { return 0; }
 virtual int availableForWrite() { return 0; }
 virtual int peek() { return -1; }
 virtual int read() { return -1; }
 virtual void flush() {}
};
uint32_t millis();
void delay(unsigned long);
void yield();
