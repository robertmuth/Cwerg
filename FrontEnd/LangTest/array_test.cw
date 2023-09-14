(module main [] :
(import test)

(type type_array (array 3 bool))


(type type_slice (slice s32))


(global c1 auto (array_val 10 s32 [
        (index_val 1)
        (index_val 2)
        (index_val 3)]))


(global @mut c2 auto (array_val 10 s32 [
        (index_val 1)
        (index_val 2)
        (index_val 3)]))


@doc """ (let c20 auto (len c1)")
         "(let c21 auto (at c1 2))") """
(global dim auto 5_u16)


(fun foo [(param a (array 10 u8)) (param b (array dim u64))] u8 :
    (let v2 auto (at c1 0))
    (let v3 auto (& (at c1 0)))
    (let v4 auto (& @mut (at c2 0)))
    (= (at c2 0) 666)
    (return 66))

(fun update_array [(param s (slice @mut u8)) 
          (param pos uint) 
          (param new u8)] u8 :
    (let old auto (at s pos))
    (= (at s pos) new)
    (return old))


@doc "ERROR: (let f4 (slice mut s32) e1)"
(fun baz [] void :
    @doc "ERROR: (= (at c1 5) 0)"
    (let pc1 (ptr s32) (front c1))
    (= (at c2 5) 0)
)

(defrec @pub type_rec3 :
    (field u2 u16)
    (field u3 u64)
    (field u5 (array 10 u8))
    (field u6 u64))

(global @mut r1 auto (rec_val type_rec3 [
    (field_val (array_val 10 u8 [
                (index_val 77)
                (index_val 88)
                (index_val 99)]) u5)
]))


(global @mut c4 auto (array_val 10 u8 [
        (index_val 41)
        (index_val 51)
        (index_val 61)]))

(fun test_mixed_array [] void :
    @doc ""
    (let @mut @ref a auto (array_val 10 u8 [
        (index_val 1)
        (index_val 2)
        (index_val 3)]))
    (let pa auto (& a))
    (let pa_mut auto (& @mut a))
    (test::AssertEq! (at c4 2) 61_u8)
    (= c4 a)   
    (test::AssertEq! (at c4 2) 3_u8)
    (= (at c4 2) 4_u8)
    (= a c4) 
    (test::AssertEq! (at a 2) 4_u8)

    (test::AssertEq! (at (. r1 u5) 1) 88_u8)
    (= (. r1 u5)  a)
    (test::AssertEq! (at (. r1 u5) 1) 2_u8)
    (= (at (. r1 u5) 1)  111)
    (= a (. r1 u5))
    (test::AssertEq! (at a 1) 111_u8)
)

(fun test_local_array [] void :
    @doc ""
    (let @mut @ref a auto (array_val 10 u8 [
        (index_val 1)
        (index_val 2)
        (index_val 3)]))   
    (let @ref b auto (array_val 10 u8 [
        (index_val 4)
        (index_val 5)
        (index_val 6)])) 
    (let pa auto (& a))
    (let pa_mut auto (& @mut a))
    (let pb auto (& b))
  
    (test::AssertEq! (at a 0) 1_u8)
    (test::AssertEq! (at b 2) 6_u8)
    (= (at a 0) 6)
    (test::AssertEq! (at a 0) 6_u8)

    (= (at (^ pa_mut) 2) 77_u8)
    (test::AssertEq! (at (^ pa) 2) 77_u8)
    (test::AssertEq! (at (^ pa_mut) 2) 77_u8)

    (test::AssertEq! (at (^ pb) 0) 4_u8)

    (= (at (^ pa_mut) 0) 66)
    (test::AssertEq! (at a 0) 66_u8)

    (= a b)
    (test::AssertEq! (at a 0) 4_u8)
    (test::AssertEq! (update_array [a 0 2]) 4_u8)
    (test::AssertEq! (update_array [a 0 3]) 2_u8)
    (test::AssertEq! (update_array [(^ pa_mut) 0 2]) 3_u8)
)


(global d1 auto (array_val 10 s32 [
        (index_val 11)
        (index_val 22)
        (index_val 33)]))


(global @mut d2 auto (array_val 10 s32 [
        (index_val 111)
        (index_val 222)
        (index_val 333)]))

(global @mut c3 auto (array_val 10 u8 [
        (index_val 4)
        (index_val 5)
        (index_val 6)]))

(global e1 (slice s32) d1)


(global e2 (slice @mut s32) d2)


@doc "ERROR: (let e3 (slice mut s32) d2)"
(global f1 (slice s32) e1)

(global f3 (slice s32) e2)

(global f2 (slice @mut s32) e2)

(fun test_global_array [] void :
   @doc "basic"
    (test::AssertEq! (at c1 1) 2_s32)
    (test::AssertEq! (at c2 2) 3_s32)
    (test::AssertEq! (at e1 1) 22_s32)
    (test::AssertEq! (at e2 2) 333_s32)
    (test::AssertEq! (at f1 1) 22_s32)
    (test::AssertEq! (at f2 2) 333_s32)
    (test::AssertEq! (at f3 0) 111_s32)
    @doc "basic"
    (test::AssertEq! (at c3 0) 4_u8)
    (test::AssertEq! (update_array [c3 0 77]) 4_u8)
    (test::AssertEq! (update_array [c3 0 5]) 77_u8)
)

(fun @cdecl main [(param argc s32) (param argv (ptr (ptr u8)))] s32 :
    (stmt (test_global_array []))
    (stmt (test_local_array []))
    (stmt (test_mixed_array []))
    @doc "test end"
    (test::Success!)
    (return 0))


)


