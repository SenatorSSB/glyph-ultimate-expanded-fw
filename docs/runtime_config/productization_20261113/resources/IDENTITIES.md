# Reviewed core0 identities

The three independently built firmware images have separate ELF graph receipts. Firmware artifacts live in the productization custody directory.

|Lane|Source|Core0 witness file|Maximum affected|
|---|---|---|---:|
|Combined|84556d904f067bda5a101e6297689239ecd04aae|combined.json|2048 including inherited legacy SET staging, 2044 lifecycle|
|Isolated startup|7d1f6a3ba99627e88dfdaf404e08ff816902ccfc|startup.json|2044 among affected, 2048 retained legacy staging|
|Isolated selection|f6655e30c6d94b4468711053e5c6c76c00be9cc7|selection.json|2036 among affected, 2048 retained legacy staging|

Each receipt is restricted to the actual source/ELF pair it names. Earlier development images are historical evidence only. The isolated `c0ac5106` linker emitted a 40-byte core0 loop with a 2056-byte inherited stage-write bound. Its successor performs the identical receiver-idle predicate in a returned leaf before a write. The combined image already had a 32-byte loop without this isolate-only adjustment.
