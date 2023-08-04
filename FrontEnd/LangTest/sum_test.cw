@doc  "union"
(module main [] :
(import test)

(type UntaggedUnion (union @untagged [bool u64 u32 r32 r64 (array 32 u8)]))
(type TaggedUnion (union [bool u64 u32 r32 r64 (array 32 u8)]))

(static_assert (== (sizeof UntaggedUnion) 32))


(fun test_untagged_union [] void :
    @doc """(let @mut u4 TaggedUnion 777_u32)"""
    (let @mut u1 UntaggedUnion auto_val)
    (let @mut u2 UntaggedUnion undef)
    (let @mut u3 UntaggedUnion 2.0_r32)

    (let s1 u32 (as u3 u32))
    (test::AssertEq s1 0x40000000_u32)
    (test::AssertEq (at (as u3 (array 32 u8)) 0) 0_u8)
    (test::AssertEq (at (as u3 (array 32 u8)) 1) 0_u8)
    (test::AssertEq (at (as u3 (array 32 u8)) 2) 0_u8)
    (test::AssertEq (at (as u3 (array 32 u8)) 3) 0x40_u8)

    (= u3 2.0_r64)
    (test::AssertEq (as u3 u64) 0x4000000000000000_u64)
    (test::AssertEq (at (as u3 (array 32 u8)) 3) 0_u8)
    (test::AssertEq (at (as u3 (array 32 u8)) 7) 0x40_u8)
)


(fun main [(param argc s32) (param argv (ptr (ptr u8)))] s32 :
    (stmt (call test_untagged_union []))

    @doc "test end"
    (stmt (call SysPrint ["OK\n"]))
    (return 0))

)