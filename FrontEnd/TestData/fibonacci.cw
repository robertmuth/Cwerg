@doc "fizzbuzz"
(module main [] :
(import test)

(fun fib [(param x uint)] uint :
    (if (<= x 1) : (return x) :)
    (return (+
               (fib [(- x 1)])
               (fib [(- x 2)]))))

(global expected auto (array_val 20 uint [
    (index_val 0)
    (index_val 1)
    (index_val 1)
    (index_val 2)
    (index_val 3)
    (index_val 5)
    (index_val 8)
    (index_val 13)
    (index_val 21)
    (index_val 34)
    (index_val 55)
    (index_val 89)
    (index_val 144)
    (index_val 233)
    (index_val 377)
    (index_val 610)
    (index_val 987)
    (index_val 1597)
    (index_val 2584)
    (index_val 4181)]))


(fun @cdecl main [(param argc s32) (param argv (ptr (ptr u8)))] s32 :
    (for i 0 20_uint 1 :
        (test::AssertEq! (at expected i) (fib [i]))
    )
    (test::Success!)
    (return 0))

)
