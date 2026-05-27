module:

import ansi

import os
import random
import fmt
import termio

global KEY_NONE= 0_u16

global KEY_ESC = 27_u16
global KEY_BACKSPACE = 127_u16

global KEY_ARROW_UP = 201_u16
global KEY_ARROW_DOWN = 202_u16
global KEY_ARROW_RIGHT = 203_u16
global KEY_ARROW_LEFT = 204_u16


global KEY_HOME = 210_u16
global KEY_END = 211_u16
global KEY_DEL = 212_u16
global KEY_PAGE_UP = 213_u16
global KEY_PAGE_DOWN = 214_u16

global KEY_F1 = 221_u16
global KEY_F2 = 222_u16
global KEY_F3 = 223_u16
global KEY_F4 = 224_u16
global KEY_F5 = 225_u16
global KEY_F6 = 226_u16
global KEY_F7 = 227_u16
global KEY_F8 = 228_u16
global KEY_F9 = 229_u16
global KEY_F10 = 230_u16
global KEY_F11 = 231_u16
global KEY_F12 = 232_u16

global MOD_CONTROL = 0x100_u16
global MOD_SHIFT = 0x200_u16
global MOD_ALT = 0x400_u16



global KEY_UNDEF = 255_u16


global ESC_MAP = {[256]u16:
    KEY_UNDEF,
    '0' = KEY_UNDEF,
    '1' = KEY_UNDEF,
    '2' = KEY_UNDEF,
    '3' = KEY_DEL,
    '4' = KEY_UNDEF,
    '5' = KEY_PAGE_UP,
    '6' = KEY_PAGE_DOWN,
    '7' = KEY_UNDEF,
    '8' = KEY_UNDEF,
    '9' = KEY_UNDEF,

    'A' = KEY_ARROW_UP,
    'B' = KEY_ARROW_DOWN,
    'C' = KEY_ARROW_RIGHT,
    'D' = KEY_ARROW_LEFT,
    'E' = KEY_UNDEF,
    'F' = KEY_END,
    'G' = KEY_UNDEF,
    'H' = KEY_HOME,
    'I' = KEY_UNDEF,
    'P' = KEY_F1,
    'Q' = KEY_F2,
    'R' = KEY_F3,
    'S' = KEY_F4,
    'T' = KEY_UNDEF
}

fun DumpKey(key u16) void:
    cond:
        case key & MOD_SHIFT == MOD_SHIFT:
            fmt\print#("SHIFT+")
        case key & MOD_ALT == MOD_ALT:
            fmt\print#("ALT+")
        case key & MOD_CONTROL == MOD_CONTROL:
            fmt\print#("CTRL+")

    let k = key & 0xff
    cond:
        case k == KEY_NONE:
            fmt\print#("NONE")
        case k == KEY_UNDEF:
            fmt\print#("UNDEF")
        case k == KEY_ESC:
            fmt\print#("ESC")
        case k == KEY_BACKSPACE:
            fmt\print#("BACKSPACE")
        case k == KEY_DEL:
            fmt\print#("DEL")
        case k == KEY_HOME:
            fmt\print#("HOME")
        case k == KEY_END:
            fmt\print#("END")
        case k == KEY_PAGE_UP:
            fmt\print#("PAGE_UP")
        case k == KEY_PAGE_DOWN:
            fmt\print#("PAGE_DOWN")
        case k == KEY_ARROW_UP:
            fmt\print#("ARROW_UP")
        case k == KEY_ARROW_DOWN:
            fmt\print#("ARROW_DOWN")
        case k == KEY_ARROW_RIGHT:
            fmt\print#("ARROW_RIGHT")
        case k == KEY_ARROW_LEFT:
            fmt\print#("ARROW_LEFT")
        case k == KEY_ARROW_RIGHT:
            fmt\print#("ARROW_RIGHT")
        case k >= KEY_F1 && k <= KEY_F12:
            fmt\print#("F", k - KEY_F1 + 1)
        case true:
            fmt\print#(wrap_as(as(k, u8), fmt\rune))


fun ReadKey() union(u16, os\Error):
    ref let! c u8 = undef
    ref let! c1 u8 = undef
    ref let! c2 u8 = undef
    ref let! c3 u8 = undef

    trylet! n uint = os\FileRead(os\Stdin, make_span(@!c, 1)), err:
            return err
    if n == 0:
        return KEY_NONE
    cond:
        case c >= 1 && c <= 26:
            return as(c - 1 + 'A', u16) + MOD_CONTROL
        case c >= 'A' && c <= 'Z':
            return as(c, u16) + MOD_SHIFT
        case  c >= 'a' && c <= 'z':
            return as(c - 'a' + 'A', u16)
        case c != 27:
            return as(c, u16)

    ; possible escape sequence with two more chars
    tryset n = os\FileRead(os\Stdin, make_span(@!c1, 1)), err:
            return err
    if n == 0:
        return KEY_ESC
    if c1 == '0':
        tryset n = os\FileRead(os\Stdin, make_span(@!c2, 1)), err:
                return err
        if n == 0:
            return KEY_UNDEF
        return ESC_MAP[c2]
    if c1 == 'O':
        tryset n = os\FileRead(os\Stdin, make_span(@!c2, 1)), err:
                return err
        if n == 0:
            return KEY_UNDEF
        if c2 >= 'P' && c2 <= 'S':
            return ESC_MAP[c2]
        fmt\print#("Unexpected ]O sequence ", wrap_as(c2, fmt\u8_hex), "\n")
        return KEY_UNDEF
    if c1 >= 1 && c1 <= 26:
        return as(c1 - 1 + 'A', u16) + MOD_ALT + MOD_CONTROL
    if c1 >= 'a' && c1 <= 'z':
        return as(c1 - 'a' + 'A', u16) + MOD_ALT
    if c1 >= 'A' && c1 <= 'Z':
        return as(c1, u16) + MOD_ALT + MOD_SHIFT
    if c1 != '[':
        fmt\print#("Expected ] got ", as(c1, u32), "\n")
        return KEY_UNDEF
    tryset n = os\FileRead(os\Stdin, make_span(@!c2, 1)), err:
        return err
    if n == 0:
        return KEY_UNDEF
    if c2 >= '0' && c2 <= '9':
        tryset n = os\FileRead(os\Stdin, make_span(@!c3, 1)), err:
                return err
        if n == 0:
            return KEY_UNDEF
        cond:

            case c3 != '~':
                fmt\print#("Expected ]] ", wrap_as(c2, fmt\u8_hex)," got ", wrap_as(c3, fmt\u8_hex), "\n")
                return KEY_UNDEF
    return ESC_MAP[c2]





fun EventLoop() void:
    for i = 0, 100_u32, 1:
        trylet key u16 = ReadKey(), err:
            fmt\print#("cannot read keyboard\n")
            return
        if key == KEY_NONE:
            continue
        do DumpKey(key)
        fmt\print#("\r\n")




fun SetRawTermAttr(term_attr ^!termio\Termios) void:
    set term_attr^.iflag &= !(termio\BRKINT | termio\ICRNL | termio\INPCK |
                          termio\IXON)
    set term_attr^.oflag &= !(termio\OPOST)
    set term_attr^.cflag &= !(termio\CS8)
    set term_attr^.lflag &= !(termio\ECHO | termio\ICANON | termio\IEXTEN |
                          termio\ISIG)
    set term_attr^.cc[termio\VMIN] = 0
    set term_attr^.cc[termio\VTIME] = 1

fun main(argc s32, argv ^^u8) s32:
    ref let! win_size termio\WinSize = undef
    trylet res void = termio\GetWinSize(os\Stdout, @!win_size), err:
        fmt\print#("cannot determine terminal resolution\n")
        return 1

    ref let! term_orig termio\Termios = undef
    trylet res2 void = termio\TcGetattr(os\Stdin, @!term_orig), err:
        fmt\print#("cannot determine terminal attributes\n")
        return 1

    ref let! term_raw termio\Termios = term_orig
    do SetRawTermAttr(@!term_raw)
    trylet res3 void = termio\TcSetattrFlush(os\Stdin, @term_raw), err:
        fmt\print#("cannot reset terminal attributes\n")
        return 1

    do EventLoop()

    trylet res5 void = termio\TcSetattrFlush(os\Stdin, @term_orig), err:
        fmt\print#("cannot reset terminal attributes\n")
        return 1
    return 0