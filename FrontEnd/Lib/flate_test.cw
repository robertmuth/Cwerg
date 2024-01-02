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
    (field output (slice @mut u8))
)

(global @mut large_output_buffer auto (array_val 1024 u8 [0]))

(global @mut one_byte_output_buffer auto (array_val 1 u8 [0]))

(global zero_times_256 auto (array_val 256 u8 [
          0 0 0 0  0 0 0 0  0 0 0 0  0 0 0 0  0 0 0 0  0 0 0 0  0 0 0 0  0 0 0 0
          0 0 0 0  0 0 0 0  0 0 0 0  0 0 0 0  0 0 0 0  0 0 0 0  0 0 0 0  0 0 0 0
          0 0 0 0  0 0 0 0  0 0 0 0  0 0 0 0  0 0 0 0  0 0 0 0  0 0 0 0  0 0 0 0
          0 0 0 0  0 0 0 0  0 0 0 0  0 0 0 0  0 0 0 0  0 0 0 0  0 0 0 0  0 0 0 0
          0 0 0 0  0 0 0 0  0 0 0 0  0 0 0 0  0 0 0 0  0 0 0 0  0 0 0 0  0 0 0 0
          0 0 0 0  0 0 0 0  0 0 0 0  0 0 0 0  0 0 0 0  0 0 0 0  0 0 0 0  0 0 0 0
          0 0 0 0  0 0 0 0  0 0 0 0  0 0 0 0  0 0 0 0  0 0 0 0  0 0 0 0  0 0 0 0
          0 0 0 0  0 0 0 0  0 0 0 0  0 0 0 0  0 0 0 0  0 0 0 0  0 0 0 0  0 0 0 0]))

(global AllTestCases auto  (array_val 17 TestCase [
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
    (rec_val TestCase [
    "fixed huffman:  one byte"
    @doc "last=1 fixed=01 sym8=000_01100 sym7=00_00000"
    (array_val 3 u8 [ 0x63 0x00 0x00])
    1_uint "\x00"
    large_output_buffer
    ])
    (rec_val TestCase [
    "fixed huffman:  two bytes"
    @doc  "last=1 fixed=01 sym8=000_01100 sym8=000_01110 sym7=00_00000"
    (array_val 4 u8 [ 0x63 0x70 0x00 0x00 ])
    2_uint "\x00\x40"
    large_output_buffer
    ])
    (rec_val TestCase [
    "fixed huffman:  two bytes in two blocks"
    @doc """last=0 fixed=01 sym8=000_01100 sym7=00_00000
            last=1 fixed=01 sym8=00001_110 sym7=0000_000"""
    (array_val 5 u8 [  0x62 0x00 0xcc 0x01 0x00 ])
    2_uint "\x00\x40"
    large_output_buffer
    ])
    (rec_val TestCase [
    "dynamic huffman:  256 zero bytes compressed using RLE (only one distance code)"
    (array_val 15 u8 [ 0xe5 0xc0 0x81 0x00 0x00 0x00 0x00 0x80
                       0xa0 0xfc 0xa9 0x07 0x39 0x73 0x01])
    256_uint zero_times_256
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
    256_uint zero_times_256
    large_output_buffer
    ])

]))

(fun test_all [] void :
    (for i 0 (len AllTestCases) 1 :
         (let tc (ptr TestCase) (& (at AllTestCases i)))
         (fmt::print! ["TEST - " (-> tc description) "\n"])
         (let @ref @mut bs auto (rec_val bitstream::Stream32 [(field_val (-> tc input))]))
         (let res  auto (flate::uncompress [ (& @mut bs) (-> tc output) ]))
         (test::AssertEq! (uniontypetag res) (uniontypetag (-> tc expected_result)))
         (if (is res uint) :
            (test::AssertSliceEq!
                (-> tc expected_output)
                (slice_val (front (-> tc output)) (narrowto @unchecked res uint))
            )
         :)

    )
)


(fun @cdecl main [(param argc s32) (param argv (ptr (ptr u8)))] s32 :
    (stmt (test_all []))

    @doc "test end"
    (test::Success!)
    (return 0))
)
