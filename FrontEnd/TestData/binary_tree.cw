(module main [] :
(# "Binary Tree Example")
(type wrapped NoneType void)


(global pub None auto (as void_val NoneType))


(defrec pub BinaryTreeNode :
    (field left (union [NoneType (ptr mut BinaryTreeNode)]))
    (field right (union [NoneType (ptr mut BinaryTreeNode)]))
    (field payload u32))


(type MaybeNode (union [NoneType (ptr mut BinaryTreeNode)]))


(type Visitor (sig [(param node (ptr mut BinaryTreeNode))] void))


(fun InorderTraversal [(param root MaybeNode) (param visitor Visitor)] void :
    (try node (ptr mut BinaryTreeNode) root _ [(return)])
    (stmt (call InorderTraversal [(. (^ node) left) visitor]))
    (stmt (call visitor [node]))
    (stmt (call InorderTraversal [(. (^ node) right) visitor])))

)


