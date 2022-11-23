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

(defenum pub type_enum S32 [
   (# "this is a comment with \" with quotes \t ")
   (entry e1 (ValNum 7))
   (entry e2)
   (entry e3 19)
   (entry e4)
])


(static_assert (== (sizeof type_enum) 4))


])