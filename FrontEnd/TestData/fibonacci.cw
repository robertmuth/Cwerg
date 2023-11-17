@doc "fizzbuzz"
(module main [] :
(import test)

(fun fib [(param x uint)] uint :
    (if (<= x 1) : (return x) :)
    (return (+
               (fib [(- x 1)])
               (fib [(- x 2)]))))

(global expected auto (array_val 20 uint [
    0
    1
    1
    2
    3
    5
    8
    13
    21
    34
    55
    89
    144
    233
    377
    610
    987
    1597
    2584
    4181]))


(fun @cdecl main [(param argc s32) (param argv (ptr (ptr u8)))] s32 :
    (for i 0 20_uint 1 :
        (test::AssertEq! (at expected i) (fib [i]))
    )
    (test::Success!)
    (return 0))

)
