(module [] :
(import test)


@pub (defrec type_rec1 :
    @doc """this is a comment with \" with quotes \t """
    (field s1 s32)
    @doc "s2 comment "
    (field s2 s32)
    @doc "s3 is ..."
    (field s3 s32)
    (field s4 bool)
    (field s5 u64)
    (field s6 u64))


@pub (defrec type_rec2 :
    (field t1 bool)
    (field t2 u32)
    (field t3 type_rec1)
    (field t4 bool))


@pub (defrec type_rec3 :
    (field u2 u16)
    (field u3 u64)
    (field u4 type_rec2)
    (field u5 (array 13 u16))
    (field u6 u64))


@pub (defrec type_rec4 :
    (field t1 u64)
    (field t2 u8)
    (field t3 u16)
    (field t4 u32)
    (field t5 bool))


(global u0 u32 0x12345678)


@doc "g0 is i mportant"
(global g0 type_rec1 undef)


(global g1 (array 5 type_rec1) undef)


(global g2 auto (rec_val type_rec2 [true u0]))


(global! g3 auto (rec_val type_rec3 [
        0x1234
        0x4321
        g2
        (vec_val 13 u16 [0x11 undef 0x12])]))


(global! g3_alt auto (rec_val type_rec3 [
        0x1234
        0x4321
        g2
        (vec_val 13 u16 [0x11 undef 0x12])]))


@doc "BROKEN init"
(global g4 auto (vec_val 4 type_rec2 [undef g2]))


@pub (defrec type_rec5 :
    (field t1 u64)
    (field t2 (slice! u8))
    (field t5 bool))


(global! buffer auto (vec_val 3 u8 [0 0 0]))


(global g5 type_rec5 undef)


(global g6 type_rec5 (rec_val type_rec5 [0 buffer false]))


(global g7 auto (vec_val 1 type_rec5 [(rec_val type_rec5 [0 buffer false])]))


(fun main [(param argc s32) (param argv (ptr (ptr u8)))] s32 :
    @doc "LOCAL"
    (let! v1 auto (rec_val type_rec3 []))
    (= (. v1 u2) 102)
    (= (. v1 u3) 103)
    (= (. v1 u6) 106)
    (test::AssertEq# (. v1 u2) 102_u16)
    (test::AssertEq# (. v1 u3) 103_u64)
    (test::AssertEq# (. v1 u6) 106_u64)
    (= (. (. v1 u4) t1) false)
    (= (. (. v1 u4) t2) 402)
    (test::AssertEq# (. (. v1 u4) t2) 402_u32)
    (test::AssertEq# (. (. v1 u4) t1) false)
    (= (at (. v1 u5) 2) 502)
    (= (at (. v1 u5) 3) 503)
    (= (at (. v1 u5) 10) 510)
    (test::AssertEq# (at (. v1 u5) 2) 502_u16)
    (test::AssertEq# (at (. v1 u5) 3) 503_u16)
    (test::AssertEq# (at (. v1 u5) 10) 510_u16)
    @doc "GLOBAL ALT"
    (test::AssertEq# (. g3_alt u2) 0x1234_u16)
    (test::AssertEq# (. g3_alt u3) 0x4321_u64)
    (test::AssertEq# (. (. g3_alt u4) t1) true)
    (test::AssertEq# (. (. g3_alt u4) t2) 0x12345678_u32)
    (test::AssertEq# (at (. g3_alt u5) 0) 0x11_u16)
    (test::AssertEq# (at (. g3_alt u5) 2) 0x12_u16)
    @doc "GLOBAL"
    (test::AssertEq# (. g3 u2) 0x1234_u16)
    (test::AssertEq# (. g3 u3) 0x4321_u64)
    (test::AssertEq# (. (. g3 u4) t1) true)
    (test::AssertEq# (. (. g3 u4) t2) 0x12345678_u32)
    (test::AssertEq# (at (. g3 u5) 0) 0x11_u16)
    (test::AssertEq# (at (. g3 u5) 2) 0x12_u16)
    (= (. g3 u2) 102)
    (= (. g3 u3) 103)
    (= (. g3 u6) 106)
    (test::AssertEq# (. g3 u2) 102_u16)
    (test::AssertEq# (. g3 u3) 103_u64)
    (test::AssertEq# (. g3 u6) 106_u64)
    (= (. (. g3 u4) t1) false)
    (= (. (. g3 u4) t2) 402)
    (test::AssertEq# (. (. g3 u4) t2) 402_u32)
    (test::AssertEq# (. (. g3 u4) t1) false)
    (= (at (. g3 u5) 2) 502)
    (= (at (. g3 u5) 3) 503)
    (= (at (. g3 u5) 10) 510)
    (test::AssertEq# (at (. g3 u5) 2) 502_u16)
    (test::AssertEq# (at (. g3 u5) 3) 503_u16)
    (test::AssertEq# (at (. g3 u5) 10) 510_u16)
    @doc "test end"
    (test::Success#)
    @doc "return"
    (return 0))
)

