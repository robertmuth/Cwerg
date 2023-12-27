(module main [] :
(import test)
(import flate)
(import bitstream)

(fun test_inflate_generic_failure [] void :
    (let @mut @ref out auto (array_val 1024 u8 [0]))
    @doc "sub test: "
    (block _ :
        @doc "missing next block after final uncompressed block"
        (let @ref data auto (array_val 5 u8 [ 0x00 0x00 0x00 0xff 0xff ]))
        (let @ref @mut bs auto (rec_val bitstream::Stream32 [(field_val data)]))
        (test::AssertIs! (flate::uncompress [ (& @mut bs) out ]) flate::TruncationError))
    (block _ :
        @doc "invalid block 11"
        (let @ref data auto (array_val 1 u8 [ 0x07 ]))
        (let @ref @mut bs auto (rec_val bitstream::Stream32 [(field_val data)]))
        (test::AssertIs! (flate::uncompress [ (& @mut bs) out ]) flate::CorruptionError))
)

(fun test_inflate_uncompressed_failure [] void :
    (let @mut @ref out auto (array_val 1 u8 [0]))
    (block _ :
         @doc "truncation"
        (let @ref data auto (array_val 1 u8 [ 0x01 ]))
        (let @ref @mut bs auto (rec_val bitstream::Stream32 [(field_val data)]))
        (test::AssertIs! (flate::uncompress [ (& @mut bs) out ]) flate::TruncationError))
    (block _ :
        @doc "truncated checksum"
        (let @ref data auto (array_val 4 u8 [ 0x01 0x00 0x00 0xff ]))
        (let @ref @mut bs auto (rec_val bitstream::Stream32 [(field_val data)]))
        (test::AssertIs! (flate::uncompress [ (& @mut bs) out ]) flate::TruncationError))

    (block _ :
        @doc "bad checksum"
        (let @ref data auto (array_val 5 u8 [ 0x01 0x00 0x00 0xee 0xee ]))
        (let @ref @mut bs auto (rec_val bitstream::Stream32 [(field_val data)]))
        (test::AssertIs! (flate::uncompress [ (& @mut bs) out ]) flate::CorruptionError))
    (block _ :
        @doc "truncated data"
        (let @ref data auto (array_val 5 u8 [ 0x01 0x00 0x00 0xee 0xee ]))
        (let @ref @mut bs auto (rec_val bitstream::Stream32 [(field_val data)]))
        (test::AssertIs! (flate::uncompress [ (& @mut bs) out ]) flate::CorruptionError))
    (block _ :
        @doc "writing past end"
        (let @ref data auto (array_val 7 u8 [ 0x01 0x02 0x00 0xfd 0xff 00 00]))
        (let @ref @mut bs auto (rec_val bitstream::Stream32 [(field_val data)]))
        (test::AssertIs! (flate::uncompress [ (& @mut bs) out ]) flate::NoSpaceError))
)

(fun test_inflate_uncompressed_success [] void :
    (let @mut @ref out auto (array_val 1024 u8 [0]))
    (block _ :
        @doc "empty"
        (let @ref data auto (array_val 5 u8 [ 0x01 0x00 0x00 0xff 0xff ]))
        (let @ref @mut bs auto (rec_val bitstream::Stream32 [(field_val data)]))
        (test::AssertIs! (flate::uncompress [ (& @mut bs) out ]) uint))
    (block _ :
        @doc "one byte"
        (let @ref data auto (array_val 6 u8 [ 0x01 0x01 0x00 0xfe 0xff 00]))
        (let @ref @mut bs auto (rec_val bitstream::Stream32 [(field_val data)]))
        (test::AssertEq! (flate::uncompress [ (& @mut bs) out ]) 1_uint))
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

(fun @cdecl main [(param argc s32) (param argv (ptr (ptr u8)))] s32 :
    (stmt (test_inflate_generic_failure []))
    @doc "uncompressed"
    (stmt (test_inflate_uncompressed_failure []))
    (stmt (test_inflate_uncompressed_success []))
    @doc "fixed huffman"
    (stmt (test_inflate_fixed_huffman_failure []))
    (stmt (test_inflate_fixed_huffman_success []))

    @doc "test end"
    (test::Success!)
    (return 0))
)
