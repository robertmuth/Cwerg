module:

import ansi

import os
import random
import fmt

global MAX_COLUMNS = 1000_u32
global MAX_LINES = 1000_u32


type Rng = random::Pcg32State

rec Cell:
    val s32
    is_head bool

rec CharRange:
    start u32
    end u32


rec Column:
    length u32
    ; how many spaces to skip
    spaces u32
    ; speed
    updates u32
    content [MAX_LINES]Cell


fun ColumnInit(col ^!Column, lines u32, rng ^!Rng) void:
    set col^.spaces = random::NextU32(rng) % lines + 1
    set col^.length = random::NextU32(rng) % (lines - 3) + 3
    set col^.updates = random::NextU32(rng) % 3 + 1
    for i = 0, lines + 1, 1:
        set col^.content[i].val = -1
    set col^.content[1].val = ' '


fun ColumnUpdate(col ^!Column, lines u32, chars ^CharRange, rng ^!Rng) void:
    if col^.content[0].val == -1 &&  col^.content[1].val == ' ':
        if col^.spaces > 0:
            set col^.spaces -= 1
        else:
            set col^.length = random::NextU32(rng) % (lines - 3) + 3
            set col^.spaces = random::NextU32(rng) % lines + 1

            set col^.content[0].val = as(random::NextU32(rng) %
                (chars^.end - chars^.start) + chars^.start, s32)

    let! leading_spaces = 0_u32
    for y = 0, lines + 1, 1:
        if col^.content[y].val == -1 || col^.content[y].val == ' ':
            set leading_spaces += 1



rec State:
    columns u32
    lines u32
    chars CharRange
    rng random::Pcg32State
    columns [MAX_COLUMNS]Column

global! gState State


fun main(argc s32, argv ^^u8) s32:
    ref let! win_size os::WinSize = undef
    trylet res uint = os::Ioctl(os::Stdout, os::IoctlOp:TIOCGWINSZ, bitwise_as(@!win_size, ^!void)), err:
        fmt::print#("cannot determine terminal resolution\n")
        return 1
    fmt::print#("Res ", win_size.ws_row, "x", win_size.ws_col, "\n")
    ; do StateInit(@!gState, as(win_size.ws_col, u32), as(win_size.ws_row, u32))

    fmt::print#(ansi::CURSOR_HIDE)
    fmt::print#(ansi::CURSOR_SHOW)

    return 0