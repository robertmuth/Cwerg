@doc "sieve"

(module main [] :
(import test)

(global SIZE uint 1000000)


(global EXPECTED uint 148932)


@doc "index i reprents number 3 + 2 * i"
(global @mut is_prime (array SIZE u8) (array_val SIZE u8 [(index_val 0 0)]))


(fun sieve [] uint :
    @doc "initially every number is assumed prime"
    (for i 0 SIZE 1 :
        (= (at is_prime i) 1))
    @doc "run the sieve"
    (let @mut count uint 0)
    (for i 0 SIZE 1 :
        (if (!= (at is_prime i) 0) :
            (= count (+ count 1))
            (let p uint (+ 3 (+ i i)))
            (for k (+ i p) SIZE p :
                (= (at is_prime k) 0))
            :))
    (return count))


(fun @cdecl main [(param argc s32) (param argv (ptr (ptr u8)))] s32 :
    (test::AssertEq (call sieve []) EXPECTED)
    (print ["OK\n"])
    (return 0))

)


