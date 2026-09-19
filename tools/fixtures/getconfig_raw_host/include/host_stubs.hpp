#ifndef GLYPH_GETCONFIG_RAW_HOST_STUBS_HPP
#define GLYPH_GETCONFIG_RAW_HOST_STUBS_HPP

#include <cstddef>
#include <cstdint>
#include <string>
#include <vector>

class Print {
  public:
    virtual ~Print() = default;
    virtual size_t write(uint8_t value) = 0;
    virtual size_t write(const uint8_t *buffer, size_t size) = 0;
};

class Stream : public Print {
  public:
    virtual int available() = 0;
    virtual int read() = 0;
    virtual int peek() = 0;
    virtual void flush() = 0;
};

class File {
  public:
    bool valid = false;
    bool seek_result = true;
    std::vector<int> values;
    size_t position = 0;
    bool operator!() const { return !valid; }
    explicit operator bool() const { return valid; }
    size_t size() const { return values.size(); }
    int available() const { return static_cast<int>(values.size() - position); }
    bool seek(size_t offset) { if (!seek_result) return false; position = offset; return true; }
    int read() { return position < values.size() ? values[position++] : -1; }
    size_t read(uint8_t *buffer, size_t size) {
        size_t count = 0;
        while (count < size && position < values.size() && values[position] != -1) {
            buffer[count++] = static_cast<uint8_t>(values[position++]);
        }
        return count;
    }
    size_t write(const uint8_t *, size_t size) { return size; }
    void close() {}
};

struct LittleFSStub {
    bool begin() { return true; }
    void end() {}
    File open(const char *, const char *) const;
};
extern LittleFSStub LittleFS;

struct Config {};
#define Config_init_default Config{}
inline int Config_msg = 0;
#define Config_fields (&Config_msg)
struct pb_istream_t { const char *errmsg = nullptr; };
struct pb_ostream_t { size_t bytes_written = 0; };
inline pb_istream_t as_pb_istream(File &, size_t) { return {}; }
inline pb_ostream_t as_pb_ostream(File &) { return {}; }
inline bool pb_decode(pb_istream_t *, const void *, Config *) { return true; }
inline bool pb_encode(pb_ostream_t *, const void *, Config *) { return true; }
inline bool pb_get_encoded_size(size_t *size, const void *, Config *) { *size = 0; return true; }

class CRC32 {
  public:
    void update(uint8_t) {}
    uint32_t finalize() { return 0; }
};

class Persistence {
  public:
    struct ConfigHeader { size_t config_size = 0; uint32_t config_crc = 0; };
    static constexpr size_t config_offset = sizeof(ConfigHeader);
    Persistence();
    ~Persistence();
    bool SaveConfig(Config &);
    bool LoadConfig(Config &);
    bool CheckSavedConfig();
    size_t LoadConfigRaw(Print &, bool validate = true);
  private:
    static constexpr char config_filename[] = "config.bin";
    bool CheckSavedConfig(File &);
};
extern Persistence persistence;

#endif
