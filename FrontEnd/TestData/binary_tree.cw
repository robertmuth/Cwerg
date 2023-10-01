@doc "Binary Tree Example"
(module main [] :
(type @wrapped NoneType void)


(global @pub None auto (wrap void_val NoneType))


(defrec @pub BinaryTreeNode :
    (field left (union [NoneType (ptr @mut BinaryTreeNode)]))
    (field right (union [NoneType (ptr @mut BinaryTreeNode)]))
    (field payload u32))


(type MaybeNode (union [NoneType (ptr @mut BinaryTreeNode)]))


(type Visitor (sig [(param node (ptr @mut BinaryTreeNode))] void))


(fun InorderTraversal [(param root MaybeNode) (param visitor Visitor)] void :
    (try node (ptr @mut BinaryTreeNode) root _ : (return))
    (stmt (InorderTraversal [(. (^ node) left) visitor]))
    (stmt (visitor [node]))
    (stmt (InorderTraversal [(. (^ node) right) visitor])))

)
