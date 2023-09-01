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

(type TaggedUnionDelta (sumdelta TaggedUnion3 TaggedUnion4))
(static_assert (== (sizeof TaggedUnionDelta) 8))
(static_assert (== (typeid TaggedUnionDelta) (typeid s64)))



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


(fun test_tagged_union_basic [] void :
    (let @mut x TaggedUnion3  true)
    (let @mut y TaggedUnion3  undef)
    (= y x)
    (test::AssertTrue (is x bool))
    (test::AssertFalse (is x s32))
    (test::AssertTrue (is y bool))
    (test::AssertFalse (is y s32))
    (= x 777_s32)
    (= y x)
    (test::AssertFalse (is x bool))
    (test::AssertTrue (is x s32))
    (test::AssertFalse (is y bool))
    (test::AssertTrue (is y s32))
)

(fun fun_param [
        (param a bool)
        (param b bool)
        (param c s32)
        (param x TaggedUnion3)] void :
    (if a :
         (test::AssertTrue (is x bool))
    :
        (test::AssertTrue (is x s32))
    ))

(fun test_tagged_union_parameter [] void :
    (let @mut x TaggedUnion3 true)
    (stmt (call fun_param [true true 0 x]))
    (= x 666_s32)
    (stmt (call fun_param [false true 666 x]))
)

(fun fun_result [
        (param a bool)
        (param b bool)
        (param c s32)] TaggedUnion3 :
    (let @mut out  TaggedUnion3 undef)
    (if a :
        (= out b) 
    :
        (= out c))
    (return out))


(fun test_tagged_union_result [] void :
    (let @mut x auto (call fun_result [true false 2]))
    (test::AssertTrue (is x bool))
    (test::AssertFalse (is x s32))

    (= x (call fun_result [false false 2]))
    (test::AssertFalse (is x bool))
    (test::AssertTrue (is x s32))
)

(fun main [(param argc s32) (param argv (ptr (ptr u8)))] s32 :
    (stmt (call test_tagged_union_basic []))
    (stmt (call test_tagged_union_result []))
    (stmt (call test_tagged_union_parameter []))

    @doc "test end"
    (stmt (call SysPrint ["OK\n"]))
    (return 0))

)


