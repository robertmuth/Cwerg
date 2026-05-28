module:

import ansi

import os
import random
import fmt
import termio

global KEY_NONE= 0_u16
global KEY_UNDEF = 255_u16

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
global KEY_ENTER = 215_u16
global KEY_TAB = 216_u16

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


fun DumpKey(key u16) void:
    if key & MOD_SHIFT == MOD_SHIFT:
        fmt\print#("SHIFT+")
    if key & MOD_ALT == MOD_ALT:
        fmt\print#("ALT+")
    if key & MOD_CONTROL == MOD_CONTROL:
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
        case k == KEY_ENTER:
            fmt\print#("ENTER")
        case k == KEY_TAB:
            fmt\print#("TAB")
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


fun ReadKeyHandleSimple(c u8) u16:
    cond:
        case c >= 1 && c <= 26:
            if c == 13:
                return KEY_ENTER
            if c == 9:
                return KEY_TAB
            return as(c - 1 + 'A', u16) + MOD_CONTROL
        case c >= 'A' && c <= 'Z':
            return as(c, u16) + MOD_SHIFT
        case  c >= 'a' && c <= 'z':
            return as(c - 'a' + 'A', u16)
        case true:
            return as(c, u16)


fun ReadKeyHandleEscSimple(c u8) union(u16, os\Error):
    cond:
        case c == 'O':
            ref let! c2 u8 = undef
            trylet n uint = os\FileRead(os\Stdin, make_span(@!c2, 1)), err:
                return err
            if n == 0:
                return KEY_UNDEF
            if c2 >= 'P' && c2 <= 'S':
                return KEY_F1 + as(c2 - 'P', u16)
            return KEY_UNDEF
        case c >= 1 && c <= 26:
            return as(c - 1 + 'A', u16) + MOD_ALT + MOD_CONTROL
        case c >= 'a' && c <= 'z':
            return as(c - 'a' + 'A', u16) + MOD_ALT
        case c >= 'A' && c <= 'Z':
            return as(c, u16) + MOD_ALT + MOD_SHIFT
        case c == ' ':
            return MOD_ALT + ' '
    return KEY_UNDEF


global ESC_XTERM_MAP = {[256]u16:
    KEY_UNDEF,
    3 = KEY_DEL,
    5 = KEY_PAGE_UP,
    6 = KEY_PAGE_DOWN,
    15 = KEY_F5,
    17 = KEY_F6,
    18 = KEY_F7,
    19 = KEY_F8,
    20 = KEY_F9,
    21 = KEY_F10,
    23 = KEY_F11,
    24 = KEY_F12,
    '0' = KEY_UNDEF,
    'A' = KEY_ARROW_UP,
    'B' = KEY_ARROW_DOWN,
    'C' = KEY_ARROW_RIGHT,
    'D' = KEY_ARROW_LEFT,
    'E' = KEY_UNDEF,
    'F' = KEY_END,
    'G' = KEY_UNDEF,
    'H' = KEY_HOME,
    'I' = KEY_UNDEF,
    'Z' = KEY_TAB + MOD_SHIFT,
    '[' = KEY_UNDEF
}


global MODIFIER_MAP = {[8]u16:
    0,
    MOD_SHIFT,
    0,
    MOD_ALT,
    MOD_ALT + MOD_SHIFT,
    MOD_CONTROL,
    MOD_CONTROL + MOD_SHIFT,
    MOD_ALT + MOD_CONTROL
}


 fun ReadKeyHandleEscSquareOpenSimple(c u8) union(u16, os\Error):
    ref let! t u8 = c
    let! key u16 = 0
    let! modifier u16 = 0
    if t < '0' || t > '9':
        set key = 1
    else:
        while t >= '0' && t <= '9':
            set key *= 10
            set key += as(t - '0', u16)
            trylet n uint = os\FileRead(os\Stdin, make_span(@!t, 1)), err:
                return err
            if n == 0:
                return KEY_NONE
    if t == ';':
        trylet! n uint = os\FileRead(os\Stdin, make_span(@!t, 1)), err:
            return err
        if n == 0:
            return KEY_NONE
        set modifier = MODIFIER_MAP[t - '0']

        tryset n = os\FileRead(os\Stdin, make_span(@!t, 1)), err:
            return err
        if n == 0:
            return KEY_NONE
    if t == '~':
        return ESC_XTERM_MAP[key] + modifier
    if key != 1:
        return KEY_UNDEF
    return ESC_XTERM_MAP[t] + modifier



fun ReadKey() union(u16, os\Error):
    ref let! c u8 = undef

    trylet! n uint = os\FileRead(os\Stdin, make_span(@!c, 1)), err:
            return err
    if n == 0:
        return KEY_NONE

    if c != 27:
        return ReadKeyHandleSimple(c)

    ; sequence so far EXC "["
    tryset n = os\FileRead(os\Stdin, make_span(@!c, 1)), err:
        return err
    if n == 0:
        return KEY_ESC


    if c != '[':
        return ReadKeyHandleEscSimple(c)

    tryset n = os\FileRead(os\Stdin, make_span(@!c, 1)), err:
        return err
    if n == 0:
        return KEY_UNDEF

    return ReadKeyHandleEscSquareOpenSimple(c)


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