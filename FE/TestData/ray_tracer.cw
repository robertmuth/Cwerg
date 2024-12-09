-- simple ray tracer adapted from
-- https://github.com/jtsiomb/c-ray/blob/master/c-ray-f/c-ray-f.c
module:

import fmt

import vecx = vec_gen(r64)

fun main(argc s32, argv ^^u8) s32:
    -- if argc < 3:
    --     fmt::print#("Not enough arguments, need width and height\n")
    --     return 0
    -- let arg_w span(u8) = fmt::strz_to_slice(pinc(argv, 1)^)
    -- let arg_h span(u8) = fmt::strz_to_slice(pinc(argv, 2)^)
    -- let width u32 = fmt::str_to_u32(arg_w)
    -- let height u32 = fmt::str_to_u32(arg_h)
    let v1 = {vecx::vec3: 1.0, 2.0, 3.0}
    let v2 = {vecx::vec3: 1.0, 2.0, 3.0}

    fmt::print#(v1, "\n")
    fmt::print#(v2, "\n")
    fmt::print#(vecx::add@(v1, v2), "\n")

    return 0
