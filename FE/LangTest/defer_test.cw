; defer
module:

import test

global! gIndex uint = 0

global! gSequence = {[10]u8: 0}

fun store(c u8) void:
    set gSequence[gIndex] = c
    set gIndex += 1

fun foo() void:
    defer:
        do store('h')
    defer:
        do store('g')
    do store('a')
    block _:
        do store('b')
        defer:
            do store('e')
        defer:
            do store('d')
        do store('c')
    do store('f')

fun main(argc s32, argv ^^u8) s32:
    do foo()
    test::AssertSliceEq#(make_span(front(gSequence), gIndex), "abcdefgh")
    ; test end
    test::Success#()
    return 0
