(module main [] :
(import test)
(import fmt)

(import bitstream)

(global DataFF auto (array_val 1024 u8 [(index_val 0xff)]))

(fun @cdecl main [(param argc s32) (param argv (ptr (ptr u8)))] s32 :

    (let @ref @mut bs auto (rec_val bitstream::Stream32 [(field_val DataFF)]))
    (test::AssertEq! (bitstream::Stream32GetBits [(& @mut bs) 1]) 1_u32)
    (test::AssertEq! (bitstream::Stream32GetBits [(& @mut bs) 2]) 3_u32)
    (test::AssertEq! (bitstream::Stream32GetBits [(& @mut bs) 3]) 7_u32)

    (test::AssertEq! (bitstream::Stream32GetBits [(& @mut bs) 32]) 0xffffffff_u32)
    (test::AssertEq! (. bs bits_count) 2_u32)
    (test::AssertEq! (. bs bits_cache) 3_u32)
    (test::AssertEq! (. bs offset) 5_uint)
    (test::AssertFalse! (. bs eos))

    (test::AssertEq! (bitstream::Stream32GetBits [(& @mut bs) 31]) 0x7fffffff_u32)
    (test::AssertEq! (. bs bits_count) 3_u32)
    (test::AssertEq! (. bs bits_cache) 7_u32)
    (test::AssertEq! (. bs offset) 9_uint)
    (test::AssertFalse! (. bs eos))

    (test::AssertEq! (bitstream::Stream32GetBits [(& @mut bs) 30]) 0x3fffffff_u32)
    (test::AssertEq! (. bs bits_count) 5_u32)
    (test::AssertEq! (. bs bits_cache) 0x1f_u32)
    (test::AssertEq! (. bs offset) 13_uint)
    (test::AssertFalse! (. bs eos))

    (test::AssertEq! (bitstream::Stream32BytesLeft [(& bs)]) 1011_uint)
    @doc """(test::AssertEq! (front (bitstream::Stream32GetByteSlice [(& @mut bs) 1000_uint]))
        (incp (front DataFF) 13))"""
    (test::AssertFalse! (. bs eos))


    @doc "test end"
    (test::Success!)
    (return 0))

)