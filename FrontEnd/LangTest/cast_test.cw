(module [] :

(fun fun1 [
        (param a s32)
        (param b u32)
        (param c r32)] u8 :
    (let x s8 (as a s8))
    (let y auto (as c r64))
    (let z s32 (bitwise_as c s32))
    (return 66))

@doc "just a compilation test"
(fun main [(param argc s32) (param argv (ptr (ptr u8)))] s32 :
   (return 0))
)
