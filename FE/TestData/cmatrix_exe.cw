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
global MAX_BYTES_PER_CHAR = 1000_uint


;
global SPEED_RANGE = 2_u32

type Rng = random\Pcg32State

enum CellKind u8:
    Normal 0
    Tip 1
    Tail 2

rec Cell:
    val u32
    kind CellKind


rec CharRange:
    start u32
    end u32

; [@, Z]
global gCharsAscii = {CharRange: 33_u32, 123_u32}
; [À:ʯ]
global gCharsDiacritics = {CharRange: 0xc0_u32, 0x2b0_u32}
global gCharsHalfWidthKana = {CharRange: 0xff66_u32, 0xff9d_u32}
global gCharsMath = {CharRange: 0xff66_u32, 0xff9d_u32}

enum Mode u8:
    Spaces 0
    Birthing 1

rec Column:
    counter u32
    speed u32
    mode Mode
    content [MAX_LINES]Cell


; needs to be at least 2 so we can distinguish tip and tail
fun RandomLength(lines u32, rng ^!Rng) u32:
    return random\NextU32(rng) % lines + 2


fun RandomSpaces(lines u32, rng ^!Rng) u32:
    return random\NextU32(rng) % (lines - 3) + 3

fun RandomChar(chars ^CharRange, rng ^!Rng) u32:
    return as(random\NextU32(rng) %
                (chars^.end - chars^.start) + chars^.start, u32)

fun ColumnInit(col ^!Column, lines u32, rng ^!Rng) void:
    set col^.speed = random\NextU32(rng) % SPEED_RANGE
    ; start with spaces
    set col^.counter = RandomSpaces(lines, rng)
    set col^.mode = Mode.Spaces
    for i = 0, lines, 1:
        set col^.content[i].val = ' '
        set col^.content[i].kind = CellKind.Normal



fun ColumnUpdate(col ^!Column, lines u32, chars ^CharRange, rng ^!Rng, frame u32) void:
    if frame % (SPEED_RANGE + 1) <= col^.speed:
        return

    for  i = 0, lines, 1:
        ; really going bottom to top
        let index = lines - 1 - i
        cond:
            case col^.content[index].kind == CellKind.Tip:
                set col^.content[index].kind = CellKind.Normal
                ; we may write out of bounds but that is ok since the actual length is MAX_LINES
                set col^.content[index + 1].kind = CellKind.Tip
                set col^.content[index + 1].val = RandomChar(chars, rng)
            case col^.content[index].kind == CellKind.Tail:
                set col^.content[index].kind = CellKind.Normal
                set col^.content[index].val = ' '
                set col^.content[index + 1].kind = CellKind.Tail

    set col^.counter -= 1
    if col^.counter == 0:
        if col^.mode == Mode.Spaces:
                set col^.mode = Mode.Birthing
                set col^.counter = RandomLength(lines, rng)
                set col^.content[0].kind = CellKind.Tip
                set col^.content[0].val = RandomChar(chars, rng)
        else:
                set col^.mode = Mode.Spaces
                set col^.counter = RandomSpaces(lines, rng)
                set col^.content[0].kind = CellKind.Tail


global! gColumns[MAX_COLUMNS]Column = undef
global! gFrameBuffer [1024 * 1024]u8 = undef

fun is_border_char(x u16, y u16, w u16, h u16) bool:
    return x == 0 || x == w - 1 || y == 0 || y == h - 1


fun get_border_char(x u16, y u16, w u16, h u16, chars ^[11]u32) u32:
    if x == 0:
        cond:
            case y == 0:
                return chars^[0]
            case y == h - 1:
                return chars^[6]
            case true:
                return chars^[10]
    if x ==  w - 1:
        cond:
            case y == 0:
                return chars^[2]
            case y == h - 1:
                return chars^[8]
            case true:
                return chars^[10]
    return chars^[9]



fun print(s span(u8)) void:
    do os\write(unwrap(os\Stdout), front(s), len(s))


fun span_fill(buf span!(u8), s span(u8)) uint:
    let out = min(len(buf), len(s))
    for i = 0, out, 1:
        set buf[i] = s[i]
    return out



fun draw_frame(t u32, w u16, h u16) void:

    fmt\print#(ansi\POS#(1_u16, 1_u16))

    let! buf span!(u8) = gFrameBuffer
    for y = 0, h, 1:
        for x = 0, w, 1:
            if len(buf) < MAX_BYTES_PER_CHAR:
                ; flush buf
                do print(make_span(front(gFrameBuffer), len(gFrameBuffer) - len(buf)))
                set buf = gFrameBuffer
                continue
            if is_border_char(x, y, w, h):
                set buf = span_inc(buf, span_fill(buf, ansi\SGR_START))
                set buf = span_inc(buf, span_fill(buf, ansi\SGR_FG_GREEN))
                set buf = span_inc(buf, span_fill(buf, ";"))
                set buf = span_inc(buf, span_fill(buf, ansi\SGR_RESET_BOLD_AND_DIM))
                set buf = span_inc(buf, span_fill(buf, ansi\SGR_END))
                set buf = span_inc(buf, fmt\UnicodeToUtf8(get_border_char(x, y, w, h, @ansi\BOX_COMPONENTS_DOUBLE), buf))

                continue
            ; every other column is blank
            if x % 2 == 0:
                set buf = span_inc(buf, fmt\UnicodeToUtf8(32, buf))
                continue
            let c = gColumns[x / 2].content[y - 1].val
            if c == -1:
                set buf = span_inc(buf, fmt\UnicodeToUtf8(32, buf))
                continue
            set buf = span_inc(buf, span_fill(buf, ansi\SGR_START))
            if gColumns[x / 2].content[y - 1].kind == CellKind.Tip:
                set buf = span_inc(buf, span_fill(buf, ansi\SGR_FG_WHITE))
                set buf = span_inc(buf, span_fill(buf, ";"))
                set buf = span_inc(buf, span_fill(buf, ansi\SGR_BOLD))
            else:
                set buf = span_inc(buf, span_fill(buf, ansi\SGR_FG_GREEN))
                set buf = span_inc(buf, span_fill(buf, ";"))
                set buf = span_inc(buf, span_fill(buf, ansi\SGR_RESET_BOLD_AND_DIM))
            set buf = span_inc(buf, span_fill(buf, ansi\SGR_END))

            ;
            set buf = span_inc(buf, fmt\UnicodeToUtf8(as(c, u32), buf))

    ; flush buf
    do print(make_span(front(gFrameBuffer), len(gFrameBuffer) - len(buf)))




fun main(argc s32, argv ^^u8) s32:
    let! num_frames = 70_u32
    if argc > 1:
        let frame_arg span(u8) = fmt\strz_to_slice(ptr_inc(argv, 1)^)
        set num_frames = fmt\str_to_u32(frame_arg)

    ref let! win_size os\WinSize = undef
    trylet res uint = os\Ioctl(os\Stdout, os\IoctlOp.TIOCGWINSZ, bitwise_as(@!win_size, ^!void)), err:
        fmt\print#("cannot determine terminal resolution\n")
        return 1
    let num_cols = as((win_size.ws_col - 2) / 2, u32)
    let num_lines = as(win_size.ws_row - 2, u32)

    ref let! rng Rng = random\Pcg32StateDefault

    for i = 0, num_cols, 1:
        do ColumnInit(@!gColumns[i], num_lines, @!rng)


    ; 0.05 sec per frame
    ref let req = {os\TimeSpec: 0, 50_000_000}
    ref let! rem os\TimeSpec = undef
    fmt\print#(ansi\CURSOR_HIDE)
    fmt\print#(ansi\CLEAR_ALL)

    for t = 0, num_frames, 1:
        for i = 0, num_cols, 1:
            do ColumnUpdate(@!gColumns[i], num_lines, @gCharsHalfWidthKana, @!rng, t)
        do draw_frame(t, win_size.ws_col, win_size.ws_row)
        do os\nanosleep(@req, @!rem)
    fmt\print#(ansi\CURSOR_SHOW)

    return 0