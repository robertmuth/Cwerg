module:

import os

pub rec WinSize:
    ws_row u16
    ws_col u16
    ws_xpixel u16
    ws_ypixel u16



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


; input modes
pub global IUCLC u32 = 0x0200
pub global IXON u32 = 0x0400
pub global IXOFF u32 = 0x1000
pub global IMAXBEL u32 = 0x2000
pub global IUTF8 u32 = 0x4000


; output modes
 pub global OLCUC u32 = 0x00002
 pub global ONLCR u32 = 0x00004
 pub global NLDLY u32 = 0x00100
 pub global NL0 u32 = 0x00000
 pub global NL1 u32 = 0x00100
 pub global CRDLY u32 = 0x00600
 pub global CR0 u32 = 0x00000
 pub global CR1 u32 = 0x00200
 pub global CR2 u32 = 0x00400
 pub global CR3 u32 = 0x00600
 pub global TABDLY u32 = 0x01800
 pub global TAB0 u32 = 0x00000
 pub global TAB1 u32 = 0x00800
 pub global TAB2 u32 = 0x01000
 pub global TAB3 u32 = 0x01800
 pub global XTABS u32 = 0x01800
 pub global BSDLY u32 = 0x02000
 pub global BS0 u32 = 0x00000
 pub global BS1 u32 = 0x02000
 pub global VTDLY u32 = 0x04000
 pub global VT0 u32 = 0x00000
 pub global VT1 u32 = 0x04000
 pub global FFDLY u32 = 0x08000
 pub global FF0 u32 = 0x00000
 pub global FF1 u32 = 0x08000


; control modes
 pub global CBAUD u32 = 0x0000100f
 pub global CSIZE u32 = 0x00000030
 pub global CS5 u32 = 0x00000000
 pub global CS6 u32 = 0x00000010
 pub global CS7 u32 = 0x00000020
 pub global CS8 u32 = 0x00000030
 pub global CSTOPB u32 = 0x00000040
 pub global CREAD u32 = 0x00000080
 pub global PARENB u32 = 0x00000100
 pub global PARODD u32 = 0x00000200
 pub global HUPCL u32 = 0x00000400
 pub global CLOCAL u32 = 0x00000800
 pub global CBAUDEX u32 = 0x00001000
 pub global BOTHER u32 = 0x00001000
 pub global B57600 u32 = 0x00001001
 pub global B115200 u32 = 0x00001002
 pub global B230400 u32 = 0x00001003
 pub global B460800 u32 = 0x00001004
 pub global B500000 u32 = 0x00001005
 pub global B576000 u32 = 0x00001006
 pub global B921600 u32 = 0x00001007
 pub global B1000000 u32 = 0x00001008
 pub global B1152000 u32 = 0x00001009
 pub global B1500000 u32 = 0x0000100a
 pub global B2000000 u32 = 0x0000100b
 pub global B2500000 u32 = 0x0000100c
 pub global B3000000 u32 = 0x0000100d
 pub global B3500000 u32 = 0x0000100e
 pub global B4000000 u32 = 0x0000100f
 pub global CIBAUD u32 = 0x100f0000


; local modes
 pub global ISIG u32 = 0x00001
 pub global ICANON u32 = 0x00002
 pub global XCASE u32 = 0x00004
 pub global ECHO u32 = 0x00008
 pub global ECHOE u32 = 0x00010
 pub global ECHOK u32 = 0x00020
 pub global ECHONL u32 = 0x00040
 pub global NOFLSH u32 = 0x00080
 pub global TOSTOP u32 = 0x00100
 pub global ECHOCTL u32 = 0x00200
 pub global ECHOPRT u32 = 0x00400
 pub global ECHOKE u32 = 0x00800
 pub global FLUSHO u32 = 0x01000
 pub global PENDIN u32 = 0x04000
 pub global IEXTEN u32 = 0x08000
 pub global EXTPROC u32 = 0x10000



; named indices for cc vector in Termios
pub global VINTR u32 = 0
pub global VQUIT u32 = 1
pub global VERASE u32 = 2
pub global VKILL u32 = 3
pub global VEOF u32 = 4
pub global VTIME u32 = 5
pub global VMIN u32 = 6
pub global VSWTC u32 = 7
pub global VSTART u32 = 8
pub global VSTOP u32 = 9
pub global VSUSP u32 = 10
pub global VEOL u32 = 11
pub global VREPRINT u32 = 12
pub global VDISCARD u32 = 13
pub global VWERASE u32 = 14
pub global VLNEXT u32 = 15
pub global VEOL2 u32 = 16


pub rec Termios:
    iflag u32
    oflag u32
    cflag u32
    lflag u32
    line u8
    cc [19]u8


pub fun GetWinSize(fd os\FD, arg ^!WinSize) union(void, os\Error):
    let res = os\ioctl(unwrap(fd), unwrap(IoctlOp.TIOCGWINSZ), bitwise_as(arg, uint))
    if res < 0:
        return wrap_as(as(res, s32), os\Error)
    else:
        return void_val
