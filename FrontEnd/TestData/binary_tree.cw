(defmod main [] [
(# "Binary Tree Example")

(type wrapped NoneType void)
(const None auto (as void_val NoneType))

(defrec pub BinaryTreeNode [
   (field left (union [None (ptr mut BinaryTreeNode)]) None)
   (field right (union [None (ptr mut BinaryTreeNode)]) None)
   (field payload u32 0)
])

(type MaybeNode (union [None (ptr mut BinaryTreeNode)]))

(type Visitor (sig [(param node (ptr mut BinaryTreeNode))] void))

(fun InorderTraversal [(param root MaybeNode) (param visitor Visitor)] void [
    (try node (ptr mut BinaryTreeNode) root _ [(return)])
    (stmt (call InorderTraversal [(. (^ node) left) visitor]))
    (stmt (call visitor [node]))
    (stmt (call InorderTraversal [(. (^ node) right) visitor]))
])

])