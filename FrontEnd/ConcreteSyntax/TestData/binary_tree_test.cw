-- Binary Tree Example
module:

import test

import fmt

fun lt(a ^u32, b ^u32) bool:
    return a^ < b^

import bt = "./binary_tree_gen"(u32, lt)

global N u32 = 64

global! NodePool = [N]bt::Node{}

global! NodePoolFreeIndex uint = 0

fun alloc(p u32) ^!bt::Node:
    let out = &!NodePool[NodePoolFreeIndex]
    set NodePoolFreeIndex += 1
    set out^.payload = p
    return out

fun reverse_bits(bits u32, width u32) u32:
    let! x u32 = bits
    let! out u32 = 0
    for i = 0, width, 1:
        set out <<= 1
        if x and 1 == 0:
            set out or= 1
        set x >>= 1
    return out

fun DumpNode(payload ^u32) void:
    fmt::print#(payload^, "\n")

@cdecl fun main(argc s32, argv ^^u8) s32:
    let! root bt::MaybeNode = bt::Leaf
    for i = 0, N, 1:
        let node = alloc(reverse_bits(i, 6))
        -- (fmt::print# "before insert " i "\n")
        let x = bt::Insert(root, node)
        set root = x
    do bt::InorderTraversal(root, DumpNode)
    test::Success#()
    return 0
