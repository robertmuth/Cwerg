module:

pub rec TimeSpec:
    sec uint
    nano_sec uint

pub @extern @cdecl fun nanosleep(req ^TimeSpec, rem ^!TimeSpec) s32:

pub @extern @cdecl fun write(fd s32, s ^u8, size uint) sint:

pub @extern @cdecl fun read(fd s32, s ^!u8, size uint) sint:

pub @wrapped type Error = s32

pub @wrapped type FD = s32

pub global Stdin = wrap_as(0, FD)

pub global Stdout = wrap_as(1, FD)

pub global Stderr = wrap_as(2, FD)

pub fun FileWrite(fd FD, buffer slice(u8)) union(uint, Error):
    let res = write(unwrap(fd), front(buffer), len(buffer))
    if res < 0:
        return wrap_as(as(res, s32), Error)
    else:
        return as(res, uint)

pub fun FileRead(fd FD, buffer slice!(u8)) union(uint, Error):
    let res = read(unwrap(fd), front!(buffer), len(buffer))
    if res < 0:
        return wrap_as(as(res, s32), Error)
    else:
        return as(res, uint)

pub fun TimeNanoSleep(req ^TimeSpec, rem ^!TimeSpec) Error:
    let res = nanosleep(req, rem)
    return wrap_as(res, Error)
