(mod m1 [] [


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
   (entry e1 (ValNum 7))
   (entry e2 (ValAuto))
   (entry e3 19)
   (entry e4 auto)
])


(const c0 void (ValVoid))

(const  c1 auto (ValNum 7_u32)) 

(const  c2 u32 7) 

(const  c3 auto (ValNum 7.0_r32)) 

(const c10 auto c2)

(const c20 auto type_enum/e3)

(const c30 auto (ValArray uint 30 [
   (IndexVal 0 7) (IndexVal 10 9) (IndexVal 20 7)]))

(const c31 auto (ValRec type_rec [
   (FieldVal s1 7) (FieldVal s2 9) (FieldVal s3 7)]))

(const c40 auto  (ExprIndex c30 0))

(const c41 auto  (ExprField c31 s1))

(# "can Functions be assigned to consts?")

])