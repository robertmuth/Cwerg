(mod m1 [] [


(type wrapped t1 s32)
(type wrapped t2 void)
(type wrapped t3 void)

(type type_ptr (ptr mut s32))

(type pub type_union (TypeSum [s32 void type_ptr]))

(type pub type_union2 (TypeSum [s32 void (TypeSum [type_union u8])]))



(type pub fun1_result (TypeSum [bool s32]))

(fun fun1 [(param a bool) (param b bool) (param c s32)] fun1_result [
   (return true) 
])

])