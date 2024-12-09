module:

import fmt

pub type vec2_r32 = [2]r32

pub type vec3_r32 = [3]r32

pub type vec4_r32 = [4]r32

--
pub type vec2_r64 = [2]r64

pub type vec3_r64 = [3]r64

pub type vec4_r64 = [4]r64

--
fun add@(a vec2_r32, b vec2_r32) vec2_r32:
    return {: a[0] + b[0], a[1] + b[1]}

fun add@(a vec3_r32, b vec3_r32) vec3_r32:
    return {: a[0] + b[0], a[1] + b[1], a[2] + b[2]}

fun add@(a vec4_r32, b vec4_r32) vec4_r32:
    return {: a[0] + b[0], a[1] + b[1], a[2] + b[2], a[3] + b[3]}

--
fun add@(a vec2_r64, b vec2_r64) vec2_r64:
    return {: a[0] + b[0], a[1] + b[1]}


fun add@(a vec3_r64, b vec3_r64) vec3_r64:
    return {: a[0] + b[0], a[1] + b[1], a[2] + b[2]}

fun add@(a vec4_r64, b vec4_r64) vec4_r64:
    return {: a[0] + b[0], a[1] + b[1], a[2] + b[2], a[3] + b[3]}

--
fun sub@(a vec2_r32, b vec2_r32) vec2_r32:
    return {: a[0] - b[0], a[1] - b[1]}

fun sub@(a vec3_r32, b vec3_r32) vec3_r32:
    return {: a[0] - b[0], a[1] - b[1], a[2] - b[2]}

fun sub@(a vec4_r32, b vec4_r32) vec4_r32:
    return {: a[0] - b[0], a[1] - b[1], a[2] - b[2], a[3] - b[3]}

--
fun sub@(a vec2_r64, b vec2_r64) vec2_r64:
    return {: a[0] - b[0], a[1] - b[1]}

fun sub@(a vec3_r64, b vec3_r64) vec3_r64:
    return {: a[0] - b[0], a[1] -  b[1], a[2] - b[2]}


fun sub@(a vec4_r64, b vec4_r64) vec4_r64:
    return {: a[0] - b[0], a[1] - b[1], a[2] - b[2], a[3] - b[3]}

--
fun scale@(b vec2_r32, a r32) vec2_r32:
    return {: a * b[0], a * b[1]}


fun scale@(b vec3_r32, a r32) vec3_r32:
    return {: a * b[0], a * b[1], a * b[2]}


fun scale@(b vec4_r32, a r32) vec4_r32:
    return {: a * b[0], a * b[1], a * b[2], a * b[3]}

--
fun scale@(b vec2_r64, a r64) vec2_r64:
    return {: a * b[0], a * b[1]}

fun scale@(b vec3_r64, a r64) vec3_r64:
    return {: a * b[0], a *  b[1], a * b[2]}

fun scale@(b vec4_r64, a r64) vec4_r64:
    return {: a * b[0], a * b[1], a * b[2], a * b[3]}

--
fun fmt::SysRender@(v vec2_r64, out span!(u8), opt ^!fmt::SysFormatOptions) uint:
    let f = front!(out)
    let l = len(out)
    let! n uint = 0
    set n += fmt::SysRender@("{", out, opt)
    set n += fmt::SysRender@(v[0], span(pinc(f, n), l - n), opt)
    set n += fmt::SysRender@(",", span(pinc(f, n), l - n), opt)
    set n += fmt::SysRender@(v[1], span(pinc(f, n), l - n), opt)
    set n += fmt::SysRender@("}", span(pinc(f, n), l - n), opt)
    return n

fun fmt::SysRender@(v vec3_r64, out span!(u8), opt ^!fmt::SysFormatOptions) uint:
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

fun fmt::SysRender@(v vec4_r64, out span!(u8), opt ^!fmt::SysFormatOptions) uint:
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