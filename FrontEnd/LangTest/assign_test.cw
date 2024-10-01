(module [] :
(import test)


@pub (defrec type_rec1 :
    @doc """this is a comment with \" with quotes \t """
    (field i1 s64)
    (field i2 u64)
    (field i3 s32)
    (field i4 u32)
    (field i5 s16)
    (field i6 u16)
    (field i7 s8)
    (field i8 u8)
    (field f1 r64)
    (field f2 r32)
    (field b1 bool)
    (field a1 (vec 7 u8))
    (field a2 (vec 7 u16))
    (field a3 (vec 7 u32))
    (field a4 (vec 7 u64))
    (field a5 (vec 7 r32))
    (field a6 (vec 7 r64)))


@pub (defrec type_rec2 :
    (field t1 bool)
    (field t2 u32)
    (field t3 type_rec1)
    (field t4 bool))


@pub (defrec type_rec3 :
    (field u2 u16)
    (field u3 u64)
    (field u4 type_rec2)
    (field u5 (vec 13 u16))
    (field u6 u64))


(global! ga1 (vec 5 s64) undef)


(global! gr1 type_rec1 undef)


(global! gar1 (vec 5 type_rec1) undef)


(global! gr2 type_rec2 undef)


(global! gar2 (vec 5 type_rec2) undef)


(fun get_addr [] (ptr! type_rec1) :
    (return (&! gr1)))


(fun main [(param argc s32) (param argv (ptr (ptr u8)))] s32 :
    @doc "a1 u32"
    (= (at ga1 3) 0x8765432187654321)
    (test::AssertEq# (at ga1 3) 0x8765432187654321_s64)
    (+= (at ga1 3) 0x1)
    (test::AssertEq# (at ga1 3) 0x8765432187654322_s64)
    @doc "gr1 s64"
    (= (. gr1 i1) 0x8765432187654321)
    (test::AssertEq# (. gr1 i1) 0x8765432187654321_s64)
    (+= (. gr1 i1) 0x1)
    (test::AssertEq# (. gr1 i1) 0x8765432187654322_s64)
    @doc "gr1 u64"
    (= (. gr1 i2) 0x1234567812345678)
    (test::AssertEq# (. gr1 i2) 0x1234567812345678_u64)
    (-= (. gr1 i2) 0x1)
    (test::AssertEq# (. gr1 i2) 0x1234567812345677_u64)
    @doc "gr1 u64 via pointer"
    (= (^. (get_addr []) i2) 0x1234567812345678)
    (test::AssertEq# (^. (get_addr []) i2) 0x1234567812345678_u64)
    (-= (^. (get_addr []) i2) 0x1)
    (test::AssertEq# (^. (get_addr []) i2) 0x1234567812345677_u64)
    @doc "gar1 s64"
    (= (. (at gar1 3) i1) 0x8765432187654321)
    (test::AssertEq# (. (at gar1 3) i1) 0x8765432187654321_s64)
    @doc "gr2 s64"
    (= (. (. gr2 t3) i1) 0x8765432187654321)
    (test::AssertEq# (. (. gr2 t3) i1) 0x8765432187654321_s64)
    (+= (. (. gr2 t3) i1) 0x1)
    (test::AssertEq# (. (. gr2 t3) i1) 0x8765432187654322_s64)
    @doc "gr2 u64"
    (= (. (. gr2 t3) i2) 0x1234567812345678)
    (test::AssertEq# (. (. gr2 t3) i2) 0x1234567812345678_u64)
    @doc "test end"
    (test::Success#)
    (return 0))
)
