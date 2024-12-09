module($T TYPE):

import fmt

--
pub type vec2 = [2]$T

pub type vec3 = [3]$T

pub type vec4 = [4]$T


--
fun add@(a vec2, b vec2) vec2:
    return {: a[0] + b[0], a[1] + b[1]}

fun add@(a vec3, b vec3) vec3:
    return {: a[0] + b[0], a[1] + b[1], a[2] + b[2]}

fun add@(a vec4, b vec4) vec4:
    return {: a[0] + b[0], a[1] + b[1], a[2] + b[2], a[3] + b[3]}

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
    return {: a[0] - b[0], a[1] -  b[1], a[2] - b[2]}

fun sub@(a vec4, b vec4) vec4:
    return {: a[0] - b[0], a[1] - b[1], a[2] - b[2], a[3] - b[3]}

--
fun scale@(b vec2, a $T) vec2:
    return {: a * b[0], a * b[1]}

fun scale@(b vec3, a $T) vec3:
    return {: a * b[0], a *  b[1], a * b[2]}

fun scale@(b vec4, a $T) vec4:
    return {: a * b[0], a * b[1], a * b[2], a * b[3]}

--
fun fmt::SysRender@(v vec2, out span!(u8), opt ^!fmt::SysFormatOptions) uint:
    let f = front!(out)
    let l = len(out)
    let! n uint = 0
    set n += fmt::SysRender@("{", out, opt)
    set n += fmt::SysRender@(v[0], span(pinc(f, n), l - n), opt)
    set n += fmt::SysRender@(",", span(pinc(f, n), l - n), opt)
    set n += fmt::SysRender@(v[1], span(pinc(f, n), l - n), opt)
    set n += fmt::SysRender@("}", span(pinc(f, n), l - n), opt)
    return n

fun fmt::SysRender@(v vec3, out span!(u8), opt ^!fmt::SysFormatOptions) uint:
    let f = front!(out)
    let l = len(out)
    let! n uint = 0
    set n += fmt::SysRender@("{", out, opt)
    set n += fmt::SysRender@(v[0], span(pinc(f, n), l - n), opt)
    set n += fmt::SysRender@(",", span(pinc(f, n), l - n), opt)
    set n += fmt::SysRender@(v[1], span(pinc(f, n), l - n), opt)
    set n += fmt::SysRender@(",", span(pinc(f, n), l - n), opt)
    set n += fmt::SysRender@(v[2], span(pinc(f, n), l - n), opt)
    set n += fmt::SysRender@("}", span(pinc(f, n), l - n), opt)
    return n

fun fmt::SysRender@(v vec4, out span!(u8), opt ^!fmt::SysFormatOptions) uint:
    let f = front!(out)
    let l = len(out)
    let! n uint = 0
    set n += fmt::SysRender@("{", out, opt)
    set n += fmt::SysRender@(v[0], span(pinc(f, n), l - n), opt)
    set n += fmt::SysRender@(",", span(pinc(f, n), l - n), opt)
    set n += fmt::SysRender@(v[1], span(pinc(f, n), l - n), opt)
    set n += fmt::SysRender@(",", span(pinc(f, n), l - n), opt)
    set n += fmt::SysRender@(v[2], span(pinc(f, n), l - n), opt)
    set n += fmt::SysRender@(",", span(pinc(f, n), l - n), opt)
    set n += fmt::SysRender@(v[3], span(pinc(f, n), l - n), opt)
    set n += fmt::SysRender@("}", span(pinc(f, n), l - n), opt)
    return n