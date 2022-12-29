(module m1 [] [


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

(enum pub type_enum S32 [
   (# "this is a comment with \" with quotes \t ")
   (entry e1 (ValNum 7))
   (entry e2)
   (entry e3 19)
   (entry e4)
])


(let c0 void void_val)

(let c1 auto (ValNum 7_u32)) 

(let c2 u32 7) 

(let c3 auto (ValNum 7.0_r32)) 

(let pub c4 auto "xxxxxx")


(let c10 auto c2)

(let c20 auto type_enum/e3)

(static_assert (== (as c20 s32) 19))

(# "array literal with explicit indices")
(let c30 auto (ValArray uint 30 [
   (IndexVal 0 1) 
   (IndexVal 10 2) 
   (IndexVal 20 3)]))

(# "array literal")
(let c31 auto (ValArray uint 30 [
   (IndexVal 10) 
   (IndexVal 20) 
   (IndexVal 30)]))

(# "rec literal with explicit field name")
(let c32 auto (ValRec type_rec [
   (FieldVal 7 s1) 
   (FieldVal 9 s2) 
   (FieldVal 7 s3)]))

(# "rec literal")
(let c33 auto (ValRec type_rec [
   (FieldVal 7) 
   (FieldVal 9) 
   (FieldVal 7)]))

(let c40 auto  (ExprIndex c30 1))

(static_assert (== c40 0))

(let c41 auto  (ExprField c32 s1))

(static_assert (== c41 7))

(static_assert (== (ExprField c33 s1) 7))

(static_assert (== (+ 3_s32 4) 7))

(# "TODO add examples with Functions")

])