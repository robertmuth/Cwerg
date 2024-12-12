-- heapsort
module:

import random

import fmt

global SIZE uint = 20

global! Data = {[SIZE]r64:}

global NEWLINE = "\n"

global ERROR = "ERROR\n"

fun cmp_lt(a ^r64, b ^r64) bool:
    return a^ < b^

fun heap_sort(sdata span!(r64)) void:
    let data ^!r64 = front!(sdata)
    let n = len(sdata)
    let! ir = n
    let! l = n >> 1 + 1
    let! rdata r64 = undef
    while true:
        if l > 1:
            set l -= 1
            set rdata = pinc(data, l)^
        else:
            set rdata = pinc(data, ir)^
            set pinc(data, ir)^ = pinc(data, 1_uint)^
            set ir -= 1
            if ir == 1:
                set pinc(data, ir)^ = rdata
                return
        let! i = l
        let! j = l << 1
        while j <= ir:
            if j < ir && cmp_lt(pinc(data, j), pinc(data, j + 1)):
                set j += 1
            if rdata < pinc(data, j)^:
                set pinc(data, i)^ = pinc(data, j)^
                set i = j
                set j += i
            else:
                set j = ir + 1
        set pinc(data, i)^ = rdata
    return

fun dump_array(size uint, data ^r64) void:
    ref let! buf [32]u8 = undef
    for i = 0, size, 1:
        let v = pinc(data, i)^
        fmt::print#(wrap_as(v, fmt::r64_hex), NEWLINE)
    return

fun main(argc s32, argv ^^u8) s32:
    for i = 0, SIZE, 1:
        let v = random::get_random(1000)
        set Data[i + 1] = v
    do dump_array(SIZE, &Data[1])
    fmt::print#(NEWLINE)
    fmt::print#(SIZE, NEWLINE)
    do heap_sort(Data)
    fmt::print#(NEWLINE)
    do dump_array(SIZE, &Data[1])
    fmt::print#(NEWLINE)
    for i = 1, SIZE, 1:
        if Data[i] > Data[i + 1]:
            fmt::print#(ERROR)
            trap
    return 0
