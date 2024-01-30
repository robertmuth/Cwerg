(module bytestream_test [] :
(import fmt)
(import test)
(import bytestream)

(global empty_slice (slice u8))

(fun test_bs_or_die [] void :
    (let! data (array 23 u8) "\x22\x33\x44\x55\x66\x77\x88abcdefghijklmnop")
    (let! @ref stream (slice u8) data)
    (test::AssertEq# 0x22_u8
                      (bytestream::FrontLeU8OrDie [(&! stream)]))
    (test::AssertEq# 0x4433_u16
                      (bytestream::FrontLeU16OrDie [(&! stream)]))
    (test::AssertEq# 0x88776655_u32
                      (bytestream::FrontLeU32OrDie [(&! stream)]))

    (test::AssertSliceEq#
         (bytestream::FrontSliceOrDie [(&! stream) 10])
          "abcdefghij")
    (test::AssertSliceEq#
         (bytestream::FrontSliceOrDie [(&! stream) 1])
          "k")
    (test::AssertSliceEq#
         (bytestream::FrontSliceOrDie [(&! stream) 0])
         empty_slice)
)

(fun test_bs [] void :
    (let! data (array 23 u8) "\x22\x33\x44\x55\x66\x77\x88abcdefghijklmnop")
    (let! @ref stream (slice u8) data)
    (test::AssertEq# 0x22_u8
                      (bytestream::FrontLeU8 [(&! stream)]))
    (test::AssertEq# 0x4433_u16
                      (bytestream::FrontLeU16 [(&! stream)]))
    (test::AssertEq# 0x88776655_u32
                      (bytestream::FrontLeU32 [(&! stream)]))

    (let raw1 auto  (bytestream::FrontSlice [(&! stream) 10]))
    (let dummy1 auto (typeid  (slice u8)))
    (let dummy2 auto (typeid  bytestream::OutOfBoundsError))

    (trylet result1 (slice u8) raw1 err :
        (test::AssertUnreachable#)
    )
    (test::AssertSliceEq# result1 "abcdefghij")


    (let raw2 auto  (bytestream::FrontSlice [(&! stream) 1000]))
    (trylet result2  bytestream::OutOfBoundsError raw2 err :
        (test::AssertUnreachable#)
    )

    (let raw3 auto  (bytestream::FrontSlice [(&! stream) 1]))
    (trylet result3 (slice u8) raw3 err :
        (test::AssertUnreachable#)
    )
    (test::AssertSliceEq# result3 "k")

    (let raw4 auto  (bytestream::FrontSlice [(&! stream) 1000]))
    (trylet result4  bytestream::OutOfBoundsError raw4 err :
        (test::AssertUnreachable#)
    )

    (let raw5 auto  (bytestream::FrontSlice [(&! stream) 0]))
    (trylet result5 (slice u8) raw5 err :
        (test::AssertUnreachable#)
    )
    (test::AssertSliceEq# result5 empty_slice)
)

(fun @cdecl main [(param argc s32) (param argv (ptr (ptr u8)))] s32 :
    (shed (test_bs_or_die []))
    (shed (test_bs []))

    @doc "test end"
    (test::Success#)
    (return 0))

)