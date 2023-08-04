@doc  "expr"
(module main [] :
(import test)

(type UntaggedUnion (union @untagged [bool u64 u32 r32 r64 (array 32 u8)]))
(type TaggedUnion (union [bool u64 u32 r32 r64 (array 32 u8)]))

(static_assert (== (sizeof UntaggedUnion) 32))


(fun test_untagged_union [] void :
    @doc """(let @mut u4 TaggedUnion 777_u32)"""
    (let @mut u1 UntaggedUnion auto_val)
    (let @mut u2 UntaggedUnion undef)
    (let @mut u3 UntaggedUnion 666_u32)

)


(fun main [(param argc s32) (param argv (ptr (ptr u8)))] s32 :
    (stmt (call test_untagged_union []))

    @doc "test end"
    (stmt (call SysPrint ["OK\n"]))
    (return 0))


)