(module m1 [] :

(fun fun1 [
        (param a s32)
        (param b u32)
        (param c r32)] u8 :
    (let x s8 (as a s8))
    (let y auto (as c r64))
    (let z s32 (bitcast c s32))
    (return 66))
)

