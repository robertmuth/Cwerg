(defmod m1 [] [


(deftype wrapped t1 s32)
(deftype wrapped t2 void)
(deftype wrapped t3 void)

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


(defrec pub linked_list [
   (# "this is a comment with \" with quotes \t ")
   (field s1 (TypeSum [void (ptr linked_list)]) void)
])

(defenum pub type_enum S32 [
   (# "this is a comment with \" with quotes \t ")
   (entry s1 (ValNum 7))
   (entry s2)
   (entry s3 19)
   (entry s4)
])

(deftype type_array (TypeArray (ValNum 3) bool))

(deftype type_slice (TypeSlice type_rec))

(deftype type_ptr (ptr mut s32))

(deftype pub type_union (TypeSum [s32 void type_ptr]))

(deftype pub type_union2 (TypeSum [s32 void (TypeSum [type_union u8])]))

(deftype type_fun (sig [(param a bool) (param b bool) (param c s32)] s32))

(defun fun [(param a type_union)] s32 [
   (return (asnot a (TypeSum [void type_ptr]))) 
])

])