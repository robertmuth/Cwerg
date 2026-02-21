; heapsort
module:

import random

import fmt

global SIZE uint = 20

ref global! Data = {[SIZE]r64:}

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
            set rdata = ptr_inc(data, l)^
        else:
            set rdata = ptr_inc(data, ir)^
            set ptr_inc(data, ir)^ = ptr_inc(data, 1_uint)^
            set ir -= 1
            if ir == 1:
                set ptr_inc(data, ir)^ = rdata
                return
        let! i = l
        let! j = l << 1
        while j <= ir:
            if j < ir && cmp_lt(ptr_inc(data, j), ptr_inc(data, j + 1)):
                set j += 1
            if rdata < ptr_inc(data, j)^:
                set ptr_inc(data, i)^ = ptr_inc(data, j)^
                set i = j
                set j += i
            else:
                set j = ir + 1
        set ptr_inc(data, i)^ = rdata
    return

fun dump_array(size uint, data ^r64) void:
    ref let! buf [32]u8 = undef
    for i = 0, size, 1:
        let v = ptr_inc(data, i)^
        fmt::print#(wrap_as(v, fmt::r64_hex), NEWLINE)
    return

global! Rng = random::SimpleLCGStateDefault


fun main(argc s32, argv ^^u8) s32:
    for i = 0, SIZE, 1:
        let v = random::NextR64(@!Rng) * 1000.0
        fmt::print#(v, NEWLINE)
        set Data[i + 1] = v
    do dump_array(SIZE, @Data[1])
    fmt::print#(NEWLINE)
    fmt::print#(SIZE, NEWLINE)
    do heap_sort(Data)
    fmt::print#(NEWLINE)
    do dump_array(SIZE, @Data[1])
    fmt::print#(NEWLINE)
    for i = 1, SIZE, 1:
        if Data[i] > Data[i + 1]:
            fmt::print#(ERROR)
            trap
    return 0
