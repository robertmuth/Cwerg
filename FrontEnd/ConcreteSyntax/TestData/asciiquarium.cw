-- main module with program entry point `main`
module main:

import artwork = "./ascii_artwork"

import aanim = "./ascii_anim"

import ansi

import os

import fmt

global! all_objects = [100]aanim::ObjectState{}

@cdecl fun main(argc s32, argv ^^u8) s32:
    if argc < 3:
        fmt::print#("Not enough arguments, need width and height\n")
        return 0
    let arg_w slice(u8) = fmt::strz_to_slice(pinc(argv, 1)^)
    let arg_h slice(u8) = fmt::strz_to_slice(pinc(argv, 2)^)
    let width s32 = as(fmt::str_to_u32(arg_w), s32)
    let height s32 = as(fmt::str_to_u32(arg_h), s32)
    -- 100ms per frame
    @ref let req os::TimeSpec = os::TimeSpec{0, 100000000}
    @ref let! rem os::TimeSpec = undef
    @ref let! window = aanim::Window{width, height, undef, undef, undef}
    let! curr = front!(all_objects)
    -- add obj
    shed aanim::InitObjectState(curr, &artwork::DuckR)
    shed aanim::SetBasics(curr, 0.0, 0, 5)
    set curr = pinc(curr, 1)
    -- add obj
    shed aanim::InitObjectState(curr, &artwork::Castle)
    shed aanim::SetBasics(curr, 0.0, as(width, r32) - 32, as(height, r32) - 13)
    set curr = pinc(curr, 1)
    -- add obj
    shed aanim::InitObjectState(curr, &artwork::BigFishR)
    shed aanim::SetBasics(curr, 0.0, 10, 10)
    set curr = pinc(curr, 1)
    -- add obj
    shed aanim::InitObjectState(curr, &artwork::SwanL)
    shed aanim::SetBasics(curr, 0.0, 50, 1)
    set curr = pinc(curr, 1)
    -- add obj
    shed aanim::InitObjectState(curr, &artwork::DolphinL)
    shed aanim::SetBasics(curr, 0.0, 30, 8)
    set curr = pinc(curr, 1)
    -- add obj
    shed aanim::InitObjectState(curr, &artwork::MonsterR)
    shed aanim::SetBasics(curr, 0.0, 30, 2)
    set curr = pinc(curr, 1)
    -- add obj
    shed aanim::InitObjectState(curr, &artwork::SharkR)
    shed aanim::SetBasics(curr, 0.0, 30, 30)
    set curr = pinc(curr, 1)
    -- add obj
    shed aanim::InitObjectState(curr, &artwork::ShipR)
    shed aanim::SetBasics(curr, 0.0, 50, 0)
    set curr = pinc(curr, 1)
    -- add obj
    shed aanim::InitObjectState(curr, &artwork::Fish1R)
    shed aanim::SetBasics(curr, 0.0, 40, 40)
    set curr = pinc(curr, 1)
    -- add obj
    fmt::print#(ansi::CURSOR_HIDE)
    let! last_t r32 = 0.0
    for t = 0.0, 5.0_r32, 0.1:
        shed aanim::window_fill(&!window, ' ', ' ')
        set curr = front!(all_objects)
        for i = 0, 9_uint, 1:
            shed aanim::draw(&!window, pinc(curr, i))
        shed aanim::window_draw(&window, 'k')
        for i = 0, 9_uint, 1:
            shed artwork::UpdateState(pinc(curr, i), t, t - last_t)
        shed os::nanosleep(&req, &!rem)
        set last_t = t
    fmt::print#(ansi::CURSOR_SHOW)
    return 0
