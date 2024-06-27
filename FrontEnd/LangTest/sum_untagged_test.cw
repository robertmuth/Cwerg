@doc "union"
(module [] :
(import test)


(@wrapped type t1 s32)


(@wrapped type t2 void)


(@wrapped type t3 void)


(type type_ptr (ptr! s32))


(type UntaggedUnion1 (@untagged union [s32 void type_ptr]))


(static_assert (== (sizeof UntaggedUnion1) 8))


(type UntaggedUnion2 (@untagged union [s32 void (@untagged union [UntaggedUnion1 u8])]))


(static_assert (== (sizeof UntaggedUnion2) 8))


(type UntaggedUnion3 (@untagged union [bool s32 s64]))


(static_assert (== (sizeof UntaggedUnion2) 8))


(type UntaggedUnion4 (@untagged union [bool s32]))


(static_assert (== (sizeof UntaggedUnion4) 4))


@pub (type UntaggedUnion5 (@untagged union [t2 t3 s8]))


(static_assert (== (sizeof UntaggedUnion5) 1))


(type UntaggedUnion6 (@untagged union [bool u16]))


(static_assert (== (sizeof UntaggedUnion6) 2))


(type UntaggedUnion (@untagged union [
        bool
        u64
        u32
        r32
        r64
        (array 32 u8)]))


(type TaggedUnion (union [
        bool
        u64
        u32
        r32
        r64
        (array 32 u8)]))


(static_assert (== (sizeof UntaggedUnion) 32))


(defrec RecordWithUntaggedUnion :
    (field t1 bool)
    (field t2 u32)
    (field t3 UntaggedUnion)
    (field t4 bool))


(fun with_union_result [
        (param a bool)
        (param b u32)
        (param c r32)] UntaggedUnion :
    (let! out UntaggedUnion undef)
    (if a :
        (= out b)
     :
        (= out c))
    (return out))


(fun test_untagged_union [] void :
    @doc "straight up union"
    (let! u1 UntaggedUnion)
    (let! u2 UntaggedUnion undef)
    (let! u3 UntaggedUnion 2.0_r32)
    (let! u4 UntaggedUnion 777_u32)
    (let s1 u32 (narrow_as u3 u32))
    (test::AssertEq# s1 0x40000000_u32)
    (test::AssertEq# (at (narrow_as u3 (array 32 u8)) 0) 0_u8)
    (test::AssertEq# (at (narrow_as u3 (array 32 u8)) 1) 0_u8)
    (test::AssertEq# (at (narrow_as u3 (array 32 u8)) 2) 0_u8)
    (test::AssertEq# (at (narrow_as u3 (array 32 u8)) 3) 0x40_u8)
    (= (at (narrow_as u3 (array 32 u8)) 2) 0x28_u8)
    (= (at (narrow_as u3 (array 32 u8)) 3) 0x42_u8)
    (test::AssertEq# (narrow_as u3 u32) 0x42280000_u32)
    (test::AssertEq# (narrow_as u3 r32) 42_r32)
    (= u3 2.0_r64)
    (test::AssertEq# (narrow_as u3 u64) 0x4000000000000000_u64)
    (test::AssertEq# (at (narrow_as u3 (array 32 u8)) 3) 0_u8)
    (test::AssertEq# (at (narrow_as u3 (array 32 u8)) 7) 0x40_u8)
    @doc "union embedded in record"
    (let! rec1 RecordWithUntaggedUnion undef)
    (= (. rec1 t3) 2.0_r32)
    (test::AssertEq# (narrow_as (. rec1 t3) u32) 0x40000000_u32)
    (test::AssertEq# (at (narrow_as (. rec1 t3) (array 32 u8)) 0) 0_u8)
    (test::AssertEq# (at (narrow_as (. rec1 t3) (array 32 u8)) 1) 0_u8)
    (test::AssertEq# (at (narrow_as (. rec1 t3) (array 32 u8)) 2) 0_u8)
    (test::AssertEq# (at (narrow_as (. rec1 t3) (array 32 u8)) 3) 0x40_u8)
    @doc "union embedded in record 2"
    (let! rec2 auto (rec_val RecordWithUntaggedUnion [false 0x12344321 2.0_r32 true]))
    (test::AssertEq# (. rec2 t1) false)
    (test::AssertEq# (. rec2 t2) 0x12344321_u32)
    (test::AssertEq# (narrow_as (. rec2 t3) u32) 0x40000000_u32)
    (test::AssertEq# (. rec2 t4) true)
    @doc ""
    (= (at (narrow_as (. rec1 t3) (array 32 u8)) 2) 0x28_u8)
    (= (at (narrow_as (. rec1 t3) (array 32 u8)) 3) 0x42_u8)
    (test::AssertEq# (narrow_as (. rec1 t3) u32) 0x42280000_u32)
    (test::AssertEq# (narrow_as (. rec1 t3) r32) 42_r32)
    (= (. rec1 t3) 2.0_r64)
    (test::AssertEq# (narrow_as (. rec1 t3) u64) 0x4000000000000000_u64)
    (test::AssertEq# (at (narrow_as (. rec1 t3) (array 32 u8)) 3) 0_u8)
    (test::AssertEq# (at (narrow_as (. rec1 t3) (array 32 u8)) 7) 0x40_u8)
    @doc "array of union"
    (let! array1 (array 16 UntaggedUnion) undef)
    (= (at array1 13) 2.0_r32)
    (test::AssertEq# (narrow_as (at array1 13) u32) 0x40000000_u32)
    (test::AssertEq# (at (narrow_as (at array1 13) (array 32 u8)) 0) 0_u8)
    (test::AssertEq# (at (narrow_as (at array1 13) (array 32 u8)) 1) 0_u8)
    (test::AssertEq# (at (narrow_as (at array1 13) (array 32 u8)) 2) 0_u8)
    (test::AssertEq# (at (narrow_as (at array1 13) (array 32 u8)) 3) 0x40_u8)
    (= (at (narrow_as (at array1 13) (array 32 u8)) 2) 0x28_u8)
    (= (at (narrow_as (at array1 13) (array 32 u8)) 3) 0x42_u8)
    (test::AssertEq# (narrow_as (at array1 13) u32) 0x42280000_u32)
    (test::AssertEq# (narrow_as (at array1 13) r32) 42_r32)
    (= u1 (with_union_result [true 10 2.0]))
    (test::AssertEq# (narrow_as u1 u32) 10_u32)
    (= u1 (with_union_result [false 10 2.0]))
    (test::AssertEq# (narrow_as u1 u32) 0x40000000_u32)
    (= (at array1 13) 2.0_r64)
    (test::AssertEq# (narrow_as (at array1 13) u64) 0x4000000000000000_u64)
    (test::AssertEq# (at (narrow_as (at array1 13) (array 32 u8)) 3) 0_u8)
    (test::AssertEq# (at (narrow_as (at array1 13) (array 32 u8)) 7) 0x40_u8))


@cdecl (fun main [(param argc s32) (param argv (ptr (ptr u8)))] s32 :
    (do (test_untagged_union []))
    @doc "test end"
    (test::Success#)
    (return 0))
)

