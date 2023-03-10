(module m1 [] [


(type wrapped t1 s32)
(type wrapped t2 void)
(type wrapped t3 void)

(defrec pub type_rec [
   (# "this is a comment with \" with quotes \t ")
   (field s1 s32)
   (field s2 s32)
   (field s3 s32)
   (field s4 s32)

   (field b1 bool)
   (field u1 u64)
   (field u2 u64)
])


(defrec pub linked_list [
   (# "this is a comment with \" with quotes \t ")
   (field s1 (TypeSum [void (ptr linked_list)]))
])

(enum pub type_enum S32 [
   (# "this is a comment with \" with quotes \t ")
   (entry s1)
   (entry s2)
   (entry s3)
   (entry s4)
])

(type type_array (array (ValNum 3) bool))

(type type_slice (TypeSlice type_rec))

(type type_ptr (ptr mut s32))

(type pub type_union (TypeSum [s32 void type_ptr]))

(type pub type_union2 (TypeSum [s32 void (TypeSum [type_union u8])]))

(type type_fun (sig [(param a bool) (param b bool) (param c s32)] s32))

(fun funx [(param a type_union)] s32 [
   (return (asnot a (TypeSum [void type_ptr]))) 
])

])