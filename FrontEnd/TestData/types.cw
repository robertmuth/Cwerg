(mod m1 [] [


(type wrapped t1 s32)
(type wrapped t2 void)
(type wrapped t3 void)

(rec pub type_rec [
   (# "this is a comment with \" with quotes \t ")
   (field s1 s32 (ValNum 7))
   (field s2 s32 (ValUndef))
   (field s3 s32 (ValUndef))
   (field s3 s32 undef)

   (field b1 bool false)
   (field u1 u64 666)
   (field u2 u64 666_u64)
])

(enum pub type_enum S32 [
   (# "this is a comment with \" with quotes \t ")
   (entry s1 (ValNum 7))
   (entry s2 (Auto))
   (entry s3 19)
   (entry s4 auto)
])

(type type_array (TypeArray (ValNum 3) bool))

(type type_slice (TypeSlice type_rec))

(type type_ptr (ptr mut s32))

(type pub type_union (TypeSum [s32 void type_ptr]))

(type pub type_union2 (TypeSum [s32 void (TypeSum [type_union u8])]))

(type type_fun (sig [(param a bool) (param b bool) (param c s32)] s32))



])