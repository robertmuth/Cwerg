module:

import fmt

import test

import bytestream

global empty_slice span(u8)

fun test_bs_or_die() void:
    let! data [23]u8 = "\x22\x33\x44\x55\x66\x77\x88abcdefghijklmnop"
    ref let! stream span(u8) = data
    test::AssertEq#(0x22_u8, bytestream::FrontU8OrDie(@!stream))
    test::AssertEq#(0x4433_u16, bytestream::FrontLeU16OrDie(@!stream))
    test::AssertEq#(0x88776655_u32, bytestream::FrontLeU32OrDie(@!stream))
    test::AssertSliceEq#(bytestream::FrontSliceOrDie(@!stream, 10), "abcdefghij")
    test::AssertSliceEq#(bytestream::FrontSliceOrDie(@!stream, 1), "k")
    test::AssertSliceEq#(bytestream::FrontSliceOrDie(@!stream, 0), empty_slice)

fun test_bs() void:
    let! data [23]u8 = "\x22\x33\x44\x55\x66\x77\x88abcdefghijklmnop"
    ref let! stream span(u8) = data
    test::AssertEq#(0x22_u8, bytestream::FrontU8(@!stream))
    test::AssertEq#(0x4433_u16, bytestream::FrontLeU16(@!stream))
    test::AssertEq#(0x88776655_u32, bytestream::FrontLeU32(@!stream))
    let raw1 = bytestream::FrontSlice(@!stream, 10)
    let dummy1 = typeid_of(span(u8))
    let dummy2 = typeid_of(bytestream::OutOfBoundsError)
    trylet result1 span(u8) = raw1, err:
        test::AssertUnreachable#()
    test::AssertSliceEq#(result1, "abcdefghij")
    let raw2 = bytestream::FrontSlice(@!stream, 1000)
    trylet result2 bytestream::OutOfBoundsError = raw2, err:
        test::AssertUnreachable#()
    let raw3 = bytestream::FrontSlice(@!stream, 1)
    trylet result3 span(u8) = raw3, err:
        test::AssertUnreachable#()
    test::AssertSliceEq#(result3, "k")
    let raw4 = bytestream::FrontSlice(@!stream, 1000)
    trylet result4 bytestream::OutOfBoundsError = raw4, err:
        test::AssertUnreachable#()
    let raw5 = bytestream::FrontSlice(@!stream, 0)
    trylet result5 span(u8) = raw5, err:
        test::AssertUnreachable#()
    test::AssertSliceEq#(result5, empty_slice)

fun main(argc s32, argv ^^u8) s32:
    do test_bs_or_die()
    do test_bs()
    -- test end
    test::Success#()
    return 0
