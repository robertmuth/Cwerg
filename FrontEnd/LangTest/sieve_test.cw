@doc "prime number sieve"
(module [] :
(import test)


(global SIZE uint 1000000)


(global EXPECTED uint 148932)


@doc """The array is initialized to all true because the explicit
value for the first element is replicated for the
subsequent unspecified ones.

index i reprents number 3 + 2 * i"""
(global! is_prime auto (array_val SIZE bool [true]))


@doc "the actual sieve function"
(fun sieve [] uint :
    (let! count uint 0)
    (for i 0 SIZE 1 :
        (if (at is_prime i) :
            (+= count 1)
            (let p uint (+ (+ i i) 3))
            (for k (+ i p) SIZE p :
                (= (at is_prime k) false))
         :))
    (return count))


@cdecl (fun main [(param argc s32) (param argv (ptr (ptr u8)))] s32 :
    (test::AssertEq# (sieve []) EXPECTED)
    (test::Success#)
    (return 0))
)