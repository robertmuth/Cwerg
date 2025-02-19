module:

import cmp

import math

import trig

import test

;
;       0    30=pi/6     45=pi/4    60=pi/3    90=pi/2
; sin   0    1/2         sqrt(2)/2  sqrt(3)/2  1
; cos   1    sqrt(3)/2   sqrt(2)/2  1/2        0
;
global REL_ERR r64 = 0.0000001

fun main(argc s32, argv ^^u8) s32:
    test::AssertGenericEq#({cmp::r64r: trig::sin_restricted(0.0, 0.0, true)},
                           {cmp::r64r: 0.0, REL_ERR})
    test::AssertGenericEq#(
                           {cmp::r64r: trig::sin_restricted(math::PI / 6.0, 0.0,
                                         true)}, {cmp::r64r: 0.5, REL_ERR})
    test::AssertGenericEq#(
                           {cmp::r64r: trig::sin_restricted(math::PI / 4.0, 0.0,
                                         true)},
                           {cmp::r64r: math::SQRT_2 / 2, REL_ERR})
    test::AssertGenericEq#(
                           {cmp::r64r: trig::sin_restricted(math::PI / 3.0, 0.0,
                                         true)},
                           {cmp::r64r: math::SQRT_3 / 2, REL_ERR})
    test::AssertGenericEq#(
                           {cmp::r64r: trig::sin_restricted(math::PI / 2.0, 0.0,
                                         true)}, {cmp::r64r: 1.0, REL_ERR})
    test::AssertGenericEq#({cmp::r64r: trig::cos_restricted(0.0, 0.0)},
                           {cmp::r64r: 1.0, REL_ERR})
    test::AssertGenericEq#(
                           {cmp::r64r: trig::cos_restricted(math::PI / 6.0, 0.0)
                            }, {cmp::r64r: math::SQRT_3 / 2, REL_ERR})
    test::AssertGenericEq#(
                           {cmp::r64r: trig::cos_restricted(math::PI / 4.0, 0.0)
                            }, {cmp::r64r: math::SQRT_2 / 2, REL_ERR})
    test::AssertGenericEq#(
                           {cmp::r64r: trig::cos_restricted(math::PI / 3.0, 0.0)
                            }, {cmp::r64r: 0.5, REL_ERR})
    test::AssertGenericEq#(
                           {cmp::r64r: trig::cos_restricted(math::PI / 2.0, 0.0)
                            }, {cmp::r64r: 0.0, REL_ERR})
    ; test end
    test::Success#()
    return 0
