(defmod m1 [] [


(static_assert (== (sizeof u8) 1_uint))
(static_assert (== (sizeof s16) 2))
(static_assert (== (sizeof r32) 4))
(static_assert (== (sizeof r64) 8))

(# "assuming 64 bit pointers")

(static_assert (== (sizeof (TypePtr u8)) 8))
(static_assert (== (sizeof (TypePtr r64)) 8))
(static_assert (== (sizeof (TypePtr (TypePtr s64))) 8))


(static_assert (== (sizeof (TypeArray 20 r64)) 160))

(static_assert (== (sizeof (TypeSlice r64)) 16))

(defrec pub type_rec [
   (# "this is a comment with \" with quotes \t ")
   (field s1 s32 (ValNum 7))
   (field s2 s32 (ValUndef))
   (field s3 s32 (ValUndef))
   (field s3 s32 undef)

   (field b1 bool false)
   (field u1 u64 666)
   (field u2 u64 666_u64)
])

(static_assert (== (sizeof type_rec) 40))
(static_assert (== (offsetof type_rec s1) 0))
(static_assert (== (offsetof type_rec b1) 16))
(static_assert (== (offsetof type_rec u1) 24))

(defenum pub type_enum S32 [
   (# "this is a comment with \" with quotes \t ")
   (entry e1 (ValNum 7))
   (entry e2)
   (entry e3 19)
   (entry e4)
])


(static_assert (== (sizeof type_enum) 4))

(deftype wrapped w1 s32)
(deftype wrapped w2 void)
(deftype wrapped w3 void)
(deftype ptr1 (ptr mut s32))

(deftype pub sum1 (TypeSum [bool u8]))

(static_assert (== (sizeof sum1) 3))

(deftype pub sum2 (TypeSum [bool s32 s64]))

(static_assert (== (sizeof sum2) 16))

(deftype pub sum3 (TypeSum [bool w3]))

(static_assert (== (sizeof sum3) 3))

(deftype pub sum4 (TypeSum [ptr1 w3]))

(static_assert (== (sizeof sum4) 8))

(deftype pub sum5 (TypeSum [ptr1 w2 w3]))

(static_assert (== (sizeof sum5) 8))

(deftype pub sum6 (TypeSum [ptr1 w1 w2 w3]))

(static_assert (== (sizeof sum6) 16))

])