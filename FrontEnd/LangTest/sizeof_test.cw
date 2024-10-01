(module [] :

(static_assert (== (size_of u8) 1_uint))


(static_assert (== (size_of s16) 2))


(static_assert (== (size_of r32) 4))


(static_assert (== (size_of r64) 8))


@doc "assuming 64 bit pointers"
(static_assert (== (size_of (ptr u8)) 8))


(static_assert (== (size_of (ptr r64)) 8))


(static_assert (== (size_of (ptr (ptr s64))) 8))


(static_assert (== (size_of (array 20 r64)) 160))


(static_assert (== (size_of (span r64)) 16))


@pub (defrec type_rec :
    (field s1 s32)
    (field s2 s32)
    (field s3 s32)
    (field s4 s32)
    (field b1 bool)
    (field u1 u64)
    (field u2 u64))


(static_assert (== (size_of type_rec) 40))


(static_assert (== (offset_of type_rec s1) 0))


(static_assert (== (offset_of type_rec b1) 16))


(static_assert (== (offset_of type_rec u1) 24))


@pub (enum type_enum S32 :
    (entry e1 7)
    (entry e2)
    (entry e3 19)
    (entry e4))


(static_assert (== (size_of type_enum) 4))


(@wrapped type w1 s32)


(@wrapped type w2 void)


(@wrapped type w3 void)


(type ptr1 (ptr! s32))


@pub (type sum1 (union [bool u8]))


(static_assert (== (size_of sum1) 3))


@pub (type sum2 (union [bool s32 s64]))


(static_assert (== (size_of sum2) 16))


@pub (type sum3 (union [bool w3]))


(static_assert (== (size_of sum3) 3))


@pub (type sum4 (union [ptr1 w3]))


@doc "8 with union optimization"
(static_assert (== (size_of sum4) 16))


@pub (type sum5 (union [ptr1 w2 w3]))


@doc "8 with union optimization"
(static_assert (== (size_of sum5) 16))


@pub (type sum6 (union [
        ptr1
        w1
        w2
        w3]))


(static_assert (== (size_of sum6) 16))


@doc "just a compilation test"
(fun main [(param argc s32) (param argv (ptr (ptr u8)))] s32 :
   (return 0))
)
