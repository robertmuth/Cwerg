(defmod main [] [
(# "Binary Tree Example")

(deftype wrapped NoneType void)
(const None auto (as void NoneType))

(defrec pub BinaryTreeNode [
   (field left (union [None (ptr mut BinaryTreeNode)]) None)
   (field right (union [None (ptr mut BinaryTreeNode)]) None)
   (field payload u32 0)
])

(deftype MaybeNode (union [None (ptr mut BinaryTreeNode)]))

(deftype Visitor (sig [(param node (ptr mut BinaryTreeNode))] void))

(defun InorderTraversal [(param root MaybeNode) (param visitor Visitor)] void [
    (try node (ptr mut BinaryTreeNode) root (catch _ [(return)]))
    (stmt (call InorderTraversal [(. (^ node) left) visitor]))
    (stmt (call visitor [node]))
    (stmt (call InorderTraversal [(. (^ node) right) visitor]))
])

])