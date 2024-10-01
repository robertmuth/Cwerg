@doc "Binary Tree Example"
(module [] :
(import test)

(import fmt)


(fun lt [(param a (ptr u32)) (param b (ptr u32))] bool :
    (return (< (^ a) (^ b))))

(import bt ./binary_tree_gen [u32 lt])


(global N u32 64)


(global! NodePool auto (vec_val N bt::Node))


(global! NodePoolFreeIndex uint 0)


(fun alloc [(param p u32)] (ptr! bt::Node) :
    (let out auto (&! (at NodePool NodePoolFreeIndex)))
    (+= NodePoolFreeIndex 1)
    (= (^. out payload) p)
    (return out))


(fun reverse_bits [(param bits u32) (param width u32)] u32 :
    (let! x u32 bits)
    (let! out u32 0)
    (for i 0 width 1 :
        (<<= out 1)
        (if (== (and x 1) 0) :
            (or= out 1)
         :)
        (>>= x 1))
    (return out))


(fun DumpNode [(param payload (ptr u32))] void :
    (fmt::print# (^ payload) "\n"))


(fun main [(param argc s32) (param argv (ptr (ptr u8)))] s32 :
    (let! root bt::MaybeNode bt::Leaf)
    (for i 0 N 1 :
        (let node auto (alloc [(reverse_bits [i 6])]))
        @doc """(fmt::print# "before insert " i "\n")"""
        (let x auto (bt::Insert [root node]))
        (= root x))
    (do (bt::InorderTraversal [root DumpNode]))
    (test::Success#)
    (return 0))
)

