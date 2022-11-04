(defmod main [] [
(# "Linked List Example")

(deftype wrapped None void)

(defrec pub LinkedListNode [
   (# "this is a comment with \" with quotes \t ")
   (field next (union [None (ptr mut LinkedListNode)]) None)
   (field payload u32 0)
])

(deftype MaybeNode (union [None (ptr mut LinkedListNode)]))

(defun SumPayload [(param root MaybeNode)] u32 [
    (let mut sum u32 0)
    (let mut node auto root)
    (while true [
        (try x (ptr mut LinkedListNode) node (catch _ [(break)]))
        (+= sum (. (^ x) payload))
        (= node (. (^ x) next))
    ])
    (return sum)
])

])