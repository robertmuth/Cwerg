@doc "Binary Tree Example"
(module BinaryTree [
    @doc "the payload type"
    (modparam $type TYPE)
    @doc "the less-than function ($type x $type) -> bool"
    (modparam $lt CONST_EXPR)] :


@pub (global Leaf auto void_val)


@pub (defrec Node :
    (field left (union [void (ptr! Node)]))
    (field right (union [void (ptr! Node)]))
    (field payload $type))

@doc "same as above for left and right"
@pub (type MaybeNode (union [void (ptr! Node)]))


(type Visitor (sig [(param node (ptr $type))] void))


@pub (fun InorderTraversal [(param root MaybeNode) (param visitor Visitor)] void :
    (trylet node (ptr! Node) root _ :
        (return))
    (do (InorderTraversal [(^. node left) visitor]))
    (do (visitor [(& (^. node payload))]))
    (do (InorderTraversal [(^. node right) visitor])))

@doc "returns the new root"
@pub (fun Insert [(param root MaybeNode) (param node (ptr! Node))] (ptr! Node):
    (= (^. node left) Leaf)
    (= (^. node right) Leaf)
    (trylet curr (ptr! Node) root _ :
         (return node)
    )
    (if (call $lt [(& (^. node payload))  (&(^. curr payload))]) :
      (= (^. curr left) (Insert [(^. curr left) node]))
       :
      (= (^. curr right) (Insert [(^. curr right) node]))
    )
    (return curr)
)
)
