(module m1 [] [


(type type_array (TypeArray (ValNum 3) bool))

(type type_slice (slice s32))

(global c1 auto (ValArray s32 10 [(IndexVal 1) (IndexVal 2) (IndexVal 3)]))
(global mut c2 auto (ValArray s32 10 [(IndexVal 1) (IndexVal 2) (IndexVal 3)]))


(# "(let c20 auto (len c1)" )

(# "(let c21 auto (at c1 2))" )

(global dim auto 5_u16)

(fun fun1 [(param a (TypeArray 10 u8)) (param b (TypeArray dim u64))] u8 [
   (let v2 auto (at c1 0))
   (let v3 auto (& (at c1 0)))
   (let v4 auto (& mut (at c2 0)))

   (return 66) 
])

(global d1 (array 6 s32) (ValArray s32 10 [(IndexVal 1) (IndexVal 2) (IndexVal 3)]))
(global mut d2 (array 8 s32) (ValArray s32 10 [(IndexVal 1) (IndexVal 2) (IndexVal 3)]))


(global e1 (slice s32) d1)
(global e2 (slice mut s32) d2)
(# "ERROR: (let e3 (slice mut s32) d2)")

(global f1 (slice s32) e1)
(global f2 (slice mut s32) e2)
(global f3 (slice s32) e2)
(# "ERROR: (let f4 (slice mut s32) e1)")

])