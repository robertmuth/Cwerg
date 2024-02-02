@doc "Linked List Example"
(module main [] :

(@wrapped type NoneType void)


@pub (global None auto (wrap void_val NoneType))


@pub (defrec LinkedListNode :
    (field next (union [NoneType (ptr! LinkedListNode)]))
    (field payload u32))


(type MaybeNode (union [NoneType (ptr! LinkedListNode)]))


(fun SumPayload [(param root MaybeNode)] u32 :
    (let! sum u32 0)
    (let! node auto root)
    (while true :
        (trylet x (ptr! LinkedListNode) node _ : (break))
        (+= sum (. (^ x) payload))
        (= node (. (^ x) next)))
    (return sum))

)
