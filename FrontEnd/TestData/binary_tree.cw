@doc "Binary Tree Example"
(module main [] :
(@wrapped type NoneType void)


@pub (global None auto (wrap void_val NoneType))


@pub (defrec BinaryTreeNode :
    (field left (union [NoneType (ptr! BinaryTreeNode)]))
    (field right (union [NoneType (ptr! BinaryTreeNode)]))
    (field payload u32))


(type MaybeNode (union [NoneType (ptr! BinaryTreeNode)]))


(type Visitor (sig [(param node (ptr! BinaryTreeNode))] void))


(fun InorderTraversal [(param root MaybeNode) (param visitor Visitor)] void :
    (trylet node (ptr! BinaryTreeNode) root _ : (return))
    (shed (InorderTraversal [(. (^ node) left) visitor]))
    (shed (visitor [node]))
    (shed (InorderTraversal [(. (^ node) right) visitor])))

)
