module:
; For error codes see
; https://www.chromium.org/chromium-os/developer-library/reference/linux-constants/errnos/

pub rec TimeSpec:
    sec uint
    nano_sec uint

pub rec WinSize:
    ws_row u16
    ws_col u16
    ws_xpixel u16
    ws_ypixel u16

pub wrapped type Error = s32
pub global EPERM = wrap_as(-1, Error)
pub global ENOENT = wrap_as(-2, Error)
pub global ESRCH = wrap_as(-3, Error)
pub global EINTR = wrap_as(-4, Error)
pub global EIO = wrap_as(-5, Error)
pub global ENXIO = wrap_as(-6, Error)
pub global E2BIG = wrap_as(-7, Error)
pub global ENOEXEC = wrap_as(-8, Error)
pub global EBADF = wrap_as(-9, Error)
pub global ECHILD = wrap_as(-10, Error)
pub global EAGAIN = wrap_as(-11, Error)
pub global ENOMEM = wrap_as(-12, Error)
pub global EACCES = wrap_as(-13, Error)
pub global EFAULT = wrap_as(-14, Error)
pub global ENOTBLK = wrap_as(-15, Error)
pub global EBUSY = wrap_as(-16, Error)
pub global EEXIST = wrap_as(-17, Error)
pub global EXDEV = wrap_as(-18, Error)
pub global ENODEV = wrap_as(-19, Error)
pub global ENOTDIR = wrap_as(-20, Error)
pub global EISDIR = wrap_as(-21, Error)
pub global EINVAL = wrap_as(-22, Error)
pub global ENFILE = wrap_as(-23, Error)
pub global EMFILE = wrap_as(-24, Error)
pub global ENOTTY = wrap_as(-25, Error)
pub global ETXTBSY = wrap_as(-26, Error)
pub global EFBIG = wrap_as(-27, Error)
pub global ENOSPC = wrap_as(-28, Error)
pub global ESPIPE = wrap_as(-29, Error)
pub global EROFS = wrap_as(-30, Error)
pub global EMLINK = wrap_as(-31, Error)
pub global EPIPE = wrap_as(-32, Error)
pub global EDOM = wrap_as(-33, Error)
pub global ERANGE = wrap_as(-34, Error)
pub global EDEADLK = wrap_as(-35, Error)
pub global ENAMETOOLONG = wrap_as(-36, Error)
pub global ENOLCK = wrap_as(-37, Error)
pub global ENOSYS = wrap_as(-38, Error)
pub global ENOTEMPTY = wrap_as(-39, Error)
pub global ELOOP = wrap_as(-40, Error)
pub global ENOMSG = wrap_as(-42, Error)
pub global EIDRM = wrap_as(-43, Error)
pub global ECHRNG = wrap_as(-44, Error)
pub global EL2NSYNC = wrap_as(-45, Error)
pub global EL3HLT = wrap_as(-46, Error)
pub global EL3RST = wrap_as(-47, Error)
pub global ELNRNG = wrap_as(-48, Error)
pub global EUNATCH = wrap_as(-49, Error)
pub global ENOCSI = wrap_as(-50, Error)
pub global EL2HLT = wrap_as(-51, Error)
pub global EBADE = wrap_as(-52, Error)
pub global EBADR = wrap_as(-53, Error)
pub global EXFULL = wrap_as(-54, Error)
pub global ENOANO = wrap_as(-55, Error)
pub global EBADRQC = wrap_as(-56, Error)
pub global EBADSLT = wrap_as(-57, Error)
pub global EBFONT = wrap_as(-59, Error)
pub global ENOSTR = wrap_as(-60, Error)
pub global ENODATA = wrap_as(-61, Error)
pub global ETIME = wrap_as(-62, Error)
pub global ENOSR = wrap_as(-63, Error)
pub global ENONET = wrap_as(-64, Error)
pub global ENOPKG = wrap_as(-65, Error)
pub global EREMOTE = wrap_as(-66, Error)
pub global ENOLINK = wrap_as(-67, Error)
pub global EADV = wrap_as(-68, Error)
pub global ESRMNT = wrap_as(-69, Error)
pub global ECOMM = wrap_as(-70, Error)
pub global EPROTO = wrap_as(-71, Error)
pub global EMULTIHOP = wrap_as(-72, Error)
pub global EDOTDOT = wrap_as(-73, Error)
pub global EBADMSG = wrap_as(-74, Error)
pub global EOVERFLOW = wrap_as(-75, Error)
pub global ENOTUNIQ = wrap_as(-76, Error)
pub global EBADFD = wrap_as(-77, Error)
pub global EREMCHG = wrap_as(-78, Error)
pub global ELIBACC = wrap_as(-79, Error)
pub global ELIBBAD = wrap_as(-80, Error)
pub global ELIBSCN = wrap_as(-81, Error)
pub global ELIBMAX = wrap_as(-82, Error)
pub global ELIBEXEC = wrap_as(-83, Error)
pub global EILSEQ = wrap_as(-84, Error)
pub global ERESTART = wrap_as(-85, Error)
pub global ESTRPIPE = wrap_as(-86, Error)
pub global EUSERS = wrap_as(-87, Error)
pub global ENOTSOCK = wrap_as(-88, Error)
pub global EDESTADDRREQ = wrap_as(-89, Error)
pub global EMSGSIZE = wrap_as(-90, Error)
pub global EPROTOTYPE = wrap_as(-91, Error)
pub global ENOPROTOOPT = wrap_as(-92, Error)
pub global EPROTONOSUPPORT = wrap_as(-93, Error)
pub global ESOCKTNOSUPPORT = wrap_as(-94, Error)
pub global EOPNOTSUPP = wrap_as(-95, Error)
pub global EPFNOSUPPORT = wrap_as(-96, Error)
pub global EAFNOSUPPORT = wrap_as(-97, Error)
pub global EADDRINUSE = wrap_as(-98, Error)
pub global EADDRNOTAVAIL = wrap_as(-99, Error)
pub global ENETDOWN = wrap_as(-100, Error)
pub global ENETUNREACH = wrap_as(-101, Error)
pub global ENETRESET = wrap_as(-102, Error)
pub global ECONNABORTED = wrap_as(-103, Error)
pub global ECONNRESET = wrap_as(-104, Error)
pub global ENOBUFS = wrap_as(-105, Error)
pub global EISCONN = wrap_as(-106, Error)
pub global ENOTCONN = wrap_as(-107, Error)
pub global ESHUTDOWN = wrap_as(-108, Error)
pub global ETOOMANYREFS = wrap_as(-109, Error)
pub global ETIMEDOUT = wrap_as(-110, Error)
pub global ECONNREFUSED = wrap_as(-111, Error)
pub global EHOSTDOWN = wrap_as(-112, Error)
pub global EHOSTUNREACH = wrap_as(-113, Error)
pub global EALREADY = wrap_as(-114, Error)
pub global EINPROGRESS = wrap_as(-115, Error)
pub global ESTALE = wrap_as(-116, Error)
pub global EUCLEAN = wrap_as(-117, Error)
pub global ENOTNAM = wrap_as(-118, Error)
pub global ENAVAIL = wrap_as(-119, Error)
pub global EISNAM = wrap_as(-120, Error)
pub global EREMOTEIO = wrap_as(-121, Error)
pub global EDQUOT = wrap_as(-122, Error)
pub global ENOMEDIUM = wrap_as(-123, Error)
pub global EMEDIUMTYPE = wrap_as(-124, Error)
pub global ECANCELED = wrap_as(-125, Error)
pub global ENOKEY = wrap_as(-126, Error)
pub global EKEYEXPIRED = wrap_as(-127, Error)
pub global EKEYREVOKED = wrap_as(-128, Error)
pub global EKEYREJECTED = wrap_as(-129, Error)
pub global EOWNERDEAD = wrap_as(-130, Error)
pub global ENOTRECOVERABLE = wrap_as(-131, Error)
pub global ERFKILL = wrap_as(-132, Error)
pub global EHWPOISON = wrap_as(-133, Error)


pub wrapped type FD = s32
pub global Stdin = wrap_as(0, FD)
pub global Stdout = wrap_as(1, FD)
pub global Stderr = wrap_as(2, FD)



pub enum IoctlOp u32:
    ; termios
    TCGETS 0x00005401
    TCSETS 0x00005402
    TCSETSW 0x00005403
    TCSETSF 0x00005404
    TCGETA 0x00005405
    TCSETA 0x00005406
    TCSETAW 0x00005407
    TCSETAF 0x00005408
    TCSBRK 0x00005409
    TCXONC 0x0000540a
    TCFLSH 0x0000540b
    TIOCEXCL 0x0000540c
    TIOCNXCL 0x0000540d
    TIOCSCTTY 0x0000540e
    TIOCGPGRP 0x0000540f
    TIOCSPGRP 0x00005410
    TIOCOUTQ 0x00005411
    TIOCSTI 0x00005412
    TIOCGWINSZ 0x00005413
    TIOCSWINSZ 0x00005414
    TIOCMGET 0x00005415
    TIOCMBIS 0x00005416
    TIOCMBIC 0x00005417
    TIOCMSET 0x00005418
    TIOCGSOFTCAR 0x00005419
    TIOCSSOFTCAR 0x0000541a
    TIOCINQ 0x0000541b
    TIOCLINUX 0x0000541c
    TIOCCONS 0x0000541d
    TIOCGSERIAL 0x0000541e
    TIOCSSERIAL 0x0000541f
    TIOCPKT 0x00005420
    FIONBIO 0x00005421
    TIOCNOTTY 0x00005422
    TIOCSETD 0x00005423
    TIOCGETD 0x00005424
    TCSBRKP 0x00005425
    TIOCTTYGSTRUCT 0x00005426
    FIONCLEX 0x00005450
    FIOCLEX 0x00005451
    FIOASYNC 0x00005452
    TIOCSERCONFIG 0x00005453
    TIOCSERGWILD 0x00005454
    TIOCSERSWILD 0x00005455
    TIOCGLCKTRMIOS 0x00005456
    TIOCSLCKTRMIOS 0x00005457
    TIOCSERGSTRUCT 0x00005458
    TIOCSERGETLSR 0x00005459
    TIOCSERGETMULTI 0x0000545a
    TIOCSERSETMULTI 0x0000545b
    ; TODO


pub enum FcntlOp u32:
    F_DUPFD         0
    F_GETFD         1
    F_SETFD         2
    F_GETFL         3
    F_SETFL         4
    F_GETLK         5
    F_SETLK         6
    F_SETLKW        7
    F_SETOWN        8
    F_GETOWN        9
    F_SETSIG        10
    F_GETSIG        11


; NOT FCNTL
pub global O_CREAT     =  0x0040_u32
pub global O_EXCL      =  0x0080_u32
pub global O_NOCTTY    =  0x0100_u32
pub global O_TRUNC     =  0x0200_u32
pub global O_APPEND    =  0x0400_u32

pub global O_ACCMODE   =  0x00003_u32
pub global O_RDONLY    =  0x00000_u32
pub global O_WRONLY    =  0x00001_u32
pub global O_RDWR      =  0x00002_u32
pub global O_NONBLOCK  =  0x00800_u32
pub global O_DSYNC     =  0x01000_u32
pub global O_DIRECT    =  0x04000_u32
pub global O_LARGEFILE =  0x08000_u32
pub global O_DIRECTORY =  0x10000_u32
pub global O_NOFOLLOW  =  0x20000_u32
pub global O_NOATIME   =  0x40000_u32
pub global O_CLOEXEC   =  0x80000_u32



{{extern}} {{cdecl}} pub fun nanosleep(req ^TimeSpec, rem ^!TimeSpec) s32:

{{extern}} {{cdecl}} pub fun write(fd s32, s ^u8, size uint) sint:

{{extern}} {{cdecl}} pub fun read(fd s32, s ^!u8, size uint) sint:

{{extern}} {{cdecl}} pub fun fcntl(fd s32, op u32, arg uint) sint:

{{extern}} {{cdecl}} pub fun ioctl(fd s32, op u32, arg uint) sint:


pub fun FileWrite(fd FD, buffer span(u8)) union(uint, Error):
    let res = write(unwrap(fd), front(buffer), len(buffer))
    if res < 0:
        return wrap_as(as(res, s32), Error)
    else:
        return as(res, uint)

pub fun FileRead(fd FD, buffer span!(u8)) union(uint, Error):
    let res = read(unwrap(fd), front!(buffer), len(buffer))
    if res < 0:
        return wrap_as(as(res, s32), Error)
    else:
        return as(res, uint)

pub fun TimeNanoSleep(req ^TimeSpec, rem ^!TimeSpec) Error:
    let res = nanosleep(req, rem)
    return wrap_as(res, Error)

pub fun FcntlInt(fd FD, op FcntlOp, arg u32) union(uint, Error):
    let res = fcntl(unwrap(fd), unwrap(op), as(arg, uint))
    if res < 0:
        return wrap_as(as(res, s32), Error)
    else:
        return as(res, uint)

pub fun Ioctl(fd FD, op IoctlOp, arg ^!void) union(uint, Error):
    let res = ioctl(unwrap(fd), unwrap(op), bitwise_as(arg, uint))
    if res < 0:
        return wrap_as(as(res, s32), Error)
    else:
        return as(res, uint)