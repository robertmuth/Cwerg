(defmod m1 [] [


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


(const c0 void void_val)

(const  c1 auto (ValNum 7_u32)) 

(const  c2 u32 7) 

(const  c3 auto (ValNum 7.0_r32)) 

(const pub c4 auto "xxxxxx")


(const c10 auto c2)

(const c20 auto type_enum/e3)

(static_assert (== (as c20 s32) 19))

(# "array literal with explicit indices")
(const c30 auto (ValArray uint 30 [
   (IndexVal 0 1) 
   (IndexVal 10 2) 
   (IndexVal 20 3)]))

(# "array literal")
(const c31 auto (ValArray uint 30 [
   (IndexVal 10) 
   (IndexVal 20) 
   (IndexVal 30)]))

(# "rec literal with explicit field name")
(const c32 auto (ValRec type_rec [
   (FieldVal 7 s1) 
   (FieldVal 9 s2) 
   (FieldVal 7 s3)]))

(# "rec literal")
(const c33 auto (ValRec type_rec [
   (FieldVal 7) 
   (FieldVal 9) 
   (FieldVal 7)]))

(const c40 auto  (ExprIndex c30 1))

(static_assert (== c40 0))

(const c41 auto  (ExprField c32 s1))

(static_assert (== c41 7))

(static_assert (== (ExprField c33 s1) 7))

(static_assert (== (+ 3_s32 4) 7))

(# "can Functions be assigned to consts?")

])