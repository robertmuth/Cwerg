(module main [] :
(# "main module with program entry point `main`")
(fun main [(param argc s32) (param argv (ptr (ptr u8)))] s32 :
    (print ["hello world\n"])
    (return 0))

)


