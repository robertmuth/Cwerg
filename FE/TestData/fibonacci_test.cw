; fibonacci
module:

import test

fun fib(x uint) uint:
    if x <= 1:
        return x
    return fib(x - 1) + fib(x - 2)

global expected = {[20]uint:
                   0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610,
                   987, 1597, 2584, 4181}

fun main(argc s32, argv ^^u8) s32:
    for i = 0, 20_uint, 1:
        test\AssertEq#(expected[i], fib(i))
    test\Success#()
    return 0
