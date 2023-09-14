@doc  "defer"
(module main [] :
(import test)


(global @mut gIndex uint 0)
(global @mut gSequence auto (array_val 10 u8 [(index_val 0)]))


(fun store [(param c u8)] void :
    (= (at gSequence gIndex) c)
    (+= gIndex 1)
)

(fun foo [] void :
    (defer :
        (stmt (store ['h'])))
    (defer :
        (stmt (store ['g'])))
    (stmt (store ['a']))
    (block _ :
        (stmt (store ['b']))
        (defer :
            (stmt (store ['e'])))
        (defer :
            (stmt (store ['d'])))
        (stmt (store ['c'])))
    (stmt (store ['f']))
)


(fun @cdecl main [(param argc s32) (param argv (ptr (ptr u8)))] s32 :
    (stmt (foo []))
    (test::AssertSliceEq! (slice_val (front gSequence) gIndex) "abcdefgh")
    @doc "test end"
    (test::Success!)
    (return 0))
)
