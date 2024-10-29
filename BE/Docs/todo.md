# Cwerg TODO List


Also check the issue tracker: https://github.com/robertmuth/Cwerg/issues?q=is%3Aissue+is%3Aopen+sort%3Aupdated-desc

## Tasks

* augment IR with opcodes for shared memory multiprocessing (ld_l, st_v, 
  atomic operations, cas, etc.)
* explore adding SIMD or vector data types
* explore ways to have inline assembly mixed with the IR
* maybe implement X64-64 backend
* define some virtual syscall that provide SDL like functionality (2D video/audio/input devices)
  so that simple games can be written in a platform neutral way.
* add new misc new opcodes, e.g.  popcnt, crc32c
 * add wider register sizes, e.g. 128bit ints

### Open Questions

* Q: Can we get away with not taking addresses of BBLs
* Q: Which intrinsics are needed (memcpy, memset, acos, pow, ...)
* Q: should the conditional branch instruction specify two target bbls
  instead of one. This would allow us to not have explicit out-going
  edges but we still need the incoming ones for data flow analysis.
