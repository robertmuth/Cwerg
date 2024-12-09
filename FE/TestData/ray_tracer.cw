-- simple ray tracer adapted from
-- https://github.com/jtsiomb/c-ray/blob/master/c-ray-f/c-ray-f.c
module:

import fmt

import v64 = vec_gen(r64)

fun main(argc s32, argv ^^u8) s32:
    -- if argc < 3:
    --     fmt::print#("Not enough arguments, need width and height\n")
    --     return 0
    -- let arg_w span(u8) = fmt::strz_to_slice(pinc(argv, 1)^)
    -- let arg_h span(u8) = fmt::strz_to_slice(pinc(argv, 2)^)
    -- let width u32 = fmt::str_to_u32(arg_w)
    -- let height u32 = fmt::str_to_u32(arg_h)
    let v1 v64::vec3 = {: 1.0, 2.0, 3.0}
    let v2 v64::vec3 = {: 1.0, 2.0, 3.0}
    let m1 v64::mat3 = {: {: 1.0, 0.0, 0.0},
                          {: 0.0, 1.0, 0.0},
                          {: 0.0, 0.0, 1.0} }
    fmt::print#(v1, "\n")
    fmt::print#(v2, "\n")
    fmt::print#(v64::zero_vec4, "\n")
    fmt::print#(v64::add@(v1, v2), "\n")

    return 0
