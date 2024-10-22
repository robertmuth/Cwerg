module:

import test

import flate

import bitstream

import fmt

rec TestCase:
    description span(u8)
    input span(u8)
    expected_result union(
            uint, flate::CorruptionError, flate::NoSpaceError, flate::TruncationError)
    expected_output span(u8)
    output span!(u8)

global! large_output_buffer = [65536]u8{0}

global! one_byte_output_buffer = [1]u8{0}

global zeros = [1024]u8{0}

global! special_2_1_0 = [32771]u8{2, 1, 0, 32768 : 2, 1, 0}

-- 
-- Many tests taken from https://github.com/jibsen/tinf/blob/master/test/test_tinf.c
-- 
global AllTestCases = [27]TestCase{
        TestCase{
            "generic: missing next block after final uncompressed block",
            [5]u8{0x00, 0x00, 0x00, 0xff, 0xff},
            flate::TruncationErrorVal,
            "",
            large_output_buffer},
        TestCase{
            "generic: invalid block 11",
            [1]u8{0x07},
            flate::CorruptionErrorVal,
            "",
            large_output_buffer},
        TestCase{
            "uncompressed: truncation",
            [1]u8{0x01},
            flate::TruncationErrorVal,
            "",
            large_output_buffer},
        TestCase{
            "uncompressed: truncation checksum",
            [4]u8{0x01, 0x00, 0x00, 0xff},
            flate::TruncationErrorVal,
            "",
            large_output_buffer},
        TestCase{
            "uncompressed: bad checksum",
            [5]u8{0x01, 0x00, 0x00, 0xee, 0xee},
            flate::CorruptionErrorVal,
            "",
            large_output_buffer},
        TestCase{
            "uncompressed: writing past end",
            [7]u8{0x01, 0x02, 0x00, 0xfd, 0xff, 0x00, 0x00},
            flate::NoSpaceErrorVal,
            "",
            one_byte_output_buffer},
        TestCase{
            "uncompressed: 0 bytes",
            [5]u8{0x01, 0x00, 0x00, 0xff, 0xff},
            0_uint,
            "",
            large_output_buffer},
        TestCase{
            "uncompressed: 1 bytes",
            [6]u8{0x01, 0x01, 0x00, 0xfe, 0xff, 0x00},
            1_uint,
            "\x00",
            large_output_buffer},
        -- fixed huffman: ERROR =======================================
        TestCase{
            "fixed huffman: huffman terminator corrupted",
            [2]u8{0x63, 0x00},
            flate::TruncationErrorVal,
            "",
            large_output_buffer},
        TestCase{
            "fixed huffman: out of bounds copy",
            [4]u8{0x63, 0x00, 0x42, 0x00},
            flate::CorruptionErrorVal,
            "",
            large_output_buffer},
        TestCase{
            "fixed huffman: out of bounds copy",
            [4]u8{0x63, 0x18, 0x03, 0x00},
            flate::CorruptionErrorVal,
            "",
            large_output_buffer},
        -- fixed huffman: SUCCESS =======================================
        TestCase{
            "fixed huffman:   empty", [3]u8{0x03, 0x00}, 0_uint, "", large_output_buffer},
        TestCase{
            "fixed huffman:  0x00",
            -- last=1 fixed=01 sym8=000_01100 sym7=00_00000
            [3]u8{0x63, 0x00, 0x00},
            1_uint,
            "\x00",
            large_output_buffer},
        TestCase{
            "fixed huffman:  0x11",
            [4]u8{0x12, 0x04, 0x0c, 0x00},
            1_uint,
            "\x11",
            large_output_buffer},
        TestCase{
            "fixed huffman:  0x00 0x00",
            -- last=1 fixed=01 sym8=000_01100 sym8=000_01110 sym7=00_00000
            [4]u8{0x63, 0x70, 0x00, 0x00},
            2_uint,
            "\x00\x40",
            large_output_buffer},
        TestCase{
            "fixed huffman:  0x11 0x12",
            [5]u8{0x12, 0x14, 0x02, 0x0c, 0x00},
            2_uint,
            "\x11\x12",
            large_output_buffer},
        TestCase{
            "fixed huffman:  0x00 0x00 in two blocks",
            -- last=0 fixed=01 sym8=000_01100 sym7=00_00000
            --             last=1 fixed=01 sym8=00001_110 sym7=0000_000
            [5]u8{0x62, 0x00, 0xcc, 0x01, 0x00},
            2_uint,
            "\x00\x40",
            large_output_buffer},
        TestCase{
            "fixed huffman:  0x11{9}",
            [5]u8{0x12, 0x84, 0x01, 0xc0, 0x00},
            2_uint,
            "\x11\x11\x11\x11\x11\x11\x11\x11\x11",
            large_output_buffer},
        TestCase{
            "fixed huffman:  We the people ... ",
            [37]u8{
                0x0b, 0x4f, 0x55, 0x28, 0xc9, 0x48, 0x55, 0x08, 0x48, 0xcd, 0x2f, 
                0xc8, 0x49, 0x55, 0xc8, 0x4f, 0x03, 0xf3, 0x42, 0xf3, 0x32, 0x4b, 
                0x52, 0x53, 0x14, 0x82, 0x4b, 0x12, 0x4b, 0x52, 0x8b, 0x75, 0x14, 
                0xf4, 0xf4, 0xf4, 0x00},
            39_uint,
            "We the People of the United States, ...",
            large_output_buffer},
        -- dynamic huffman: =======================================
        TestCase{
            "dynamic huffman:  256 zero bytes compressed using RLE (only one distance code)",
            [15]u8{
                0xe5, 0xc0, 0x81, 0x00, 0x00, 0x00, 0x00, 0x80, 0xa0, 0xfc, 0xa9, 
                0x07, 0x39, 0x73, 0x01},
            256_uint,
            span(front(zeros), 256),
            large_output_buffer},
        TestCase{
            "dynamic huffman:  empty (no distance only literal tree)",
            [13]u8{
                0x05, 0xca, 0x81, 0x00, 0x00, 0x00, 0x00, 0x00, 0x90, 0xff, 0x6b, 
                0x01, 0x00},
            0_uint,
            "",
            large_output_buffer},
        TestCase{
            "dynamic huffman:  256 zero bytes (no distance only literal tree)",
            [45]u8{
                0x05, 0xca, 0x81, 0x00, 0x00, 0x00, 0x00, 0x00, 0x10, 0xff, 0xd5, 
                0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 
                0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 
                0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 
                0x02},
            256_uint,
            span(front(zeros), 256),
            large_output_buffer},
        TestCase{
            "dynamic huffman:  259 zero bytes compressed using literal/length code 285 (len 258)",
            [15]u8{
                0xed, 0xcc, 0x81, 0x00, 0x00, 0x00, 0x00, 0x80, 0xa0, 0xfc, 0xa9, 
                0x17, 0xb9, 0x00, 0x2c},
            259_uint,
            span(front(zeros), 259),
            large_output_buffer},
        TestCase{
            "dynamic huffman: 259 zero bytes compressed using literal/length code 284 + 31 (len 258)",
            [16]u8{
                0xe5, 0xcc, 0x81, 0x00, 0x00, 0x00, 0x00, 0x80, 0xa0, 0xfc, 0xa9, 
                0x07, 0xb9, 0x00, 0xfc, 0x05},
            259_uint,
            span(front(zeros), 259),
            large_output_buffer},
        TestCase{
            "dynamic huffman:  copy of 3 bytes with a distance of 32768 ",
            [53]u8{
                0xed, 0xdd, 0x01, 0x01, 0x00, 0x00, 0x08, 0x02, 0x20, 0xed, 0xff, 
                0xe8, 0xfa, 0x11, 0x1c, 0x61, 0x9a, 0xf7, 0x00, 0x00, 0x00, 0x00, 
                0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 
                0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 
                0x00, 0x00, 0x00, 0x00, 0x00, 0xe0, 0xfe, 0xff, 0x05},
            32771_uint,
            special_2_1_0,
            large_output_buffer},
        TestCase{
            "dynamic huffman:  4 zero bytes - use code length codes include codes 16, 17, and 18",
            [15]u8{
                0x0d, 0xc3, 0x37, 0x01, 0x00, 0x00, 0x00, 0x80, 0x20, 0xfa, 0x77, 
                0x1e, 0xca, 0x61, 0x01},
            4_uint,
            span(front(zeros), 4),
            large_output_buffer},
        TestCase{
            "dynamic huffman:  15 zero bytes - use all codeword lengths including 15",
            [39]u8{
                0x05, 0xea, 0x01, 0x82, 0x24, 0x49, 0x92, 0x24, 0x49, 0x02, 0x12, 
                0x8b, 0x9a, 0x47, 0x56, 0xcf, 0xde, 0xff, 0x9f, 0x7b, 0x0f, 0xd0, 
                0xee, 0x7d, 0xbf, 0xbf, 0x7f, 0xff, 0xfd, 0xef, 0xff, 0xfe, 0xdf, 
                0xff, 0xf7, 0xff, 0xfb, 0xff, 0x03},
            15_uint,
            "\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e",
            large_output_buffer}}

fun test_all() void:
    for i = 0, len(AllTestCases), 1:
        let tc ^TestCase = &AllTestCases[i]
        fmt::print#("TEST - ", tc^.description, "\n")
        ref let! bs = bitstream::Stream32{tc^.input}
        let res = flate::uncompress(&!bs, tc^.output)
        test::AssertEq#(union_tag(res), union_tag(tc^.expected_result))
        if is(res, uint):
            test::AssertSliceEq#(
                    tc^.expected_output, span(
                        front(tc^.output), @unchecked narrow_as(res, uint)))

fun main(argc s32, argv ^^u8) s32:
    do test_all()
    -- test end
    test::Success#()
    return 0
