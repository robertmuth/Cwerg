(module trig [] :
(# """
sin and cos

https://git.musl-libc.org/cgit/musl/tree/src/math/__cos.c
https://git.musl-libc.org/cgit/musl/tree/src/math/__sin.c
""")


(defrec pub SumCompensation :
    (field sum r64)
    (field compensation r64)
)

(global S1 r64 -0x1.5555555555549p-3)
(global S2 r64  0x1.111111110f8a6p-7)
(global S3 r64 -0x1.a01a019c161d5p-13)
(global S4 r64  0x1.71de357b1fe7dp-19)
(global S5 r64 -0x1.ae5e68a2b9cebp-26)
(global S6 r64  0x1.5d93a5acfd57cp-33)


(# " |x + y | <= pi / 4")
(fun sin_restricted [(param x r64) 
                   (param y r64) 
                   (param y_is_zero bool)] r64 : 
    (let x2 auto (* x x))
    (let x3 auto (* x2 x))
    (let x4 auto (* x2 x2))
    (let x5 auto (* x4 x))
    (let x6 auto (* x4 x2))

    (let s56 auto (* x6 (+ S5 (* x2 S6))))
    (let s34 auto (* x2 (+ S3 (* x2 S4))))
    (let s2_6 auto (+ (+ S2 s34) s56))
    (if y_is_zero :
        (let s1_6 auto (* x3 (+ S1 (* x2 s2_6))))
        (return (+ x s1_6))
    :
        (let t auto (- (* y 0.5) (* x3 s2_6)))
        (let t2 auto (- (* x2 t) y))

    )

)



(# "eom"))
