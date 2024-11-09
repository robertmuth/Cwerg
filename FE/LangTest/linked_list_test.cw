-- Linked List Example
module:

import test

import fmt

wrapped type NoneType = void

pub global None = wrap_as(void, NoneType)

pub rec LinkedListNode:
    next union(NoneType, ^!LinkedListNode)
    payload u32

type MaybeNode = union(NoneType, ^!LinkedListNode)

fun SumPayload(root MaybeNode) u32:
    let! sum u32 = 0
    let! node MaybeNode = root
    while true:
        trylet x ^!LinkedListNode = node, _:
            break
        set sum += x^.payload
        set node = x^.next
    return sum

global N uint = 100

global! NodePool = {[N]LinkedListNode :}

-- currently (* N 24) but should be (* N 16) on 64 bit system with union optimization
static_assert size_of(type_of(NodePool)) == N * 3 * size_of(^!LinkedListNode)

fun DumpNode(i u32) void:
    fmt::print#(i, " ", NodePool[i].payload, " ", union_tag(NodePool[i].next))
    if is(NodePool[i].next, NoneType):
        fmt::print#(" next: NULL\n")
    else:
        fmt::print#(
                " next: ",
                unsafe_as(narrow_as(NodePool[i].next, ^!LinkedListNode), ^void),
                "\n")

fun main(argc s32, argv ^^u8) s32:
    fmt::print#("start: ", unsafe_as(front(NodePool), ^void), "\n")
    for i = 0, N, 1:
        set NodePool[i].payload = as(i, u32)
        if i == N - 1:
            set NodePool[i].next = None
        else:
            set NodePool[i].next = &!NodePool[i + 1]
    --
    --     (for i 0 N 1 :
    --        (do (DumpNode [i])))
    --     
    test::AssertEq#(SumPayload(front!(NodePool)), 4950_u32)
    test::Success#()
    return 0
