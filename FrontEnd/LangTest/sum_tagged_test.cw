(module main [] :
(import test)

(@wrapped type t1 s32)
(@wrapped type t2 void)
(@wrapped type t3 void)
(type type_ptr (ptr! s32))


(type Union1 (union [ s32 void type_ptr ]))

(static_assert (== (sizeof Union1) 16))


(type Union2 (union [
        s32
        void
        (union  [Union1 u8])]))

(static_assert (== (sizeof Union2) 16))

(type Union2Simplified (union [s32 void u8 type_ptr]))

(static_assert (== (typeid Union2) (typeid Union2Simplified)))


(type Union3 (union [ bool u8 s32 s64 ]))

(static_assert (== (sizeof Union3) 16))



(type Delta1 (uniondelta Union3 (union [ bool u8 s32 ])))
(static_assert (== (sizeof Delta1) 8))
(static_assert (== (typeid Delta1) (typeid s64)))


(type Delta2 (uniondelta Union3 (union [ bool u8 ])))
(static_assert (== (typeid Delta2) (typeid (union [ s32 s64 ]))))

(type Delta3 (uniondelta Union3 (union [ bool u8 s64])))
(static_assert (== (typeid Delta3) (typeid s32)))

@pub (type Union5 (union [ t2 t3 s8 ]))

(static_assert (== (sizeof Union5) 3))


(type  Union6 (union [ bool u16 ]))

(static_assert (== (sizeof Union6) 4))



(type Union (union [bool u64 u32 r32 r64 (array 32 u8)]))

(static_assert (== (sizeof Union) 40))


(defrec rec1 :
    (field s1 Union5)
    (field s2 Union5))


@pub (defrec rec2 :
    (field s1 Union1)
    (field s2 Union2))


(global global_rec1  auto (rec_val rec1 [1_s8 2_s8]))

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
    (test::AssertTrue# (== 777_s32 y))
)



@pub (type UnionVoid (union [ void t2 t3 ]))

(fun test_tagged_union_void [] void :
  (let! x UnionVoid  void_val)
)

(fun fun_param [
        (param a bool)
        (param b bool)
        (param c s32)
        (param x Union3)] void :
    (if a :
         (test::AssertTrue# (is x bool))
    :
        (test::AssertTrue# (is x s32))
    ))

(fun test_tagged_union_parameter [] void :
    (let! x Union3 true)
    (shed (fun_param [true true 0 x]))
    (= x 666_s32)
    (shed (fun_param [false true 666 x]))
)

(fun fun_result [
        (param a bool)
        (param b bool)
        (param c s32)] Union3 :
    (let! out  Union3 undef)
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
    (test::AssertTrue# (is x s32))
)

(fun test_tagged_union_narrowto [] void :
    (let! x Union3 true)
    (let! y auto (narrowto x bool))
    (test::AssertTrue# y)

    (test::AssertTrue# (narrowto x bool))

    (let! z auto (narrowto x (union [ u8 bool ])))

)

@cdecl (fun main [(param argc s32) (param argv (ptr (ptr u8)))] s32 :
    (shed (test_tagged_union_basic []))
    (shed (test_tagged_union_void []))
    (shed (test_tagged_union_result []))
    (shed (test_tagged_union_parameter []))
    (shed (test_tagged_union_narrowto []))

    @doc "test end"
    (test::Success#)
    (return 0))

)
