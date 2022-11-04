(defmod main [] [
(# "Binary Tree Example")

(deftype wrapped None void)

(defrec pub BinaryTreeNode [
   (field left (union [None (ptr mut BinaryTreeNode)]) None)
   (field right (union [None (ptr mut BinaryTreeNode)]) None)
   (field payload u32 0)
])

(deftype MaybeNode (union [None (ptr mut BinaryTreeNode)]))

(deftype Visitor (sig [(param node (ptr mut BinaryTreeNode))] void))

(defun InorderTraversal [(param root MaybeNode) (param visitor Visitor)] void [
    (try node (ptr mut BinaryTreeNode) root (catch _ [(return)]))
    (expr (call InorderTraversal [(. (^ node) left) visitor]))
    (expr (call visitor [node]))
    (expr (call InorderTraversal [(. (^ node) right) visitor]))
])

])