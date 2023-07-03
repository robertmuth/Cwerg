(module main [] :
(# "main module with program entry point `main`")
(fun main [(param argc s32) (param argv (ptr (ptr u8)))] s32 :
    (print ["""hello world
    
    line 1
    line 2
"""])
    (return 0))

)


