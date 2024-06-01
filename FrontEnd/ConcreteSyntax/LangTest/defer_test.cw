-- defer
module main:

import test

global! gIndex uint = 0

global! gSequence = [10]u8{0}

fun store(c u8) void:
    set gSequence[gIndex] = c
    set gIndex += 1

fun foo() void:
    defer:
        shed store('h')
    defer:
        shed store('g')
    shed store('a')
    block _:
        shed store('b')
        defer:
            shed store('e')
        defer:
            shed store('d')
        shed store('c')
    shed store('f')

@cdecl fun main(argc s32, argv ^^u8) s32:
    shed foo()
    test::AssertSliceEq#(slice(front(gSequence), gIndex), "abcdefgh")
    -- test end
    test::Success#()
    return 0
