(module m1 [] :
(static_assert (== (sizeof u8) 1_uint))


(static_assert (== (sizeof s16) 2))


(static_assert (== (sizeof r32) 4))


(static_assert (== (sizeof r64) 8))


@doc "assuming 64 bit pointers"
(static_assert (== (sizeof (ptr u8)) 8))


(static_assert (== (sizeof (ptr r64)) 8))


(static_assert (== (sizeof (ptr (ptr s64))) 8))


(static_assert (== (sizeof (array 20 r64)) 160))


(static_assert (== (sizeof (slice r64)) 16))


(defrec @pub type_rec :
    (field s1 s32)
    (field s2 s32)
    (field s3 s32)
    (field s4 s32)
    (field b1 bool)
    (field u1 u64)
    (field u2 u64))


(static_assert (== (sizeof type_rec) 40))


(static_assert (== (offsetof type_rec s1) 0))


(static_assert (== (offsetof type_rec b1) 16))


(static_assert (== (offsetof type_rec u1) 24))


(enum @pub type_enum S32 :
    (entry e1 7)
    (entry e2)
    (entry e3 19)
    (entry e4))


(static_assert (== (sizeof type_enum) 4))


(type @wrapped w1 s32)


(type @wrapped w2 void)


(type @wrapped w3 void)


(type ptr1 (ptr! s32))


(type @pub sum1 (union [bool u8]))


(static_assert (== (sizeof sum1) 3))


(type @pub sum2 (union [
        bool
        s32
        s64]))


(static_assert (== (sizeof sum2) 16))


(type @pub sum3 (union [bool w3]))


(static_assert (== (sizeof sum3) 3))


(type @pub sum4 (union [ptr1 w3]))


(static_assert (== (sizeof sum4) 8))


(type @pub sum5 (union [
        ptr1
        w2
        w3]))


(static_assert (== (sizeof sum5) 8))


(type @pub sum6 (union [
        ptr1
        w1
        w2
        w3]))


(static_assert (== (sizeof sum6) 16))

)
