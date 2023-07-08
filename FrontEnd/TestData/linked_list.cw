(module main [] :
(# "Linked List Example")
(type wrapped NoneType void)


(global pub None auto (as void_val NoneType))


(defrec pub LinkedListNode :
    (# "this is a comment with \" with quotes \t ")
    (field next (union [NoneType (ptr mut LinkedListNode)]))
    (field payload u32))


(type MaybeNode (union [NoneType (ptr mut LinkedListNode)]))


(fun SumPayload [(param root MaybeNode)] u32 :
    (let mut sum u32 0)
    (let mut node auto root)
    (while true :
        (try x (ptr mut LinkedListNode) node _ [(break)])
        (+= sum (. (^ x) payload))
        (= node (. (^ x) next)))
    (return sum))

)


