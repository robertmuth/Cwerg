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
        (stmt (call store ['h'])))
    (defer :
        (stmt (call store ['g'])))
    (stmt (call store ['a']))
    (block _ :
        (stmt (call store ['b']))
        (defer :
            (stmt (call store ['e'])))
        (defer :
            (stmt (call store ['d'])))
        (stmt (call store ['c'])))
    (stmt (call store ['f']))
)


(fun @cdecl main [(param argc s32) (param argv (ptr (ptr u8)))] s32 :
    (stmt (call foo []))
    (test::AssertSliceEq (slice_val (front gSequence) gIndex) "abcdefgh")
    @doc "test end"
    (test::SysPrint ["OK\n"])
    (return 0))
)


