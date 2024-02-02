(module main [] :
(import test)
(import flate)
(import bitstream)
(import fmt)

(defrec TestCase :
    (field description (slice u8))
    (field input (slice u8))
    (field expected_result (union [uint flate::CorruptionError flate::NoSpaceError flate::TruncationError]))
    (field expected_output (slice u8))
    (field output (slice! u8))
)

(global! large_output_buffer auto (array_val 65536 u8 [0]))

(global! one_byte_output_buffer auto (array_val 1 u8 [0]))

(global zeros auto (array_val 1024 u8 [0]))

(global! special_2_1_0 auto (array_val 32771 u8 [
      2 1 0 (index_val 2 32768) 1 0]))

@doc """
Many tests taken from https://github.com/jibsen/tinf/blob/master/test/test_tinf.c
"""
(global AllTestCases auto  (array_val 27 TestCase [
   (rec_val TestCase [
    "generic: missing next block after final uncompressed block"
    (array_val 5 u8 [ 0x00 0x00 0x00 0xff 0xff ])
    flate::TruncationErrorVal
    ""
    large_output_buffer
   ])
   (rec_val TestCase [
    "generic: invalid block 11"
    (array_val 1 u8 [ 0x07 ])
    flate::CorruptionErrorVal ""
    large_output_buffer
    ])
    (rec_val TestCase [
    "uncompressed: truncation"
    (array_val 1 u8 [ 0x01 ])
    flate::TruncationErrorVal ""
    large_output_buffer
    ])
    (rec_val TestCase [
    "uncompressed: truncation checksum"
    (array_val 4 u8 [0x01 0x00 0x00 0xff ])
    flate::TruncationErrorVal ""
    large_output_buffer
    ])
    (rec_val TestCase [
    "uncompressed: bad checksum"
    (array_val 5 u8 [  0x01 0x00 0x00 0xee 0xee  ])
    flate::CorruptionErrorVal ""
    large_output_buffer
    ])
    (rec_val TestCase [
    "uncompressed: writing past end"
    (array_val 7 u8 [  0x01 0x02 0x00 0xfd 0xff 0x00 0x00  ])
    flate::NoSpaceErrorVal ""
    one_byte_output_buffer
    ])
    (rec_val TestCase [
    "uncompressed: 0 bytes"
    (array_val 5 u8 [ 0x01 0x00 0x00 0xff 0xff  ])
    0_uint ""
    large_output_buffer
    ])
    (rec_val TestCase [
    "uncompressed: 1 bytes"
    (array_val 6 u8 [ 0x01 0x01 0x00 0xfe 0xff 0x00 ])
    1_uint "\x00"
    large_output_buffer
    ])
    @doc "fixed huffman: ERROR ======================================="
    (rec_val TestCase [
    "fixed huffman: huffman terminator corrupted"
    (array_val 2 u8 [ 0x63 0x00 ])
    flate::TruncationErrorVal ""
    large_output_buffer
    ])
    (rec_val TestCase [
    "fixed huffman: out of bounds copy"
    (array_val 4 u8 [ 0x63 0x00 0x42 0x00])
    flate::CorruptionErrorVal ""
    large_output_buffer
    ])
    (rec_val TestCase [
    "fixed huffman: out of bounds copy"
    (array_val 4 u8 [ 0x63 0x18 0x03 0x00])
    flate::CorruptionErrorVal ""
    large_output_buffer
    ])
    @doc "fixed huffman: SUCCESS ======================================="
    (rec_val TestCase [
    "fixed huffman:   empty"
    (array_val 3 u8 [ 0x03 0x00])
    0_uint ""
    large_output_buffer
    ])
    (rec_val TestCase [
    "fixed huffman:  0x00"
    @doc "last=1 fixed=01 sym8=000_01100 sym7=00_00000"
    (array_val 3 u8 [ 0x63 0x00 0x00])
    1_uint "\x00"
    large_output_buffer
    ])
    (rec_val TestCase [
    "fixed huffman:  0x11"
    (array_val 4 u8 [ 0x12 0x04 0x0c 0x00])
    1_uint "\x11"
    large_output_buffer
    ])
    (rec_val TestCase [
    "fixed huffman:  0x00 0x00"
    @doc  "last=1 fixed=01 sym8=000_01100 sym8=000_01110 sym7=00_00000"
    (array_val 4 u8 [ 0x63 0x70 0x00 0x00 ])
    2_uint "\x00\x40"
    large_output_buffer
    ])
    (rec_val TestCase [
    "fixed huffman:  0x11 0x12"
    (array_val 5 u8 [0x12 0x14 0x02 0x0c 0x00  ])
    2_uint "\x11\x12"
    large_output_buffer
    ])
    (rec_val TestCase [
    "fixed huffman:  0x00 0x00 in two blocks"
    @doc """last=0 fixed=01 sym8=000_01100 sym7=00_00000
            last=1 fixed=01 sym8=00001_110 sym7=0000_000"""
    (array_val 5 u8 [  0x62 0x00 0xcc 0x01 0x00 ])
    2_uint "\x00\x40"
    large_output_buffer
    ])
    (rec_val TestCase [
    "fixed huffman:  0x11{9}"
    (array_val 5 u8 [ 0x12 0x84 0x01 0xc0 0x00])
    2_uint "\x11\x11\x11\x11\x11\x11\x11\x11\x11"
    large_output_buffer
    ])
    (rec_val TestCase [
    "fixed huffman:  We the people ... "
    (array_val 37 u8 [
        0x0b 0x4f 0x55 0x28 0xc9 0x48 0x55 0x08
        0x48 0xcd 0x2f 0xc8 0x49 0x55 0xc8 0x4f
        0x03 0xf3 0x42 0xf3 0x32 0x4b 0x52 0x53
        0x14 0x82 0x4b 0x12 0x4b 0x52 0x8b 0x75
        0x14 0xf4 0xf4 0xf4 0x00
    ])
    39_uint "We the People of the United States, ..."
    large_output_buffer
    ])
    @doc "dynamic huffman: ======================================="
    (rec_val TestCase [
    "dynamic huffman:  256 zero bytes compressed using RLE (only one distance code)"
    (array_val 15 u8 [ 0xe5 0xc0 0x81 0x00 0x00 0x00 0x00 0x80
                       0xa0 0xfc 0xa9 0x07 0x39 0x73 0x01])
    256_uint (slice_val (front zeros) 256)
    large_output_buffer
    ])
    (rec_val TestCase [
    "dynamic huffman:  empty (no distance only literal tree)"
    (array_val 13 u8 [
        0x05 0xca 0x81 0x00  0x00 0x00 0x00 0x00
        0x90 0xff 0x6b 0x01  0x00 ])
    0_uint ""
    large_output_buffer
    ])
    (rec_val TestCase [
    "dynamic huffman:  256 zero bytes (no distance only literal tree)"
    (array_val 45 u8 [
        0x05 0xca 0x81 0x00  0x00 0x00 0x00 0x00
        0x10 0xff 0xd5 0x02  0x00 0x00 0x00 0x00
        0x00 0x00 0x00 0x00  0x00 0x00 0x00 0x00
        0x00 0x00 0x00 0x00  0x00 0x00 0x00 0x00
        0x00 0x00 0x00 0x00  0x00 0x00 0x00 0x00
        0x00 0x00 0x00 0x00  0x02 ])
    256_uint (slice_val (front zeros) 256)
    large_output_buffer
    ])
    (rec_val TestCase [
    "dynamic huffman:  259 zero bytes compressed using literal/length code 285 (len 258)"
    (array_val 15 u8 [
        0xed 0xcc 0x81 0x00  0x00 0x00 0x00 0x80
        0xa0 0xfc 0xa9 0x17  0xb9 0x00 0x2c
        ])
    259_uint (slice_val (front zeros) 259)
    large_output_buffer
    ])
    (rec_val TestCase [
    "dynamic huffman: 259 zero bytes compressed using literal/length code 284 + 31 (len 258)"
    (array_val 16 u8 [
        0xe5 0xcc 0x81 0x00  0x00 0x00 0x00 0x80
        0xa0 0xfc 0xa9 0x07  0xb9 0x00 0xfc 0x05
        ])
    259_uint (slice_val (front zeros) 259)
    large_output_buffer
    ])
    (rec_val TestCase [
    "dynamic huffman:  copy of 3 bytes with a distance of 32768 "
    (array_val 53 u8 [
		0xed 0xdd 0x01 0x01  0x00 0x00 0x08 0x02
        0x20 0xed 0xff 0xe8  0xfa 0x11 0x1c 0x61
        0x9a 0xf7 0x00 0x00  0x00 0x00 0x00 0x00
        0x00 0x00 0x00 0x00  0x00 0x00 0x00 0x00
        0x00 0x00 0x00 0x00  0x00 0x00 0x00 0x00
		0x00 0x00 0x00 0x00  0x00 0x00 0x00 0x00
        0x00 0xe0 0xfe 0xff  0x05
        ])
    32771_uint special_2_1_0
    large_output_buffer
    ])
    (rec_val TestCase [
    "dynamic huffman:  4 zero bytes - use code length codes include codes 16, 17, and 18"
    (array_val 15 u8 [
        0x0d 0xc3 0x37 0x01  0x00 0x00 0x00 0x80
        0x20 0xfa 0x77 0x1e  0xca 0x61 0x01 ])
    4_uint  (slice_val (front zeros) 4)
    large_output_buffer
    ])
    (rec_val TestCase [
    "dynamic huffman:  15 zero bytes - use all codeword lengths including 15"
    (array_val 39 u8 [
        0x05 0xea 0x01 0x82  0x24 0x49 0x92 0x24
        0x49 0x02 0x12 0x8b  0x9a 0x47 0x56 0xcf
        0xde 0xff 0x9f 0x7b  0x0f 0xd0 0xee 0x7d
        0xbf 0xbf 0x7f 0xff  0xfd 0xef 0xff 0xfe
        0xdf 0xff 0xf7 0xff  0xfb 0xff 0x03
        ])
    15_uint "\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e"
    large_output_buffer
    ])
]))

(fun test_all [] void :
    (for i 0 (len AllTestCases) 1 :
         (let tc (ptr TestCase) (& (at AllTestCases i)))
         (fmt::print# "TEST - " (-> tc description) "\n")
         (@ref let! bs auto (rec_val bitstream::Stream32 [(field_val (-> tc input))]))
         (let res  auto (flate::uncompress [ (&! bs) (-> tc output) ]))
         (test::AssertEq# (uniontypetag res) (uniontypetag (-> tc expected_result)))
         (if (is res uint) :
            (test::AssertSliceEq#
                (-> tc expected_output)
                (slice_val (front (-> tc output)) (@unchecked narrowto res uint))
            )
         :)

    )
)


@cdecl (fun main [(param argc s32) (param argv (ptr (ptr u8)))] s32 :
    (shed (test_all []))

    @doc "test end"
    (test::Success#)
    (return 0))
)
