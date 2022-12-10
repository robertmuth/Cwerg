(module m1 [] [


(type type_array (TypeArray (ValNum 3) bool))

(type type_slice (slice s32))

(let c1 auto (ValArray s32 10 [(IndexVal 1) (IndexVal 2) (IndexVal 3)]))
(let mut c2 auto (ValArray s32 10 [(IndexVal 1) (IndexVal 2) (IndexVal 3)]))


(let c20 auto (len c1))

(let c21 auto (at c1 2))

(const dim auto 5_u16)

(fun fun1 [(param a (TypeArray 10 u8)) (param b (TypeArray dim u64))] u8 [
   (let v1 auto (chop a))
   (return 66) 
])

(let d1 (array 6 s32) (ValArray s32 10 [(IndexVal 1) (IndexVal 2) (IndexVal 3)]))
(let d2 (array mut 8 s32) (ValArray s32 10 [(IndexVal 1) (IndexVal 2) (IndexVal 3)]))


(let e1 (slice s32) d1)
(let e2 (slice mut s32) d2)
(# "ERROR: (let e3 (slice mut s32) d2)")

(let f1 (slice s32) e1)
(let f2 (slice mut s32) e2)
(let f3 (slice s32) e2)
(# "ERROR: (let f4 (slice mut s32) e1)")

])