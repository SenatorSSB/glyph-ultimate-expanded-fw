#ifndef GLYPH_CHECKED_STORAGE_FILE_HPP
#define GLYPH_CHECKED_STORAGE_FILE_HPP
#include <Arduino.h>
#include "core/CheckedStorage.hpp"
// Bounded Stream bridge for existing Nanopb/CRC code. Every explicit close is
// checked; no Arduino File wrapper owns or closes this native handle.
class CheckedStorageFile : public Stream {
  public:
    CheckedStorageFile(const char *path, const char *mode) {
        _result = CheckedStorage::Open(_file, path, mode[0] == 'w', CheckedStorage::Kind::Config); remember_uncertainty();
        if (_result && mode[0] != 'w') _result = CheckedStorage::Stat(path, &_size, CheckedStorage::Kind::Config); remember_uncertainty();
        _failed = !_result;
    }
    ~CheckedStorageFile() { if (_file.opened) close(); }
    explicit operator bool() const { return _file.opened && !_failed; }
    int available() override { return _size >= _position ? _size - _position : 0; }
    int read() override { uint8_t byte; return read(&byte, 1) == 1 ? byte : -1; }
    int read(uint8_t *bytes, size_t size) {
        _result = CheckedStorage::Read(_file, bytes, size); remember_uncertainty();
        if (!_result) { _failed = true; return -1; }
        _position += _result.bytes; return _result.bytes;
    }
    int peek() override { auto position = _position; int byte = read(); if (byte >= 0 && !seek(position)) return -1; return byte; }
    size_t write(uint8_t byte) override { return write(&byte, 1); }
    size_t write(const uint8_t *bytes, size_t size) override {
        _result = CheckedStorage::Write(_file, bytes, size); remember_uncertainty();
        if (!_result) { _failed = true; return 0; }
        _position += _result.bytes; if (_position > _size) _size = _position;
        return _result.bytes;
    }
    void flush() override { sync(); }
    bool sync() { _result = CheckedStorage::Sync(_file); remember_uncertainty(); if (!_result) _failed = true; return bool(_result); }
    bool seek(size_t offset) { _result = CheckedStorage::Seek(_file, offset); remember_uncertainty(); if (!_result) _failed = true; else _position = offset; return bool(_result); }
    size_t size() const { return _size; }
    size_t position() const { return _position; }
    bool close() { _result = CheckedStorage::Close(_file); remember_uncertainty(); if (!_result) _failed = true; return !_failed; }
    bool failed() const { return _failed; }
    bool uncertain() const { return _uncertain; }
    CheckedStorage::Result last_result() const { return _result; }
  private:
    CheckedStorage::File _file;
    CheckedStorage::Result _result;
    size_t _position = 0, _size = 0;
    bool _failed = false;
    bool _uncertain = false;
    void remember_uncertainty() { if (_result.outcome == CheckedStorage::Outcome::Uncertain) _uncertain = true; }
};
#endif
