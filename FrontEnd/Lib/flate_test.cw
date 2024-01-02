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

(global AllTestCases auto  (array_val 8 TestCase [
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
    one_byte_output_buffer
    ])
    (rec_val TestCase [
    "uncompressed: 1 bytes"
    (array_val 6 u8 [ 0x01 0x01 0x00 0xfe 0xff 0x00 ])
    0_uint "\x00"
    one_byte_output_buffer
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




(fun test_inflate_fixed_huffman_failure [] void :
    (let @mut @ref out auto (array_val 1024 u8 [0]))
    (block _ :
        @doc "huffman terminator corrupted"
        (let @ref data auto (array_val 2 u8 [ 0x63 0x00 ]))
        (let @ref @mut bs auto (rec_val bitstream::Stream32 [(field_val data)]))
        (test::AssertIs! (flate::uncompress [ (& @mut bs) out ]) flate::TruncationError))
    (block _ :
        @doc "out of bounds copy"
        (let @ref data auto (array_val 4 u8 [ 0x63 0x00 0x42 0x00 ]))
        (let @ref @mut bs auto (rec_val bitstream::Stream32 [(field_val data)]))
        (test::AssertIs! (flate::uncompress [ (& @mut bs) out ]) flate::CorruptionError))
    (block _ :
        @doc "out of bounds copy"
        (let @ref data auto (array_val 4 u8 [ 0x63 0x18 0x03 0x00 ]))
        (let @ref @mut bs auto (rec_val bitstream::Stream32 [(field_val data)]))
        (test::AssertIs! (flate::uncompress [ (& @mut bs) out ]) flate::CorruptionError))
)

(fun test_inflate_fixed_huffman_success [] void :
    (block _ :
        @doc "one byte"
        (let @mut @ref out auto (array_val 1 u8 []))
        @doc "last=1 fixed=01 sym8=000_01100 sym7=00_00000"
        (let @ref data auto (array_val 3 u8 [ 0x63 0x00 0x00]))
        (let @ref @mut bs auto (rec_val bitstream::Stream32 [(field_val data)]))
        (test::AssertEq! (flate::uncompress [ (& @mut bs) out ]) 1_uint)
        (let @ref expected auto (array_val 1 u8 [ 0x00 ]))
        (test::AssertSliceEq! expected out))
    (block _ :
        @doc "two byte"
        (let @mut @ref out auto (array_val 2 u8 []))
        @doc "last=1 fixed=01 sym8=000_01100 sym8=000_01110 sym7=00_00000"
        (let @ref data auto (array_val 4 u8 [ 0x63 0x70 0x00 0x00]))
        (let @ref @mut bs auto (rec_val bitstream::Stream32 [(field_val data)]))
        (test::AssertEq! (flate::uncompress [ (& @mut bs) out ]) 2_uint)
        (let @ref expected auto (array_val 2 u8 [ 0x00 0x40]))
        (test::AssertSliceEq! expected out))
    (block _ :
        @doc "two byte in two blocks"
        (let @mut @ref out auto (array_val 2 u8 []))
        @doc """last=0 fixed=01 sym8=000_01100 sym7=00_00000
                last=1 fixed=01 sym8=00001_110 sym7=0000_000"""
        (let @ref data auto (array_val 5 u8 [ 0x62 0x00 0xcc 0x01 0x00]))
        (let @ref @mut bs auto (rec_val bitstream::Stream32 [(field_val data)]))
        (test::AssertEq! (flate::uncompress [ (& @mut bs) out ]) 2_uint)
        (let @ref expected auto (array_val 2 u8 [ 0x00 0x40]))
        (test::AssertSliceEq! expected out))
)

(fun test_inflate_dynamic_huffman_success [] void :
    (block _ :
        @doc "256 zero bytes compressed using RLE (only one distance code)"
        (let @mut @ref out auto (array_val 256 u8 []))
        (let @ref data auto (array_val 15 u8 [
        0xe5 0xc0 0x81 0x00 0x00 0x00 0x00 0x80
        0xa0 0xfc 0xa9 0x07 0x39 0x73 0x01]
        ))
        (let @ref @mut bs auto (rec_val bitstream::Stream32 [(field_val data)]))
        (test::AssertEq! (flate::uncompress [ (& @mut bs) out ]) 256_uint)
        (let @ref expected auto (array_val 256 u8 [
          0 0 0 0  0 0 0 0  0 0 0 0  0 0 0 0  0 0 0 0  0 0 0 0  0 0 0 0  0 0 0 0
          0 0 0 0  0 0 0 0  0 0 0 0  0 0 0 0  0 0 0 0  0 0 0 0  0 0 0 0  0 0 0 0
          0 0 0 0  0 0 0 0  0 0 0 0  0 0 0 0  0 0 0 0  0 0 0 0  0 0 0 0  0 0 0 0
          0 0 0 0  0 0 0 0  0 0 0 0  0 0 0 0  0 0 0 0  0 0 0 0  0 0 0 0  0 0 0 0
          0 0 0 0  0 0 0 0  0 0 0 0  0 0 0 0  0 0 0 0  0 0 0 0  0 0 0 0  0 0 0 0
          0 0 0 0  0 0 0 0  0 0 0 0  0 0 0 0  0 0 0 0  0 0 0 0  0 0 0 0  0 0 0 0
          0 0 0 0  0 0 0 0  0 0 0 0  0 0 0 0  0 0 0 0  0 0 0 0  0 0 0 0  0 0 0 0
          0 0 0 0  0 0 0 0  0 0 0 0  0 0 0 0  0 0 0 0  0 0 0 0  0 0 0 0  0 0 0 0]))
        (test::AssertSliceEq! expected out))
)

(fun @cdecl main [(param argc s32) (param argv (ptr (ptr u8)))] s32 :
    @doc "fixed huffman"
    (stmt (test_inflate_fixed_huffman_failure []))
    (stmt (test_inflate_fixed_huffman_success []))

    @doc "dynamic huffman"
    (stmt (test_inflate_dynamic_huffman_success []))

    (stmt (test_all []))

    @doc "test end"
    (test::Success!)
    (return 0))
)
