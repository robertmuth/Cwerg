-- main module with program entry point `main`
module:

import artwork = "./ascii_artwork"

import aanim = "./ascii_anim"

import ansi

import os

import fmt

global! all_objects = {[100]aanim::ObjectState:}

fun main(argc s32, argv ^^u8) s32:
    if argc < 3:
        fmt::print#("Not enough arguments, need width and height\n")
        return 0
    let arg_w span(u8) = fmt::strz_to_slice(ptr_inc(argv, 1)^)
    let arg_h span(u8) = fmt::strz_to_slice(ptr_inc(argv, 2)^)
    let width s32 = as(fmt::str_to_u32(arg_w), s32)
    let height s32 = as(fmt::str_to_u32(arg_h), s32)
    -- 100ms per frame
    ref let req = {os::TimeSpec: 0, 100000000}
    ref let! rem os::TimeSpec = undef
    ref let! window = {aanim::Window: width, height, undef, undef, undef}
    let! curr = front!(all_objects)
    -- add obj
    do aanim::InitObjectState(curr, &artwork::DuckR)
    do aanim::SetBasics(curr, 0.0, 0, 5)
    set curr = ptr_inc(curr, 1)
    -- add obj
    do aanim::InitObjectState(curr, &artwork::Castle)
    do aanim::SetBasics(curr, 0.0, as(width, r32) - 32, as(height, r32) - 13)
    set curr = ptr_inc(curr, 1)
    -- add obj
    do aanim::InitObjectState(curr, &artwork::BigFishR)
    do aanim::SetBasics(curr, 0.0, 10, 10)
    set curr = ptr_inc(curr, 1)
    -- add obj
    do aanim::InitObjectState(curr, &artwork::SwanL)
    do aanim::SetBasics(curr, 0.0, 50, 1)
    set curr = ptr_inc(curr, 1)
    -- add obj
    do aanim::InitObjectState(curr, &artwork::DolphinL)
    do aanim::SetBasics(curr, 0.0, 30, 8)
    set curr = ptr_inc(curr, 1)
    -- add obj
    do aanim::InitObjectState(curr, &artwork::MonsterR)
    do aanim::SetBasics(curr, 0.0, 30, 2)
    set curr = ptr_inc(curr, 1)
    -- add obj
    do aanim::InitObjectState(curr, &artwork::SharkR)
    do aanim::SetBasics(curr, 0.0, 30, 30)
    set curr = ptr_inc(curr, 1)
    -- add obj
    do aanim::InitObjectState(curr, &artwork::ShipR)
    do aanim::SetBasics(curr, 0.0, 50, 0)
    set curr = ptr_inc(curr, 1)
    -- add obj
    do aanim::InitObjectState(curr, &artwork::Fish1R)
    do aanim::SetBasics(curr, 0.0, 40, 40)
    set curr = ptr_inc(curr, 1)
    -- add obj
    fmt::print#(ansi::CURSOR_HIDE)
    let! last_t r32 = 0.0
    for t = 0.0, 5.0_r32, 0.1:
        do aanim::window_fill(&!window, ' ', ' ')
        set curr = front!(all_objects)
        for i = 0, 9_uint, 1:
            do aanim::draw(&!window, ptr_inc(curr, i))
        do aanim::window_draw(&window, 'k')
        for i = 0, 9_uint, 1:
            do artwork::UpdateState(ptr_inc(curr, i), t, t - last_t)
        do os::nanosleep(&req, &!rem)
        set last_t = t
    fmt::print#(ansi::CURSOR_SHOW)
    return 0
