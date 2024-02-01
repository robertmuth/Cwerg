@doc  "defer"
(module main [] :
(import test)


(global! gIndex uint 0)
(global! gSequence auto (array_val 10 u8 [(index_val 0)]))


(fun store [(param c u8)] void :
    (= (at gSequence gIndex) c)
    (+= gIndex 1)
)

(fun foo [] void :
    (defer :
        (shed (store ['h'])))
    (defer :
        (shed (store ['g'])))
    (shed (store ['a']))
    (block _ :
        (shed (store ['b']))
        (defer :
            (shed (store ['e'])))
        (defer :
            (shed (store ['d'])))
        (shed (store ['c'])))
    (shed (store ['f']))
)


@cdecl (fun main [(param argc s32) (param argv (ptr (ptr u8)))] s32 :
    (shed (foo []))
    (test::AssertSliceEq# (slice_val (front gSequence) gIndex) "abcdefgh")
    @doc "test end"
    (test::Success#)
    (return 0))
)
