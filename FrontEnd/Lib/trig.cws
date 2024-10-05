@doc "trigonometric functions"
(module [] :

@doc "see https://git.musl-libc.org/cgit/musl/tree/src/math/__sin.c"
(global SIN1 r64 -0x1.5555555555549p-3)


(global SIN2 r64 0x1.111111110f8a6p-7)


(global SIN3 r64 -0x1.a01a019c161d5p-13)


(global SIN4 r64 0x1.71de357b1fe7dp-19)


(global SIN5 r64 -0x1.ae5e68a2b9cebp-26)


(global SIN6 r64 0x1.5d93a5acfd57cp-33)


@doc "| x + y | <= pi / 4"
@pub (fun sin_restricted [
        (param x r64)
        (param y r64)
        (param y_is_zero bool)] r64 :
    (let x2 auto (* x x))
    (let x3 auto (* x2 x))
    (let x4 auto (* x2 x2))
    (let x5 auto (* x4 x))
    (let x6 auto (* x4 x2))
    (let sin56 auto (* x6 (+ SIN5 (* x2 SIN6))))
    (let sin34 auto (* x2 (+ SIN3 (* x2 SIN4))))
    (let sin2_6 auto (+ (+ SIN2 sin34) sin56))
    (if y_is_zero :
        (let sin1_6 auto (* x3 (+ SIN1 (* x2 sin2_6))))
        (return (+ x sin1_6))
     :
        (let t auto (- (* y 0.5) (* x3 sin2_6)))
        (let t2 auto (- (* x2 t) y))
        (return (- x (- t2 (* x3 SIN1))))))


@doc "see https://git.musl-libc.org/cgit/musl/tree/src/math/__cos.c"
(global COS1 r64 0x1.555555555554cp-5)


(global COS2 r64 -0x1.6c16c16c15177p-10)


(global COS3 r64 0x1.a01a019cb1590p-16)


(global COS4 r64 -0x1.27e4f809c52adp-22)


(global COS5 r64 0x1.1ee9ebdb4b1c4p-29)


(global COS6 r64 0x1.8fae9be8838d4p-37)


@doc "| x + y | <= pi / 4"
@pub (fun cos_restricted [(param x r64) (param y r64)] r64 :
    (let x2 auto (* x x))
    (let x4 auto (* x2 x2))
    (let x8 auto (* x4 x4))
    (let cos456 auto (+ COS4 (* x2 (+ COS5 (* x2 COS6)))))
    (let cos123 auto (+ COS1 (* x2 (+ COS2 (* x2 COS3)))))
    (let r auto (+ (* x2 cos123) (* x8 cos456)))
    (let hz auto (* x2 0.5))
    (let w auto (- 1.0_r64 hz))
    (let w2 auto (- (- 1.0_r64 w) hz))
    (let r2 auto (- (* x2 r) (* x y)))
    (return (+ w (+ w2 r2))))
)

