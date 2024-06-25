@doc "defer"
(module [] :
(import test)


(global! gIndex uint 0)


(global! gSequence auto (array_val 10 u8 [0]))


(fun store [(param c u8)] void :
    (= (at gSequence gIndex) c)
    (+= gIndex 1))


(fun foo [] void :
    (defer :
        (do (store ['h'])))
    (defer :
        (do (store ['g'])))
    (do (store ['a']))
    (block _ :
        (do (store ['b']))
        (defer :
            (do (store ['e'])))
        (defer :
            (do (store ['d'])))
        (do (store ['c'])))
    (do (store ['f'])))


@cdecl (fun main [(param argc s32) (param argv (ptr (ptr u8)))] s32 :
    (do (foo []))
    (test::AssertSliceEq# (slice_val (front gSequence) gIndex) "abcdefgh")
    @doc "test end"
    (test::Success#)
    (return 0))
)

