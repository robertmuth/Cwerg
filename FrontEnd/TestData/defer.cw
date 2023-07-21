@doc  "defer"
(module main [] :
(fun main [(param argc s32) (param argv (ptr (ptr u8)))] s32 :
    (defer :
        (print ["defer fun 1\n"]))
    (defer :
        (print ["defer fun 2\n"]))
    (print ["fun start\n"])
    (block _ :
        (defer :
            (print ["defer block 1\n"]))
        (defer :
            (print ["defer block 2\n"]))
        (print ["block start\n"])
        (print ["block end\n"]))
    (print ["fun end\n"])
    (return 0))

)


