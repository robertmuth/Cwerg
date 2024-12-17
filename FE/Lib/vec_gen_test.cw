module:

import fmt
import string
import parse_real
import random
import test

import v64 = vec_gen(r64)


fun Test_Dim2() void:
    test::AssertTrue#(
        v64::eq@(v64::ID_mat2, {v64::mat2: v64::X_vec2, v64::Y_vec2}))
    test::AssertTrue#(
        v64::eq@(v64::ONES_vec2, v64::add@(v64::X_vec2, v64::Y_vec2)))


fun main(argc s32, argv ^^u8) s32:
    do Test_Dim2()
    -- test end
    test::Success#()
    return 0