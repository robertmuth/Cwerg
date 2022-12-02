(defmod m1 [] [


(deftype wrapped t1 s32)
(deftype wrapped t2 void)
(deftype wrapped t3 void)

(deftype type_ptr (ptr mut s32))

(deftype pub type_union (TypeSum [s32 void type_ptr]))

(deftype pub type_union2 (TypeSum [s32 void (TypeSum [type_union u8])]))


(deftype pub sum1_t (TypeSum [bool s32 s64]))

(deftype pub sum2_t (TypeSum [bool s32]))


(defun fun1 [(param a sum1_t) (param b bool) (param c s32)] sum2_t [
    (let x sum2_t true)
    (let y sum1_t x)
   (= x false)
   (if (is x sum2_t) [(return false)] [])
   (or= x false)
   (stmt discard (call fun1 [true false 1]))
   (return true) 
])

(defrec pub rec1 [
   (# "this is a comment with \" with quotes \t ")
   (field s1 sum2_t (ValNum 7_s32))
   (field s2 sum2_t true)
])


])