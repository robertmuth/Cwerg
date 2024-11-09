-- prime number sieve
module:

import test

global SIZE uint = 1000000

global EXPECTED uint = 148932

-- The array is initialized to all true because the explicit
-- value for the first element is replicated for the
-- subsequent unspecified ones.
--
-- index i reprents number 3 + 2 * i
global! is_prime = {[SIZE]bool : true}

-- the actual sieve function
fun sieve() uint:
    -- mutable local variable
    let! count uint = 0
    -- the type of loop variable `i`  is determined by `N`
    for i = 0, SIZE, 1:
        if is_prime[i]:
            set count += 1
            let p uint = i + i + 3
            for k = i + p, SIZE, p:
                set is_prime[k] = false
    return count

fun main(argc s32, argv ^^u8) s32:
    test::AssertEq#(sieve(), EXPECTED)
    test::Success#()
    return 0
