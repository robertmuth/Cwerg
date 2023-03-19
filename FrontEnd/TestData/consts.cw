(module m1 [] [


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

(enum pub type_enum S32 [
   (# "this is a comment with \" with quotes \t ")
   (entry e1 7)
   (entry e2)
   (entry e3 19)
   (entry e4)
])


(global c0 void void_val)

(global c1 auto 7_u32) 

(global c2 u32 7) 

(global c3 auto 7.0_r32) 

(global pub c4 auto "xxxxxx")


(global c10 auto c2)

(global c20 auto type_enum/e3)   

(static_assert (== (as c20 s32) 19))

(# "array literal with explicit indices")
(global c30 auto (array_val 30 uint [
   (index_val 0 1) 
   (index_val 10 2) 
   (index_val 20 3)]))

(# "array literal")
(global c31 auto (array_val 30 uint [
   (index_val 10) 
   (index_val 20) 
   (index_val 30)]))

(# "rec literal with explicit field name")
(global c32 auto (rec_val type_rec [
   (field_val 7 s1) 
   (field_val 9 s2) 
   (field_val 7 s3)]))

(# "rec literal")
(global c33 auto (rec_val type_rec [
   (field_val 7) 
   (field_val 9) 
   (field_val 7)]))

(global c40 auto  (at c30 1))

(static_assert (== c40 0))

(global c41 auto  (. c32 s1))

(static_assert (== c41 7))

(static_assert (== (. c33 s1) 7))

(static_assert (== (+ 3_s32 4) 7))

(# "TODO add examples with Functions")

])