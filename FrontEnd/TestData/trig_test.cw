(module main [] :
(import trig)
(import test)

(global EPSILON r64 0.000000000001)
(fun main [(param argc s32) (param argv (ptr (ptr u8)))] s32 :
    (test::AssertApproxEq 1_r64 1.0_r64 EPSILON)
    (return 0))

(# "eom"))