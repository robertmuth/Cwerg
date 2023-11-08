(module main [] :
(import test)
(import flate)

(fun @cdecl main [(param argc s32) (param argv (ptr (ptr u8)))] s32 :
    @doc "test end"
    (test::Success!)
    (return 0))
)
