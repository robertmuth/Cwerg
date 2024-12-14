-- simple ray tracer adapted from
-- https://github.com/jtsiomb/c-ray/blob/master/c-ray-f/c-ray-f.c
module:

import fmt
import parse_real

import v64 = vec_gen(r64)

global gScene = """
# spheres
#	position		radius	color			shininess	reflectivity
s	-1.5 -0.3 -1	0.7		1.0 0.2 0.05		50.0	0.3
s	1.5 -0.4 0		0.6		0.1 0.85 1.0		50.0	0.4

# walls
#s	0 -1000 2		999		0.1 0.2 0.6			80.0	0.8

#   position		junk										normal
p	0 -1 0			0		0.1 0.2 0.4			80.0	0.8		0 1 0
p	3 0 1			0		0.2 0.5 0.3			0		0.2		-1 0 -0.3
p	1 -1 4			0		0.1 0.1 0.1			60.0	0.5		0.3 0 -1
p	-100 0 0		0		0.7 0.6 0.5			50.0	0		1 0 0
p	1 -1 -100		0		0.1 0.1 0.1			60.0	0		0.3 0 1

# bouncing ball
s	0 0 2			1		1.0 0.5 0.1			60.0	0.7

# lights...
l	-50 100 -50
l	40 40 150

# camera (there can be only one!)
#	position	FOV		target
c	0 3 -8		45		0 0 0
"""

rec Material:
    col v64::vec3
    -- specular power
    spow r64
    -- reflection intensity
    refl r64

rec Sphere:
    pos v64::vec3
    rad r64

rec Scene:
    pos v64::vec3

global KIND_S u8 = 's'

global KIND_P u8 = 'p'

global KIND_L u8 = 'l'

global KIND_C u8 = 'c'

rec LineObj:
    kind u8
    v1 v64::vec3
    s1 r64
    v2 v64::vec3
    s2 r64
    s3 r64
    v3 v64::vec3

fun is_white_space(c u8) bool:
    return c == ' ' || c == '\n' || c == '\t' || c == '\r'


fun skip_white_space(line span(u8)) uint:
    let! n = 0_uint
    while n < len(line) && is_white_space(line[n]):
        set n += 1
    return n

fun skip_non_white_space(line span(u8)) uint:
    let! n = 0_uint
    while n < len(line) && !is_white_space(line[n]):
        set n += 1
    return n

-- captures s, out
macro read_r64# STMT_LIST($dst EXPR)[$t]:
    set s = span_inc(s, skip_white_space(s))
    mlet $t = parse_real::parse_r64(s)
    set s = span_inc(s, $t.length)
    if $t.length == 0:
        return out
    set $dst = $t.value

-- captures s, out
macro read_vec3# STMT_LIST($dst EXPR)[$tx, $ty, $tz]:
    set s = span_inc(s, skip_white_space(s))
    mlet $tx = parse_real::parse_r64(s)
    set s = span_inc(s, $tx.length)
    set s = span_inc(s, skip_white_space(s))
    mlet $ty = parse_real::parse_r64(s)
    set s = span_inc(s, $ty.length)
    set s = span_inc(s, skip_white_space(s))
    mlet $tz = parse_real::parse_r64(s)
    set s = span_inc(s, $tz.length)

    if $tx.length == 0 || $ty.length == 0 || $tz.length == 0:
        return out
    set $dst = {: $tx.value, $ty.value, $tz.value}

-- assumes that len(line) > 0
fun ParseLine(line span(u8)) LineObj:
    let! s = line
    let! out LineObj
    set out.kind = s[0]
    set s = span_inc(s, 1)
    --
    read_vec3#(out.v1)
    read_r64#(out.s1)
    read_vec3#(out.v2)
    read_r64#(out.s2)
    read_r64#(out.s3)
    read_vec3#(out.v3)
    return out

fun ParseScene(scene span(u8)) Scene:
    let! s = scene
    let out Scene
    while len(s) > 0:
        set s = s
    return out

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
    let m1 v64::mat3 = {: {: 1.0, 0.0, 0.0}, {: 0.0, 1.0, 0.0}, {: 0.0, 0.0, 1.0}}
    fmt::print#(v1, "\n")
    fmt::print#(v2, "\n")
    fmt::print#(v64::zero_vec4, "\n")
    fmt::print#(v64::add@(v1, v2), "\n")
    fmt::print#(v64::zero_mat2, "\n")
    fmt::print#(v64::id_mat4, "\n")
    return 0
