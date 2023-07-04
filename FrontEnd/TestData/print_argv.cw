(module main [] :
(# "main module with program entry point `main`")
(fun strlen [(param s (ptr u8))] uint :
    (let mut i uint 0)
    (while (!= (^ (incp s i undef)) 0) :
        (+= i 1))
    (return i))


(fun main [(param argc s32) (param argv (ptr (ptr u8)))] s32 :
    (for i u32 0 (as argc u32) 1 :
            (let s (ptr u8) (^ (incp argv i undef)))
            (let t auto (slice_val s (call strlen [s])))
            (print [t "\n"]))
    (return 0))

)


