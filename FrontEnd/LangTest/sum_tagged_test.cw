(module [] :
(import test)


(@wrapped type void_t1 void)


(global void_t1_val auto (wrap_as void_val void_t1))


(@wrapped type void_t2 void)


(global void_t2_val auto (wrap_as void_val void_t2))


(@wrapped type void_t3 void)


(global void_t3_val auto (wrap_as void_val void_t3))


(static_assert (== (size_of (union [void_t1 void_t2])) (size_of typeid)))


(static_assert (== (size_of (union [void_t1 void_t2 void_t3])) (size_of typeid)))


(type type_ptr (ptr! s32))


(type Union1 (union [s32 void type_ptr]))


(static_assert (== (size_of Union1) (* (size_of type_ptr) 2)))


(type Union2 (union [s32 void (union [Union1 u8])]))


(static_assert (== (size_of Union2) (* (size_of type_ptr) 2)))


(type Union2Simplified (union [
        s32
        void
        u8
        type_ptr]))


(static_assert (== (typeid_of Union2) (typeid_of Union2Simplified)))


(type Union3 (union [
        bool
        u8
        s32
        s64]))


(static_assert (== (size_of Union3) 16))


(type Delta1 (union_delta Union3 (union [bool u8 s32])))


(static_assert (== (size_of Delta1) 8))


(static_assert (== (typeid_of Delta1) (typeid_of s64)))


(type Delta2 (union_delta Union3 (union [bool u8])))


(static_assert (== (typeid_of Delta2) (typeid_of (union [s32 s64]))))


(type Delta3 (union_delta Union3 (union [bool u8 s64])))


(static_assert (== (typeid_of Delta3) (typeid_of s32)))


(type Union5 (union [void_t2 void_t3 s8]))


(static_assert (== (size_of Union5) 3))


(type Union6 (union [bool u16]))


(static_assert (== (size_of Union6) 4))


(type Union (union [
        bool
        u64
        u32
        r32
        r64
        (array 32 u8)]))


(static_assert (== (size_of Union) 40))


(defrec rec1 :
    (field s1 Union5)
    (field s2 Union5))


(defrec rec2 :
    (field s1 Union1)
    (field s2 Union2))


(global global_rec1 auto (rec_val rec1 [1_s8 2_s8]))


@doc """
@pub (type sum11_t (union [bool u16]))
@pub (type sum12_t (union [type_ptr u16])) """
(fun test_tagged_union_basic [] void :
    (let! x Union3 true)
    (let! y Union3 undef)
    (let! z s32 777)
    (= y x)
    (test::AssertTrue# (is x bool))
    (test::AssertFalse# (is x s32))
    (test::AssertTrue# (is y bool))
    (test::AssertFalse# (is y s32))
    (= x 777_s32)
    (= x z)
    (= y x)
    (test::AssertFalse# (is x bool))
    (test::AssertTrue# (is x s32))
    (test::AssertFalse# (is y bool))
    (test::AssertTrue# (is y s32))
    (test::AssertTrue# (== y 777_s32))
    (test::AssertTrue# (== 777_s32 y)))


@pub (type UnionVoid (union [void void_t2 void_t3]))


(fun test_tagged_union_void [] void :
    (let! x012 (union [void void_t1 void_t2]) void_val)
    (let! x123 (union [void_t1 void_t2 void_t3]) void_t3_val)
    (let! x12 (union [void_t1 void_t2]) void_t1_val)
    (= x012 x12))


(fun fun_param [
        (param a bool)
        (param b bool)
        (param c s32)
        (param x Union3)] void :
    (if a :
        (test::AssertTrue# (is x bool))
     :
        (test::AssertTrue# (is x s32))))


(fun test_tagged_union_parameter [] void :
    (let! x Union3 true)
    (do (fun_param [true true 0 x]))
    (= x 666_s32)
    (do (fun_param [false true 666 x])))


(fun fun_result [
        (param a bool)
        (param b bool)
        (param c s32)] Union3 :
    (let! out Union3 undef)
    (if a :
        (= out b)
     :
        (= out c))
    (return out))


(fun test_tagged_union_result [] void :
    (let! x auto (fun_result [true false 2]))
    (test::AssertTrue# (is x bool))
    (test::AssertFalse# (is x s32))
    (= x (fun_result [false false 2]))
    (test::AssertFalse# (is x bool))
    (test::AssertTrue# (is x s32)))


(fun test_tagged_union_narrowto [] void :
    (let! x Union3 true)
    (let! y auto (narrow_as x bool))
    (test::AssertTrue# y)
    (test::AssertTrue# (narrow_as x bool))
    (let! z auto (narrow_as x (union [u8 bool]))))


(fun main [(param argc s32) (param argv (ptr (ptr u8)))] s32 :
    (do (test_tagged_union_basic []))
    (do (test_tagged_union_void []))
    (do (test_tagged_union_result []))
    (do (test_tagged_union_parameter []))
    (do (test_tagged_union_narrowto []))
    @doc "test end"
    (test::Success#)
    (return 0))
)

