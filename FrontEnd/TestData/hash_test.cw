@doc "hash_test"

(module main [] :
(import random)
(import fmt)


(fun hash_32 [(param xx (ptr u32))] u32 :
   (let x u32 (^ xx))
   (return (or (<< x 16_u32) (! x)))
)

(fun eq_32 [(param a (ptr u32)) (param b (ptr u32))] bool :
    (return (== (^ a) (^ b)))
)

(import hashtab32 hashtab [u32 u32 hash_32 eq_32])

(global SIZE u32 1024)

(global! meta auto (array_val SIZE u8 [0]))
(global! keys auto (array_val SIZE u32 [0]))
(global! vals auto (array_val SIZE u32 [0]))
(global ht auto (rec_val hashtab::HashTab32 [
    (front! meta) (front! keys) (front! vals) SIZE 0]))

)
