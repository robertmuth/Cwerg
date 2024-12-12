module($T TYPE):

import fmt

--
pub type vec2 = [2]$T

pub type vec3 = [3]$T

pub type vec4 = [4]$T

pub type mat2 = [2][2]$T

pub type mat3 = [3][3]$T

pub type mat4 = [4][4]$T

pub global zero_vec2 vec2
pub global zero_vec3 vec3
pub global zero_vec4 vec4

pub global zero_mat2 mat2
pub global zero_mat3 mat3
pub global zero_mat4 mat4

pub global id_mat2 mat2 = {:
    {: 1.0, 0.0},
    {: 0.0, 1.0}}

pub global id_mat3 mat3= {:
    {: 1.0, 0.0, 0.0},
    {: 0.0, 1.0, 0.0},
    {: 0.0, 0.0, 1.0}}

pub global id_mat4 mat4= {:
    {: 1.0, 0.0, 0.0, 0.0},
    {: 0.0, 1.0, 0.0, 0.0},
    {: 0.0, 0.0, 1.0, 0.0},
    {: 0.0, 0.0, 0.0, 1.0}}

--
fun add@(a vec2, b vec2) vec2:
    return {: a[0] + b[0], a[1] + b[1]}

fun add@(a vec3, b vec3) vec3:
    return {: a[0] + b[0], a[1] + b[1], a[2] + b[2]}

fun add@(a vec4, b vec4) vec4:
    return {: a[0] + b[0], a[1] + b[1], a[2] + b[2], a[3] + b[3]}

fun add@(a mat2, b mat2) mat2:
    return {:
    {: a[0][0] + b[0][0], a[0][1] + b[0][1] },
    {: a[1][0] + b[1][0], a[1][1] + b[1][1] }}

fun add@(a mat3, b mat3) mat3:
    return {:
    {: a[0][0] + b[0][0], a[0][1] + b[0][1], a[0][2] + b[0][2] },
    {: a[1][0] + b[1][0], a[1][1] + b[1][1], a[1][2] + b[1][2] },
    {: a[2][0] + b[2][0], a[2][1] + b[2][1], a[2][2] + b[2][2] }}

fun add@(a mat4, b mat4) mat4:
    return {:
    {: a[0][0] + b[0][0], a[0][1] + b[0][1], a[0][2] + b[0][2], a[0][3] +  b[0][3] },
    {: a[1][0] + b[1][0], a[1][1] + b[1][1], a[1][2] + b[1][2], a[1][3] +  b[1][3] },
    {: a[2][0] + b[2][0], a[2][1] + b[2][1], a[2][2] + b[2][2], a[2][3] +  b[2][3] },
    {: a[3][0] + b[3][0], a[3][1] + b[3][1], a[3][2] + b[3][2], a[3][3] +  b[3][3] }}
--
fun dot@(a vec2, b vec2) $T:
    return a[0] * b[0] + a[1] * b[1]

fun dot@(a vec3, b vec3) $T:
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]

fun dot@(a vec4, b vec4) $T:
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2] + a[3] * b[3]

--
fun sub@(a vec2, b vec2) vec2:
    return {: a[0] - b[0], a[1] - b[1]}

fun sub@(a vec3, b vec3) vec3:
    return {: a[0] - b[0], a[1] - b[1], a[2] - b[2]}

fun sub@(a vec4, b vec4) vec4:
    return {: a[0] - b[0], a[1] - b[1], a[2] - b[2], a[3] - b[3]}

fun sub@(a mat2, b mat2) mat2:
    return {:
    {: a[0][0] - b[0][0], a[0][1] - b[0][1] },
    {: a[1][0] - b[1][0], a[1][1] - b[1][1] }}

fun sub@(a mat3, b mat3) mat3:
    return {:
    {: a[0][0] - b[0][0], a[0][1] - b[0][1], a[0][2] - b[0][2] },
    {: a[1][0] - b[1][0], a[1][1] - b[1][1], a[1][2] - b[1][2] },
    {: a[2][0] - b[2][0], a[2][1] - b[2][1], a[2][2] - b[2][2] }}

fun sub@(a mat4, b mat4) mat4:
    return {:
    {: a[0][0] - b[0][0], a[0][1] - b[0][1], a[0][2] - b[0][2], a[0][3] - b[0][3] },
    {: a[1][0] - b[1][0], a[1][1] - b[1][1], a[1][2] - b[1][2], a[1][3] - b[1][3] },
    {: a[2][0] - b[2][0], a[2][1] - b[2][1], a[2][2] - b[2][2], a[2][3] - b[2][3] },
    {: a[3][0] - b[3][0], a[3][1] - b[3][1], a[3][2] - b[3][2], a[3][3] - b[3][3] }}
--
fun scale@(b vec2, a $T) vec2:
    return {: a * b[0], a * b[1]}

fun scale@(b vec3, a $T) vec3:
    return {: a * b[0], a *  b[1], a * b[2]}

fun scale@(b vec4, a $T) vec4:
    return {: a * b[0], a * b[1], a * b[2], a * b[3]}

fun scale@(b mat2, a $T) mat2:
    return {:
    {: a * b[0][0], a * b[0][1] },
    {: a * b[1][0], a * b[1][1] }}

fun scale@(b mat3, a $T) mat3:
    return {:
    {: a * b[0][0], a * b[0][1], a * b[0][2] },
    {: a * b[1][0], a * b[1][1], a * b[1][2] },
    {: a * b[2][0], a * b[2][1], a * b[2][2] }}

fun scale@(b mat4, a $T) mat4:
    return {:
    {: a * b[0][0], a * b[0][1], a * b[0][2], a * b[0][3] },
    {: a * b[1][0], a * b[1][1], a * b[1][2], a * b[1][3] },
    {: a * b[2][0], a * b[2][1], a * b[2][2], a * b[2][3] },
    {: a * b[3][0], a * b[3][1], a * b[3][2], a * b[3][3] }}

--
fun fmt::SysRender@(v vec2, out span!(u8), opt ^!fmt::SysFormatOptions) uint:
    let! t = out
    set t = span_inc(t, fmt::SysRender@("{", t, opt))
    set t = span_inc(t, fmt::SysRender@(v[0], t, opt))
    set t = span_inc(t, fmt::SysRender@(",", t, opt))
    set t = span_inc(t, fmt::SysRender@(v[1], t, opt))
    set t = span_inc(t, fmt::SysRender@("}", t, opt))
    return as(front(t) &-& front(out), uint)


fun fmt::SysRender@(v vec3, out span!(u8), opt ^!fmt::SysFormatOptions) uint:
    let! t = out
    set t = span_inc(t, fmt::SysRender@("{", t, opt))
    set t = span_inc(t, fmt::SysRender@(v[0], t, opt))
    set t = span_inc(t, fmt::SysRender@(",", t, opt))
    set t = span_inc(t, fmt::SysRender@(v[1], t, opt))
    set t = span_inc(t, fmt::SysRender@(",", t, opt))
    set t = span_inc(t, fmt::SysRender@(v[2], t, opt))
    set t = span_inc(t, fmt::SysRender@("}", t, opt))
    return as(front(t) &-& front(out), uint)

fun fmt::SysRender@(v vec4, out span!(u8), opt ^!fmt::SysFormatOptions) uint:
    let! t = out
    set t = span_inc(t, fmt::SysRender@("{", t, opt))
    set t = span_inc(t, fmt::SysRender@(v[0], t, opt))
    set t = span_inc(t, fmt::SysRender@(",", t, opt))
    set t = span_inc(t, fmt::SysRender@(v[1], t, opt))
    set t = span_inc(t, fmt::SysRender@(",", t, opt))
    set t = span_inc(t, fmt::SysRender@(v[2], t, opt))
    set t = span_inc(t, fmt::SysRender@(",", t, opt))
    set t = span_inc(t, fmt::SysRender@(v[3], t, opt))
    set t = span_inc(t, fmt::SysRender@("}", t, opt))
    return as(front(t) &-& front(out), uint)


fun fmt::SysRender@(v mat2, out span!(u8), opt ^!fmt::SysFormatOptions) uint:
    let! t = out
    set t = span_inc(t, fmt::SysRender@("{", t, opt))
    set t = span_inc(t, fmt::SysRender@(v[0], t, opt))
    set t = span_inc(t, fmt::SysRender@(",", t, opt))
    set t = span_inc(t, fmt::SysRender@(v[1], t, opt))
    set t = span_inc(t, fmt::SysRender@("}", t, opt))
    return as(front(t) &-& front(out), uint)


fun fmt::SysRender@(v mat3, out span!(u8), opt ^!fmt::SysFormatOptions) uint:
    let! t = out
    set t = span_inc(t, fmt::SysRender@("{", t, opt))
    set t = span_inc(t, fmt::SysRender@(v[0], t, opt))
    set t = span_inc(t, fmt::SysRender@(",", t, opt))
    set t = span_inc(t, fmt::SysRender@(v[1], t, opt))
    set t = span_inc(t, fmt::SysRender@(",", t, opt))
    set t = span_inc(t, fmt::SysRender@(v[2], t, opt))
    set t = span_inc(t, fmt::SysRender@("}", t, opt))
    return as(front(t) &-& front(out), uint)

fun fmt::SysRender@(v mat4, out span!(u8), opt ^!fmt::SysFormatOptions) uint:
    let! t = out
    set t = span_inc(t, fmt::SysRender@("{", t, opt))
    set t = span_inc(t, fmt::SysRender@(v[0], t, opt))
    set t = span_inc(t, fmt::SysRender@(",", t, opt))
    set t = span_inc(t, fmt::SysRender@(v[1], t, opt))
    set t = span_inc(t, fmt::SysRender@(",", t, opt))
    set t = span_inc(t, fmt::SysRender@(v[2], t, opt))
    set t = span_inc(t, fmt::SysRender@(",", t, opt))
    set t = span_inc(t, fmt::SysRender@(v[3], t, opt))
    set t = span_inc(t, fmt::SysRender@("}", t, opt))
    return as(front(t) &-& front(out), uint)
