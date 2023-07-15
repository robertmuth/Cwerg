(module main [] :
(import math)
(import trig)
(import test)

(# """
      0    30=pi/6     45=pi/4    60=pi/3    90=pi/2 
sin   0    1/2         sqrt(2)/2  sqrt(3)/2  1
cos   1    sqrt(3)/2   sqrt(2)/2  1/2        0
""")
(global EPSILON r64 0.0000001)

(fun main [(param argc s32) (param argv (ptr (ptr u8)))] s32 :
    (test::AssertApproxEq (call trig::sin_restricted [0.0 0.0 true]) 0.0_r64 EPSILON)
    (test::AssertApproxEq (call trig::sin_restricted [(/ math::PI 6.0) 0.0 true]) 0.5_r64 EPSILON)
    (test::AssertApproxEq (call trig::sin_restricted [(/ math::PI 4.0) 0.0 true]) (/ math::SQRT_2 2) EPSILON)
    (test::AssertApproxEq (call trig::sin_restricted [(/ math::PI 3.0) 0.0 true]) (/ math::SQRT_3 2) EPSILON)
    (test::AssertApproxEq (call trig::sin_restricted [(/ math::PI 2.0) 0.0 true]) 1.0_r64 EPSILON)

    (test::AssertApproxEq (call trig::cos_restricted [0.0 0.0]) 1.0_r64 EPSILON)
    (test::AssertApproxEq (call trig::cos_restricted [(/ math::PI 6.0) 0.0]) (/ math::SQRT_3 2) EPSILON)
    (test::AssertApproxEq (call trig::cos_restricted [(/ math::PI 4.0) 0.0]) (/ math::SQRT_2 2) EPSILON)
    (test::AssertApproxEq (call trig::cos_restricted [(/ math::PI 3.0) 0.0]) 0.5_r64 EPSILON)
    (test::AssertApproxEq (call trig::cos_restricted [(/ math::PI 2.0) 0.0]) 0.0_r64 EPSILON)

    (return 0))

(# "eom"))