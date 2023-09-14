@doc "main module with program entry point `main`"

(module main [] :
(import fmt)

(fun strlen [(param s (ptr u8))] uint :
    (let @mut i uint 0)
    (while (!= (^ (incp s i)) 0) :
        (+= i 1))
    (return i))


(fun @cdecl main [(param argc s32) (param argv (ptr (ptr u8)))] s32 :
    (for i 0 (as argc u32) 1 :
        (let s (ptr u8) (^ (incp argv i)))
        (let t auto (slice_val s (strlen [s])))
        (fmt::print! [t "\n"]))
    (return 0))

)
