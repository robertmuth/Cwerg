module:

import ansi

import os
import random
import fmt

; every other column is blank so these limits
; scale up to screen size of a 1000x1000 chars
global MAX_COLUMNS = 500_u32
global MAX_LINES = 1000_u32

; very conservative estimate of byte count per char on the screen
global MAX_BYTES_PER_CHAR = 1000_u32



type Rng = random\Pcg32State

rec Cell:
    val s32
    is_head bool

rec CharRange:
    start u32
    end u32

; [@, Z]
global gCharsAscii = {CharRange: 33_u32, 123_u32}
; [À:ʯ]
global gCharsDiacritics = {CharRange: 0xc0_u32, 0x2b0_u32}
global gCharsHalfWidthKana = {CharRange: 0xff66_u32, 0xff9d_u32}
global gCharsMath = {CharRange: 0xff66_u32, 0xff9d_u32}

rec Column:
    length u32
    ; how many spaces to skip
    spaces u32
    ; speed
    updates u32
    content [MAX_LINES]Cell


fun ColumnInit(col ^!Column, lines u32, rng ^!Rng) void:
    set col^.spaces = random\NextU32(rng) % lines + 1
    set col^.length = random\NextU32(rng) % (lines - 3) + 3
    set col^.updates = random\NextU32(rng) % 3 + 1
    for i = 0, lines + 1, 1:
        set col^.content[i].val = -1
    set col^.content[1].val = ' '


fun ColumnUpdate(col ^!Column, lines u32, chars ^CharRange, rng ^!Rng) void:
    if col^.content[0].val == -1 &&  col^.content[1].val == ' ':
        if col^.spaces > 0:
            set col^.spaces -= 1
        else:
            set col^.length = random\NextU32(rng) % (lines - 3) + 3
            set col^.spaces = random\NextU32(rng) % lines + 1

            set col^.content[0].val = as(random\NextU32(rng) %
                (chars^.end - chars^.start) + chars^.start, s32)

    let! first_done = false
    let! i = 0_u32
    while i <= lines:
        let! begin_trace = 0_u32
        for y = i, lines + 1, 1:
            if col^.content[y].val != -1 && col^.content[y].val != ' ':
                set begin_trace = y
                break
        if begin_trace >= lines:
            break

        let! end_trace = 0_u32
        for y = begin_trace, lines + 1, 1:
            if col^.content[y].val == -1 || col^.content[y].val == ' ':
                set end_trace = y
                break
            set col^.content[y].is_head = false

        set i = end_trace
        if end_trace > lines:
            set col^.content[begin_trace].val = ' '
            break
        set col^.content[i].is_head = true
        set col^.content[i].val = as(random\NextU32(rng) %
                (chars^.end - chars^.start) + chars^.start, s32)
        if end_trace - begin_trace > col^.length || first_done:
            set col^.content[0].val = -1
            set col^.content[begin_trace].val = ' '
        set first_done = true
        set i += 1


global! gColumns[MAX_COLUMNS]Column = undef
global! gFrameBuffer [1024 * 1024]u8 = undef

fun is_border_char(x u16, y u16, w u16, h u16) bool:
    return x == 0 || x == w - 1 || y == 0 || y == h - 1


fun get_border_char(x u16, y u16, w u16, h u16, char ^[11]u32) fmt\rune_utf8:
    if x == 0:
        cond:
            case y == 0:
                return wrap_as(char^[0], fmt\rune_utf8)
            case y == h - 1:
                return wrap_as(char^[6], fmt\rune_utf8)
            case true:
                return wrap_as(char^[10], fmt\rune_utf8)
    if x ==  w - 1:
        cond:
            case y == 0:
                return wrap_as(char^[2], fmt\rune_utf8)
            case y == h - 1:
                return wrap_as(char^[8], fmt\rune_utf8)
            case true:
                return wrap_as(char^[10], fmt\rune_utf8)
    return wrap_as(char^[9], fmt\rune_utf8)


fun draw_frame(t u32, w u16, h u16) void:
    ; fmt\print#(ansi\CLEAR_ALL)
    fmt\print#(ansi\POS#(1_u16, 1_u16))

    let! buf span!(u8) = gFrameBuffer
    for y = 0, h, 1:
        for x = 0, w, 1:
            if is_border_char(x, y, w, h):
                fmt\print#(get_border_char(x, y, w, h, @ansi\BOX_COMPONENTS_DOUBLE))
                continue
            if x % 2 == 0:
                fmt\print#(wrap_as(' ', fmt\rune))
                continue
            ; fmt\print#(wrap_as('x', fmt\rune))
            ;   continue
            let c = gColumns[x / 2].content[y].val
            if c == -1:
                fmt\print#(wrap_as(' ', fmt\rune))
                continue
            fmt\print#(wrap_as(as(c, u32), fmt\rune_utf8))




fun main(argc s32, argv ^^u8) s32:
    let! num_frames = 70_u32
    if argc > 1:
        let frame_arg span(u8) = fmt\strz_to_slice(ptr_inc(argv, 1)^)
        set num_frames = fmt\str_to_u32(frame_arg)

    ref let! win_size os\WinSize = undef
    trylet res uint = os\Ioctl(os\Stdout, os\IoctlOp.TIOCGWINSZ, bitwise_as(@!win_size, ^!void)), err:
        fmt\print#("cannot determine terminal resolution\n")
        return 1
    set win_size.ws_row -= 6
    let num_cols = as((win_size.ws_col - 2) / 2, u32)
    let num_lines = as(win_size.ws_row - 2, u32)

    ref let! rng Rng = random\Pcg32StateDefault

    for i = 0, num_cols, 1:
        do ColumnInit(@!gColumns[i], num_lines, @!rng)


    ; 0.1 sec per frame
    ref let req = {os\TimeSpec: 0, 100_000_000}
    ref let! rem os\TimeSpec = undef
    fmt\print#(ansi\CURSOR_HIDE)
    for t = 0, num_frames, 1:
        for i = 0, num_cols, 1:
            do ColumnUpdate(@!gColumns[i], num_lines, @gCharsHalfWidthKana, @!rng)
        do draw_frame(t, win_size.ws_col, win_size.ws_row)
        do os\nanosleep(@req, @!rem)
    fmt\print#(ansi\CURSOR_SHOW)

    return 0