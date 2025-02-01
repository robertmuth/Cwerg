; Binary Tree Example
module(
        ; the payload type
        $type TYPE,
        ; the less-than function ($type x $type) -> bool
        $lt CONST_EXPR):

pub global Leaf = void_val

pub rec Node:
    left union(void, ^!Node)
    right union(void, ^!Node)
    payload $type

; same as above for left and right
pub type MaybeNode = union(void, ^!Node)

type Visitor = funtype(node ^$type) void

pub fun InorderTraversal(root MaybeNode, visitor Visitor) void:
    trylet node ^!Node = root, _:
        return
    do InorderTraversal(node^.left, visitor)
    do visitor(@node^.payload)
    do InorderTraversal(node^.right, visitor)

; returns the new root
pub fun Insert(root MaybeNode, node ^!Node) ^!Node:
    set node^.left = Leaf
    set node^.right = Leaf
    trylet curr ^!Node = root, _:
        return node
    if $lt(@node^.payload, @curr^.payload):
        set curr^.left = Insert(curr^.left, node)
    else:
        set curr^.right = Insert(curr^.right, node)
    return curr
