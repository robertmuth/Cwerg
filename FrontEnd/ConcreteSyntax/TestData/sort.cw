-- heapsort
module main:

import random

import fmt

type real64 = r64

fun cmp_r64_lt(a ^real64, b ^real64) bool:
    return a^ < b^

import rhs = heapsort(real64, cmp_r64_lt)

global SIZE uint = 20

global! Data = [SIZE]r64{}

global NEWLINE = "\n"

global ERROR = "ERROR\n"

fun dump_array(size uint, data ^r64) void:
    @ref let! buf [32]u8 = undef
    for i = 0, size, 1:
        let v = pinc(data, i)^
        fmt::print#(wrapas(v, fmt::r64_hex), NEWLINE)
    return

@cdecl fun main(argc s32, argv ^^u8) s32:
    for i = 0, SIZE, 1:
        let v = random::get_random(1000)
        set Data[i + 1] = v
    shed dump_array(SIZE, &Data[1])
    fmt::print#(NEWLINE)
    fmt::print#(SIZE, NEWLINE)
    shed rhs::sort(Data)
    fmt::print#(NEWLINE)
    shed dump_array(SIZE, &Data[1])
    fmt::print#(NEWLINE)
    for i = 1, SIZE, 1:
        if Data[i] > Data[i + 1]:
            fmt::print#(ERROR)
            trap
    return 0
