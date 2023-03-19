(module m1 [] [


(type type_array (array 3 bool))

(type type_slice (slice s32))

(global c1 auto (array_val 10 s32 [(index_val 1) (index_val 2) (index_val 3)]))
(global mut c2 auto (array_val 10 s32 [(index_val 1) (index_val 2) (index_val 3)]))


(# "(let c20 auto (len c1)" )

(# "(let c21 auto (at c1 2))" )

(global dim auto 5_u16)

(fun foo [(param a (array 10 u8)) (param b (array dim u64))] u8 [
   (let v2 auto (at c1 0))
   (let v3 auto (& (at c1 0)))
   (let v4 auto (& mut (at c2 0)))
   (= (at c2 0 ) 666)
   (return 66) 
])

(global d1 auto (array_val 10 s32 [(index_val 1) (index_val 2) (index_val 3)]))
(global mut d2 auto (array_val 10 s32 [(index_val 1) (index_val 2) (index_val 3)]))


(global e1 (slice s32) d1)
(global e2 (slice mut s32) d2)
(# "ERROR: (let e3 (slice mut s32) d2)")

(global f1 (slice s32) e1)
(global f2 (slice mut s32) e2)
(global f3 (slice s32) e2)
(# "ERROR: (let f4 (slice mut s32) e1)")

(fun baz [] void [
   (# "ERRPOR: (= (at c1 5) 0)")
   (let pc1 (ptr s32) (front c1))
   (= (at c2 5) 0)
])

])