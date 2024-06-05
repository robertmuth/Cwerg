-- Binary Tree Example
module main:

@wrapped type NoneType = void

@pub global None = wrapas(void, NoneType)

@pub rec BinaryTreeNode:
    left union(NoneType, ^!BinaryTreeNode)
    right union(NoneType, ^!BinaryTreeNode)
    payload u32

type MaybeNode = union(NoneType, ^!BinaryTreeNode)

type Visitor = funtype(node ^!BinaryTreeNode) void

fun InorderTraversal(root MaybeNode, visitor Visitor) void:
    trylet node ^!BinaryTreeNode = root, _:
        return
    do InorderTraversal(node^.left, visitor)
    do visitor(node)
    do InorderTraversal(node^.right, visitor)
