#include "pb_arduino.h"

#include <Print.h>
#include <Stream.h>

static bool pb_print_write(pb_ostream_t *stream, const pb_byte_t *buf, size_t count) {
    Print *p = reinterpret_cast<Print *>(stream->state);
    size_t written = p->write(buf, count);
    return written == count;
};

pb_ostream_s as_pb_ostream(Print &p) {
    return { pb_print_write, &p, SIZE_MAX, 0 };
};

static bool pb_stream_read(pb_istream_t *stream, pb_byte_t *buf, size_t count) {
    Stream *s = reinterpret_cast<Stream *>(stream->state);
    size_t read = s->readBytes(buf, count);
    if (read == 0) {
        stream->bytes_left = 0;
        return false;
    }
    return read == count;
};

pb_istream_s as_pb_istream(Stream &s, size_t bytes_left) {
#ifndef PB_NO_ERRMSG
    return { pb_stream_read, &s, bytes_left, 0 };
#else
    return { pb_stream_read, &s, bytes_left };
#endif
}

pb_istream_s as_pb_istream(Stream &s) {
    return as_pb_istream(s, SIZE_MAX);
};
