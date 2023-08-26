(module main [] :
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

(global @mut c3 auto (array_val 10 u8 [
        (index_val 4)
        (index_val 5)
        (index_val 6)]))

(defrec @pub type_rec3 :
    (field u2 u16)
    (field u3 u64)
    (field u5 (array 10 u8))
    (field u6 u64))

(global @mut r1 type_rec3 undef)


@doc """ (let c20 auto (len c1)")
         "(let c21 auto (at c1 2))") """
(global dim auto 5_u16)


(fun foo [(param a (array 10 u8)) (param b (array dim u64))] u8 :
    (let v2 auto (at c1 0))
    (let v3 auto (& (at c1 0)))
    (let v4 auto (& @mut (at c2 0)))
    (= (at c2 0) 666)
    (return 66))

(fun bar [(param s (slice @mut u8)) 
          (param pos uint) 
          (param new u8)] u8 :
    (let old auto (at s pos))
    (= (at s pos) new)
    (return old))


(fun bar2 [] u8 :
    (let @mut @ref a auto (array_val 10 u8 [
        (index_val 1)
        (index_val 2)
        (index_val 3)]))   
    (let @ref b auto (array_val 10 u8 [
        (index_val 1)
        (index_val 2)
        (index_val 3)])) 
    (let pa auto (& a))
    (let pa_mut auto (& @mut a))
    (let pb auto (& b))
    (let pb_mut auto (& @mut b))

    (= (at a 0) 6)
    (= (at (^ pa_mut) 0) 6)
    (= a b)
    (= c3 a)
    (= c3 b)
    (= (. r1 u5)  a)
    (= (. r1 u5)  b)
    (= (at (. r1 u5) 1)  66)
    (stmt (call bar [a 0 2]))
    (stmt (call bar [a 0 2]))

    (return (call bar [(^ pa_mut) 0 2]))
)


(global d1 auto (array_val 10 s32 [
        (index_val 1)
        (index_val 2)
        (index_val 3)]))


(global @mut d2 auto (array_val 10 s32 [
        (index_val 1)
        (index_val 2)
        (index_val 3)]))


(global e1 (slice s32) d1)


(global e2 (slice @mut s32) d2)


@doc "ERROR: (let e3 (slice mut s32) d2)"
(global f1 (slice s32) e1)


(global f2 (slice @mut s32) e2)


(global f3 (slice s32) e2)


@doc "ERROR: (let f4 (slice mut s32) e1)"
(fun baz [] void :
    @doc "ERRPOR: (= (at c1 5) 0)"
    (let pc1 (ptr s32) (front c1))
    (= (at c2 5) 0)
)

(fun main [(param argc s32) (param argv (ptr (ptr u8)))] s32 :
    @doc "test end"
    (stmt (call SysPrint ["OK\n"]))
    (return 0))


)


