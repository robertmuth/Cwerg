(module bytestream_test [] :
(import fmt)
(import test)
(import bytestream)

(fun test_all [] void :
    @doc "(test::AssertSliceEq! )"
    (let @mut data (array 23 u8) "\x22\x33\x44\x55\x66\x77\x88abcdefghijklmnop")
    (let @mut @ref stream (slice u8) data)
     (test::AssertEq! 0x22_u8
                      (bytestream::FrontLeU8OrDie [(& @mut stream)]))
    (test::AssertEq! 0x4433_u16
                      (bytestream::FrontLeU16OrDie [(& @mut stream)]))
    (test::AssertEq! 0x88776655_u32
                      (bytestream::FrontLeU32OrDie [(& @mut stream)]))
)

(fun @cdecl main [(param argc s32) (param argv (ptr (ptr u8)))] s32 :
    (stmt (test_all []))

    @doc "test end"
    (test::Success!)
    (return 0))

)