@doc "Linked List Example"
(module main [] :

(type @wrapped NoneType void)


(global @pub None auto (wrap void_val NoneType))


(defrec @pub LinkedListNode :
    (field next (union [NoneType (ptr @mut LinkedListNode)]))
    (field payload u32))


(type MaybeNode (union [NoneType (ptr @mut LinkedListNode)]))


(fun SumPayload [(param root MaybeNode)] u32 :
    (let @mut sum u32 0)
    (let @mut node auto root)
    (while true :
        (trylet x (ptr @mut LinkedListNode) node _ : (break))
        (+= sum (. (^ x) payload))
        (= node (. (^ x) next)))
    (return sum))

)
