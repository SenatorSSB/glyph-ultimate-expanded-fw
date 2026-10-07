#ifndef __PB_ARDUINO_H
#define __PB_ARDUINO_H

#include "pb_encode.h"
#include "pb_decode.h"

#include <Arduino.h>

//! Convert an object implementing Print into a nanopb ostream
pb_ostream_s as_pb_ostream(Print &p);

//! Convert an object implementing Stream into a nanopb istream
pb_istream_s as_pb_istream(Stream &p, size_t bytes_left);
pb_istream_s as_pb_istream(Stream &p);

#endif