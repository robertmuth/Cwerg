; simple ray tracer adapted from
; https://github.com/jtsiomb/c-ray/blob/master/c-ray-f/c-ray-f.c
module:

import fmt

import string

import parse_real

import random

import v64 = vec_gen (r64)

rec Material:
    col v64::vec3
    ; specular power
    spow r64
    ; reflection intensity
    refl r64

rec Sphere:
    pos v64::vec3
    rad r64
    mat Material

rec Plane:
    pos v64::vec3
    mat Material
    norm v64::vec3

rec Light:
    pos v64::vec3

rec Camera:
    pos v64::vec3
    fov r64
    target v64::vec3

rec Scene:
    camera Camera
    lights [10]Light
    num_lights uint
    spheres [100]Sphere
    num_spheres uint
    planes [100]Plane
    num_planes uint

rec Ray:
    orig v64::vec3
    dir v64::vec3

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

; captures s, out
macro read_r64# STMT_LIST ($dst EXPR) [$t]:
    set s = span_inc(s, skip_white_space(s))
    let $t = parse_real::parse_r64(s)
    set s = span_inc(s, $t.length)
    if $t.length == 0:
        return out
    set $dst = $t.value

; captures s, out
macro read_vec3# STMT_LIST ($dst EXPR) [$tx, $ty, $tz]:
    set s = span_inc(s, skip_white_space(s))
    let $tx = parse_real::parse_r64(s)
    set s = span_inc(s, $tx.length)
    set s = span_inc(s, skip_white_space(s))
    let $ty = parse_real::parse_r64(s)
    set s = span_inc(s, $ty.length)
    set s = span_inc(s, skip_white_space(s))
    let $tz = parse_real::parse_r64(s)
    set s = span_inc(s, $tz.length)
    if $tx.length == 0 || $ty.length == 0 || $tz.length == 0:
        return out
    set $dst = {: $tx.value, $ty.value, $tz.value}

; assumes that len(line) > 0
fun ParseLine(line span(u8)) LineObj:
    let! s = line
    let! out LineObj
    ;
    set out.kind = s[0]
    set s = span_inc(s, 1)
    ;
    read_vec3#(out.v1)
    read_r64#(out.s1)
    read_vec3#(out.v2)
    read_r64#(out.s2)
    read_r64#(out.s3)
    read_vec3#(out.v3)
    return out

fun ParseScene(scene_str span(u8)) Scene:
    let! s = scene_str
    let! out Scene
    while len(s) > 0:
        let! eol = string::find(s, "\n")
        if eol == string::NOT_FOUND:
            set eol = len(s) - 1
        let! line = make_span(front(s), eol + 1)
        set s = span_inc(s, eol + 1)
        set line = span_inc(line, skip_white_space(line))
        if len(line) == 0 || line[0] == '#':
            continue
        fmt::print#(line)
        let! num_cameras = 0_uint
        let obj = ParseLine(line)
        cond:
            case obj.kind == 's':
                if out.num_spheres >= len(out.spheres):
                    fmt::print#("too many spheres\n")
                    trap
                set out.spheres[out.num_spheres] =
                  {: obj.v1, obj.s1, {: obj.v2, obj.s2, obj.s3}}
                set out.num_spheres += 1
            case obj.kind == 'p':
                if out.num_planes >= len(out.planes):
                    fmt::print#("too many planes\n")
                    trap
                set out.planes[out.num_planes] =
                  {: obj.v1, {: obj.v2, obj.s2, obj.s3}, v64::normalized(obj.v3)
                   }
                set out.num_planes += 1
            case obj.kind == 'l':
                if out.num_lights >= len(out.lights):
                    fmt::print#("too many lights\n")
                    trap
                set out.lights[out.num_lights] = {: obj.v1}
                set out.num_lights += 1
            case obj.kind == 'c':
                if num_cameras != 0:
                    fmt::print#("more than one camera\n")
                    trap
                set out.camera = {: obj.v1, obj.s1, obj.v2}
                set num_cameras += 1
    return out

global! urand [1024]v64::vec2

global! irand [1024]u32

fun init_vrand_urand() void:
    ref let! state = random::Pcg32StateDefault
    for i = 0, len(urand), 1:
        set urand[i][0] = random::Pcg32GetRandomR64(@!state) - 0.5
    for i = 0, len(urand), 1:
        set urand[i][1] = random::Pcg32GetRandomR64(@!state) - 0.5
    for i = 0, len(urand), 1:
        set irand[i] = random::Pcg32GetRandomU32(@!state) % as(len(urand), u32)

fun get_jitter(x u32, y u32, s u32) v64::vec2:
    let a = irand[(x + s) % as(len(irand), u32)]
    let aa = (x + (y << 2) + a) % as(len(urand), u32)
    let b = irand[(y + s) % as(len(irand), u32)]
    let bb = (y + (x << 2) + b) % as(len(urand), u32)
    return {: urand[aa][0], urand[bb][1]}

fun get_sample_pos(w u32, h u32, x u32, y u32, s u32) v64::vec2:
    let wr = as(w, r64)
    let hr = as(h, r64)
    let xr = as(x, r64)
    let yr = as(y, r64)
    let! px = (xr / wr - 0.5) * 2.0 * wr / hr
    let! py = (0.5_r64 - yr) / hr * 2.0
    if s > 0:
        let jitter = get_jitter(x, y, s)
        let sf r64 = 1.5 / wr
        set px += jitter[0] * sf
        set py += jitter[1] * sf
    return {: px, py}

fun get_primry_ray(cam ^Camera, pos v64::vec2) Ray:
    let orig = cam^.pos
    let! dir = {v64::vec3:}
    let k = v64::sub(cam^.target, cam^.pos)
    let i = v64::cross({v64::vec3: 0, 1, 0}, k)
    let j = v64::cross(k, i)
    let m = {v64::mat3: i, j, k}
    set dir = v64::add(dir, orig)
    return {: orig, dir}

fun Render(w u32, h u32, rays_per_pixel u32, fb span!(u32), scene ^Scene) void:
    let color_scaler = 255.0_r64 / as(rays_per_pixel, r64)
    let lo = {v64::vec3: 0.0, 0.0, 0.0}
    let hi = {v64::vec3: 255.0, 255.0, 255.0}
    for y = 0, h, 1:
        for x = 0, w, 1:
            let! rgb v64::vec3
            for r = 0, rays_per_pixel, 1:
                let pos = get_sample_pos(w, h, x, y, r)
                let ray = get_primry_ray(@scene^.camera, pos)
                ; let ray = get_primary_ray()
                set rgb = v64::add(rgb, rgb)
            set rgb = v64::scaled(rgb, color_scaler)
            set rgb = v64::pmin(hi, v64::pmax(lo, rgb))
            let color = as(rgb[0], s32) << 16 + as(rgb[1], s32) << 8 +
              as(rgb[2], s32)
            set fb[y * w + x] = as(color, u32)
    return

global gSceneStr =
  """
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

; we support up to 4k - which is too large for the stack
; global gPixels [3840 * 2160]u32
ref global! gPixels [640 * 480]u32

fun main(argc s32, argv ^^u8) s32:
    ; if argc < 3:
    ;     fmt::print#("Not enough arguments, need width and height\n")
    ;     return 0
    ; let arg_w span(u8) = fmt::strz_to_slice(ptr_inc(argv, 1)^)
    ; let arg_h span(u8) = fmt::strz_to_slice(ptr_inc(argv, 2)^)
    ; let width u32 = fmt::str_to_u32(arg_w)
    ; let height u32 = fmt::str_to_u32(arg_h)
    let w u32 = 640_u32
    let h u32 = 480_u32
    let rays_per_pixel = 1_u32
    do init_vrand_urand()
    ref let scene = ParseScene(gSceneStr)
    do Render(w, h, rays_per_pixel, make_span(front!(gPixels), as(w * h, uint)),
         @scene)
    return 0
