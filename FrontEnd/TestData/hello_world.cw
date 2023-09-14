@doc "main module with program entry point `main`"
(module main [] :
(import fmt)
(fun @cdecl main [(param argc s32) (param argv (ptr (ptr u8)))] s32 :
    (fmt::print! ["""hello world

    line 1
    line 2
"""])
    (return 0))

)
