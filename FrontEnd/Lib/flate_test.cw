(module main [] :
(import test)
(import flate)
(import bitstream)

(fun test_inflate_errors [] void :
    (let @mut @ref out auto (array_val 1024 u8 [0]))
    @doc "sub test: "
    (let @ref data1 auto (array_val 1 u8 [ 0x42 ]))
    (let @ref @mut bs1 auto (rec_val bitstream::Stream32 [(field_val data1)]))
)

(fun @cdecl main [(param argc s32) (param argv (ptr (ptr u8)))] s32 :
    (stmt (test_inflate_errors []))
    @doc "test end"
    (test::Success!)
    (return 0))
)
