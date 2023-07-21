(module m1 [] :
(type @wrapped t1 s32)


(type @wrapped t2 void)


(type @wrapped t3 void)


(type type_ptr (ptr @mut s32))


(type @pub type_union (union [
        s32
        void
        type_ptr]))


(type @pub type_union2 (union [
        s32
        void
        (union [type_union u8])]))


(type @pub sum1_t (union [
        bool
        s32
        s64]))


(type @pub sum2_t (union [bool s32]))


(type @pub sum3_t (union [
        t2
        t3
        type_ptr]))


(fun fun1 [
        (param a sum1_t)
        (param b bool)
        (param c s32)] sum2_t :
    (let @mut x sum2_t true)
    (let y sum1_t x)
    (= x false)
    (if (is x sum2_t) :
        (return false)
        :)
    (= x (or (tryas x bool undef) false))
    (stmt (call fun1 [
            true
            false
            1]))
    (return true))


(defrec @pub rec1 :
    (field s1 sum2_t)
    (field s2 sum2_t))


(defrec @pub rec2 :
    (field s1 sum3_t)
    (field s2 sum3_t))


(type @pub sum10_t (union [
        bool
        s32
        s64]))


(type @pub sum11_t (union [bool u16]))


(type @pub sum12_t (union [type_ptr u16]))

)


