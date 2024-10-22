-- bounce benchmark adapted from https://github.com/smarr/are-we-fast-yet/
module:

import test

global RANDOM_SEED = 74755_s32


global! rng_state = RANDOM_SEED

fun RngReset() void:
    set rng_state = RANDOM_SEED


fun RngNext() s32:
    set rng_state = ((rng_state * 1309) + 13849) and 65535
    return rng_state


global X_LIMIT = 500_s32
global Y_LIMIT = 500_s32
global NUM_BALLS = 100_u32
global NUM_ITERS = 50_u32

rec Ball:
    x s32
    y s32
    xVel s32
    yVel s32


fun BallInit(b ^!Ball) void:
    set b^.x = RngNext() % X_LIMIT
    set b^.y = RngNext() % Y_LIMIT
    set b^.xVel = RngNext() % 300 - 150
    set b^.yVel = RngNext() % 300 - 150
    -- fmt::print#(b^.x, " ",b^.y, "  ", b^.xVel, " ",  b^.yVel,  "\n")

fun BallBounce(b ^!Ball) bool:
    let! bounced = false
    set b^.x += b^.xVel
    set b^.y += b^.yVel
    if b^.x > X_LIMIT:
        set  b^.x = X_LIMIT
        set  b^.xVel = - abs(b^.xVel)
        set bounced = true
    if b^.x < 0:
        set  b^.x = 0
        set  b^.xVel = abs(b^.xVel)
        set bounced = true
    if b^.y > Y_LIMIT:
        set  b^.y = Y_LIMIT
        set  b^.yVel = - abs(b^.yVel)
        set bounced = true
    if b^.y < 0:
        set  b^.y = 0
        set  b^.yVel = abs(b^.yVel)
        set bounced = true
    return bounced




fun main(argc s32, argv ^^u8) s32:
    do RngReset()
    ref let! balls = [NUM_BALLS]Ball{}
    for i = 0, NUM_BALLS, 1:
        do BallInit(&!balls[i])
    let! num_bounces = 0_u32
    for n = 0, NUM_ITERS, 1:
        for i = 0, NUM_BALLS, 1:
            if BallBounce(&!balls[i]):
                set num_bounces += 1
    test::AssertEq#(num_bounces, 1331_u32)
    test::Success#()
    return 0
