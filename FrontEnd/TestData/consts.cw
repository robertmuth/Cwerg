(module m1 [] :

(static_assert (== (+ 3_s32 4) 7))


(global a1 u32 7)


(static_assert (== a1 7))


(global a2 u32)


(static_assert (== a2 0))


(global a3 s32 -1)


(static_assert (== a3 -1))


(global a4 s32)


(static_assert (== a4 0))


(global a5 r32 1.0_r32)


(static_assert (== a5 1.0_r32))


(global a6 r32)


(static_assert (== a6 0.0_r32))


(global a7 bool true)


(static_assert (== a7 true))


(global a8 bool)


(static_assert (== a8 false))


(global c0 void void_val)


(global c1 auto 7_u32)


(global c2 u32 7)


(global c3 auto 7.0_r32)


@pub (global c4 auto "xxxxxx")


(global c10 auto c2)


@pub (defrec type_rec :
    (field s1 s32)
    (field s2 s32)
    (field s3 s32)
    (field s4 s32)
    (field b1 bool)
    (field u1 u64)
    (field u2 u64))


@doc "rec literal with explicit field name"
(global c32 auto (rec_val type_rec [7 9 7]))


(static_assert (== (. c32 s1) 7))


(static_assert (== (. c32 s2) 9))


(static_assert (== (. c32 s3) 7))


(static_assert (== (. c32 s4) 0))


(static_assert (== (. c32 b1) false))


@pub (enum type_enum S32 :
    (entry e1 7)
    (entry e2)
    (entry e3 19)
    (entry e4))


(global c20 auto type_enum:e3)


(static_assert (== (as c20 s32) 19))


(global c41 auto (. c32 s1))


(static_assert (== c41 7))


@doc "array literal with explicit indices"
(global c30 auto (array_val 30 uint [(index_val 0 1) (index_val 10 2) (index_val 20 3)]))


(global c40 auto (at c30 1))


(static_assert (== c40 0))


@doc "array literal"
(global c31 auto (array_val 30 uint [10 20 30]))


@doc "rec literal"
(global c33 auto (rec_val type_rec [7 9 7]))


(static_assert (== (. c33 s1) 7))


@pub (defrec type_rec2 :
    (field s1 (slice u8))
    (field s2 s32)
    (field s3 s32))


@doc "rec literal"
(global r01 auto (rec_val type_rec2 ["aaa" 9 7]))


@doc "rec literal"
(global r02 auto (rec_val type_rec2 [(field_val 9 s2) 7]))


(static_assert (== (len (. r02 s1)) 0))


(global auto1 s32)


(static_assert (== auto1 0))


(global auto2 bool)


(static_assert (== auto2 false))


(global auto3 r64)


(static_assert (== auto3 0.0))


(global auto4 type_rec2)


(static_assert (== (is auto4 type_rec2) true))


(static_assert (!= (is auto4 s32) true))


(static_assert (!= (is a8 s32) true))


(static_assert (== (is a8 bool) true))


(global! Real r32)


(global p1 (ptr r32) (& Real))


(global p2 (ptr! r32) (&! Real))


(static_assert (== (is p1 bool) false))


(static_assert (== (is p1 (ptr! r32)) false))


(static_assert (== (is p1 (ptr r32)) true))
)

