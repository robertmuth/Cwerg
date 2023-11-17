(module main [] :
(import test)
(import flate)
(import bitstream)

(fun test_inflate_failure [] void :
    (let @mut @ref out auto (array_val 1024 u8 [0]))
    @doc "sub test: "
    (block _ :
        (let @ref data1 auto (array_val 1 u8 [ 0x42 ]))
        (let @ref @mut bs1 auto (rec_val bitstream::Stream32 [(field_val data1)]))
        (test::AssertIs! (flate::uncompress [ (& @mut bs1) out ]) flate::CorruptionError)
    )
)

(fun test_inflate_success [] void :
    (let @mut @ref out auto (array_val 1024 u8 [0]))
    @doc "sub test: empty"
    (block _ :
        (let @ref data1 auto (array_val 5 u8 [ 0x01 0x00 0xf8 0xff 0x07 ]))
        (let @ref @mut bs1 auto (rec_val bitstream::Stream32 [(field_val data1)]))
        (test::AssertIs! (flate::uncompress [ (& @mut bs1) out ]) uint)
    )
)

(fun @cdecl main [(param argc s32) (param argv (ptr (ptr u8)))] s32 :
    (stmt (test_inflate_failure []))
    (stmt (test_inflate_success []))
    @doc "test end"
    (test::Success!)
    (return 0))
)
