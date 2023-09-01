(module main [] :
(import test)

(type @wrapped t1 s32)
(type @wrapped t2 void)
(type @wrapped t3 void)
(type type_ptr (ptr @mut s32))


(type TaggedUnion1 (union [
        s32
        void
        type_ptr]))

(static_assert (== (sizeof TaggedUnion1) 16))


(type TaggedUnion2 (union [
        s32
        void
        (union  [TaggedUnion1 u8])]))

(static_assert (== (sizeof TaggedUnion2) 16))


(type TaggedUnion3 (union [
        bool
        s32
        s64]))

(static_assert (== (sizeof TaggedUnion3) 16))


(type TaggedUnion4 (union [bool s32]))

(static_assert (== (sizeof TaggedUnion4) 8))


(type @pub TaggedUnion5 (union [
        t2
        t3
        s8]))

(static_assert (== (sizeof TaggedUnion5) 3))


(type  TaggedUnion6 (union [bool u16]))

(static_assert (== (sizeof TaggedUnion6) 4))



(type TaggedUnion (union [bool u64 u32 r32 r64 (array 32 u8)]))

(static_assert (== (sizeof TaggedUnion) 40))


(defrec rec1 :
    (field s1 TaggedUnion5)
    (field s2 TaggedUnion5))


(defrec @pub rec2 :
    (field s1 TaggedUnion1)
    (field s2 TaggedUnion2))


@doc """
(type @pub sum11_t (union [bool u16]))
(type @pub sum12_t (union [type_ptr u16])) """


@doc """
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
    (return true)) """


(fun test_tagged_union [] void :
    (let @mut x TaggedUnion3  true)
    (let @mut y TaggedUnion3  undef)
    (= y x)
    (test::AssertEq (is x bool) true)
    (test::AssertEq (is x s32) false)
    (test::AssertEq (is y bool) true)
    (test::AssertEq (is y s32) false)
    (= x 777_s32)
    (= y x)
    (test::AssertEq (is x bool) false)
    (test::AssertEq (is x s32) true)
    (test::AssertEq (is y bool) false)
    (test::AssertEq (is y s32) true)
)


(fun main [(param argc s32) (param argv (ptr (ptr u8)))] s32 :
    (stmt (call test_tagged_union []))

    @doc "test end"
    (stmt (call SysPrint ["OK\n"]))
    (return 0))

)


