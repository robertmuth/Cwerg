@doc  "union"
(module main [] :
(import test)

(type @wrapped t1 s32)
(type @wrapped t2 void)
(type @wrapped t3 void)
(type type_ptr (ptr @mut s32))


(type UntaggedUnion1 (union @untagged [
        s32
        void
        type_ptr]))

(static_assert (== (sizeof UntaggedUnion1) 8))


(type UntaggedUnion2 (union @untagged [
        s32
        void
        (union  @untagged [UntaggedUnion1 u8])]))

(static_assert (== (sizeof UntaggedUnion2) 8))


(type UntaggedUnion3 (union @untagged [
        bool
        s32
        s64]))

(static_assert (== (sizeof UntaggedUnion2) 8))


(type UntaggedUnion4 (union @untagged [bool s32]))

(static_assert (== (sizeof UntaggedUnion4) 4))


(type @pub UntaggedUnion5 (union @untagged [
        t2
        t3
        s8]))

(static_assert (== (sizeof UntaggedUnion5) 1))


(type  UntaggedUnion6 (union @untagged [bool u16]))

(static_assert (== (sizeof UntaggedUnion6) 2))



(type UntaggedUnion (union @untagged [bool u64 u32 r32 r64 (array 32 u8)]))
(type TaggedUnion (union [bool u64 u32 r32 r64 (array 32 u8)]))

(static_assert (== (sizeof UntaggedUnion) 32))

(defrec RecordWithUntaggedUnion :
    (field t1 bool)
    (field t2 u32)
    (field t3 UntaggedUnion)
    (field t4 bool))



(fun with_union_result [(param a bool) (param b u32) (param c r32)] UntaggedUnion :
    (let @mut out UntaggedUnion undef)
    (if a : 
        (= out b) 
        : (= out c))
    (return out)
)

(fun test_untagged_union [] void :
    @doc "straight up union"
    (let @mut u1 UntaggedUnion)
    (let @mut u2 UntaggedUnion undef)
    (let @mut u3 UntaggedUnion 2.0_r32)
    (let @mut u4 UntaggedUnion 777_u32)

    (let s1 u32 (as u3 u32))
    (test::AssertEq! s1 0x40000000_u32)
    (test::AssertEq! (at (as u3 (array 32 u8)) 0) 0_u8)
    (test::AssertEq! (at (as u3 (array 32 u8)) 1) 0_u8)
    (test::AssertEq! (at (as u3 (array 32 u8)) 2) 0_u8)
    (test::AssertEq! (at (as u3 (array 32 u8)) 3) 0x40_u8)

    (= (at (as u3 (array 32 u8)) 2) 0x28_u8)
    (= (at (as u3 (array 32 u8)) 3) 0x42_u8)
    (test::AssertEq! (as u3 u32) 0x42280000_u32)
    (test::AssertEq! (as u3 r32) 42_r32)

    (= u3 2.0_r64)
    (test::AssertEq! (as u3 u64) 0x4000000000000000_u64)
    (test::AssertEq! (at (as u3 (array 32 u8)) 3) 0_u8)
    (test::AssertEq! (at (as u3 (array 32 u8)) 7) 0x40_u8)

    @doc "union embedded in record"
    (let @mut rec1 RecordWithUntaggedUnion undef)
    (= (. rec1 t3) 2.0_r32)
    (test::AssertEq! (as (. rec1 t3) u32) 0x40000000_u32)
    (test::AssertEq! (at (as (. rec1 t3) (array 32 u8)) 0) 0_u8)
    (test::AssertEq! (at (as (. rec1 t3) (array 32 u8)) 1) 0_u8)
    (test::AssertEq! (at (as (. rec1 t3) (array 32 u8)) 2) 0_u8)
    (test::AssertEq! (at (as (. rec1 t3) (array 32 u8)) 3) 0x40_u8)
    
    @doc "union embedded in record 2"
    (let @mut rec2 auto (rec_val RecordWithUntaggedUnion [
        (field_val false)
        (field_val 0x12344321)
        (field_val 2.0_r32)
        (field_val true)]))
    (test::AssertEq! (. rec2 t1) false)
    (test::AssertEq! (. rec2 t2) 0x12344321_u32)
    (test::AssertEq! (as (. rec2 t3) u32) 0x40000000_u32)
    (test::AssertEq! (. rec2 t4) true)


    @doc ""
    (= (at (as (. rec1 t3) (array 32 u8)) 2) 0x28_u8)
    (= (at (as (. rec1 t3) (array 32 u8)) 3) 0x42_u8)
    (test::AssertEq! (as (. rec1 t3) u32) 0x42280000_u32)
    (test::AssertEq! (as (. rec1 t3) r32) 42_r32)

    (= (. rec1 t3) 2.0_r64)
    (test::AssertEq! (as (. rec1 t3) u64) 0x4000000000000000_u64)
    (test::AssertEq! (at (as (. rec1 t3) (array 32 u8)) 3) 0_u8)
    (test::AssertEq! (at (as (. rec1 t3) (array 32 u8)) 7) 0x40_u8)

    @doc "array of union"
    (let @mut array1 (array 16 UntaggedUnion) undef)
    (= (at array1 13) 2.0_r32)
    (test::AssertEq! (as (at array1 13) u32) 0x40000000_u32)
    (test::AssertEq! (at (as (at array1 13) (array 32 u8)) 0) 0_u8)
    (test::AssertEq! (at (as (at array1 13) (array 32 u8)) 1) 0_u8)
    (test::AssertEq! (at (as (at array1 13) (array 32 u8)) 2) 0_u8)
    (test::AssertEq! (at (as (at array1 13) (array 32 u8)) 3) 0x40_u8)

    (= (at (as (at array1 13) (array 32 u8)) 2) 0x28_u8)
    (= (at (as (at array1 13) (array 32 u8)) 3) 0x42_u8)
    (test::AssertEq! (as (at array1 13) u32) 0x42280000_u32)
    (test::AssertEq! (as (at array1 13) r32) 42_r32)

    (= u1 (with_union_result [true 10 2.0]))
    (test::AssertEq! (as u1 u32) 10_u32)
    (= u1 (with_union_result [false 10 2.0]))
    (test::AssertEq! (as u1 u32) 0x40000000_u32)

    (= (at array1 13) 2.0_r64)
    (test::AssertEq! (as (at array1 13) u64) 0x4000000000000000_u64)
    (test::AssertEq! (at (as (at array1 13) (array 32 u8)) 3) 0_u8)
    (test::AssertEq! (at (as (at array1 13) (array 32 u8)) 7) 0x40_u8)
)


(fun @cdecl main [(param argc s32) (param argv (ptr (ptr u8)))] s32 :
    (stmt (test_untagged_union []))

    @doc "test end"
    (test::Success!)
    (return 0))

)