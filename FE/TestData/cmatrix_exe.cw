module:

import ansi

import os
import random
import fmt

global MAX_COLUMNS = 1000_u32
global MAX_LINES = 1000_u32



rec Cell:
    val s32
    is_head bool


rec State:
    columns u32
    lines u32
    rng random::Pcg32State
    lengths [MAX_COLUMNS]u32
    ; how many spaces to skip
    spaces [MAX_COLUMNS]u32
    ; update speed
    updates [MAX_COLUMNS]u32
    matrix [MAX_LINES][MAX_COLUMNS]Cell


fun StateInit(state ^!State, columns u32, lines u32) void:
    set state^.columns = columns
    set state^.lines = lines
    set state^.rng = random::Pcg32StateDefault

    for y = 0, lines + 1, 1:
        for x = 0, columns, 2:
            set state^.matrix[y][x].val = -1
    for x = 0, columns, 2:
       set state^.spaces[x] = random::Pcg32GetRandomU32(@!state^.rng) % lines + 1
       set state^.lengths[x] = random::Pcg32GetRandomU32(@!state^.rng) % (lines - 3) + 3
       set state^.updates[x] = random::Pcg32GetRandomU32(@!state^.rng) % 3 + 1
       ; sentinel
       set state^.matrix[1][x].val = ' '

global! gState State


fun main(argc s32, argv ^^u8) s32:
    ref let! win_size os::WinSize = undef
    trylet res uint = os::Ioctl(os::Stdout, os::IoctlOp:TIOCGWINSZ, bitwise_as(@!win_size, ^!void)), err:
        fmt::print#("cannot determine terminal resolution\n")
        return 1
    fmt::print#("Res ", win_size.ws_row, "x", win_size.ws_col, "\n")
    do StateInit(@!gState, as(win_size.ws_col, u32), as(win_size.ws_row, u32))

    fmt::print#(ansi::CURSOR_HIDE)
    fmt::print#(ansi::CURSOR_SHOW)

    return 0