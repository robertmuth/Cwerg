-- adapted from http://shootout.alioth.debian.org/
module:

import test

import fmt

import fmt_real

global PI = 3.141592653589793_r64

global SOLAR_MASS = PI * PI * 4.0

global DAYS_PER_YEAR = 365.24_r64

global EPSILON = 5e-13_r64

rec Body:
    x r64
    y r64
    z r64
    vx r64
    vy r64
    vz r64
    mass r64

fun BodyCommon(x r64, y r64, z r64, vx r64, vy r64, vz r64, m r64) Body:
    return {
            Body : x, y, z, vx * DAYS_PER_YEAR, vy * DAYS_PER_YEAR, vz * DAYS_PER_YEAR, 
            m* SOLAR_MASS}

fun BodyJupiter() Body:
    return BodyCommon(
            4.84143144246472090e+00,
            -1.16032004402742839e+00,
            -1.03622044471123109e-01,
            1.66007664274403694e-03,
            7.69901118419740425e-03,
            -6.90460016972063023e-05,
            9.54791938424326609e-04)

fun BodySaturn() Body:
    return BodyCommon(
            8.34336671824457987e+00,
            4.12479856412430479e+00,
            -4.03523417114321381e-01,
            -2.76742510726862411e-03,
            4.99852801234917238e-03,
            2.30417297573763929e-05,
            2.85885980666130812e-04)

fun BodyUranus() Body:
    return BodyCommon(
            1.28943695621391310e+01,
            -1.51111514016986312e+01,
            -2.23307578892655734e-01,
            2.96460137564761618e-03,
            2.37847173959480950e-03,
            -2.96589568540237556e-05,
            4.36624404335156298e-05)

fun BodyNeptune() Body:
    return BodyCommon(
            1.53796971148509165e+01,
            -2.59193146099879641e+01,
            1.79258772950371181e-01,
            2.68067772490389322e-03,
            1.62824170038242295e-03,
            -9.51592254519715870e-05,
            5.15138902046611451e-05)

fun BodySun() Body:
    return BodyCommon(0, 0, 0, 0, 0, 0, 1.0)

fun UpdateOffsetMomentum(bodies ^![5]Body) void:
    let! px = 0.0_r64
    let! py = 0.0_r64
    let! pz = 0.0_r64
    for i = 0, len(bodies^), 1:
        let b = &!bodies^[i]
        set px += b^.vx * b^.mass
        set py += b^.vy * b^.mass
        set pz += b^.vz * b^.mass
    let s = &!bodies^[0]
    set s^.vx = -(px / SOLAR_MASS)
    set s^.vy = -(py / SOLAR_MASS)
    set s^.vz = -(pz / SOLAR_MASS)

fun Advance(bodies ^![5]Body, dt r64) void:
    for i = 0, len(bodies^), 1:
        let bi = &!bodies^[i]
        for j = i + 1, len(bodies^), 1:
            let bj = &!bodies^[j]
            let dx = bi^.x - bj^.x
            let dy = bi^.y - bj^.y
            let dz = bi^.z - bj^.z
            let d2 = dx * dx + dy * dy + dz * dz
            let d = sqrt(d2)
            let mag = dt / (d * d2)
            let mj = bj^.mass * mag
            set bi^.vx -= dx * mj
            set bi^.vy -= dy * mj
            set bi^.vz -= dz * mj
            let mi = bi^.mass * mag
            set bj^.vx += dx * mi
            set bj^.vy += dy * mi
            set bj^.vz += dz * mi
    for i = 0, len(bodies^), 1:
        let bi = &!bodies^[i]
        set bi^.x += dt * bi^.vx
        set bi^.y += dt * bi^.vy
        set bi^.z += dt * bi^.vz

fun Energy(bodies ^[5]Body) r64:
    let! e = 0.0_r64
    for i = 0, len(bodies^), 1:
        let bi = &bodies^[i]
        set e += 0.5 * bi^.mass * (bi^.vx * bi^.vx + bi^.vy * bi^.vy + bi^.vz * bi^.
            vz)
        for j = i + 1, len(bodies^), 1:
            let bj = &bodies^[j]
            let dx = bi^.x - bj^.x
            let dy = bi^.y - bj^.y
            let dz = bi^.z - bj^.z
            let d = sqrt(dx * dx + dy * dy + dz * dz)
            set e -= bi^.mass * bj^.mass / d
    return e

global DT = 0.01_r64

global NUM_ITER = 250000_u32

fun main(argc s32, argv ^^u8) s32:
    ref let! bodies = {
            [5]Body : BodySun(), BodyJupiter(), BodySaturn(), BodyUranus(), BodyNeptune(
            )}
    do UpdateOffsetMomentum(&!bodies)
    -- do permute(&!v, DIM)
    -- DIM! = 5040
    -- test::AssertEq#(COUNT, 5040_u32)
    if true:
        -- sanity test with one iteration
        do Advance(&!bodies, DT)
        let e = Energy(&bodies)
        -- fmt::print#(wrap_as(e, fmt::r64_hex), " ", e, "\n")
        test::AssertApproxEq#(e, -0.16907495402506745_r64, EPSILON)
    else:
        for i = 0, NUM_ITER, 1:
            do Advance(&!bodies, DT)
        let e = Energy(&bodies)
        -- fmt::print#(wrap_as(e, fmt::r64_hex), " ", e,  "\n")
        test::AssertApproxEq#(e, -0.1690859889909308_r64, EPSILON)
    test::Success#()
    return 0
