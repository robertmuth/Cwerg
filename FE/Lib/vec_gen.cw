module($T TYPE):

import fmt

-- vecX may be interpreted as row or column vectors
pub type vec2 = [2]$T

pub type vec3 = [3]$T

pub type vec4 = [4]$T

-- matX is organized in row major form
-- https://en.wikipedia.org/wiki/Row-_and_column-major_order
-- matX[i] denotes the row vector of row i
pub type mat2 = [2][2]$T

pub type mat3 = [3][3]$T

pub type mat4 = [4][4]$T

pub global ZERO_vec2 = {vec2:  0, 0}
pub global ONES_vec2 = {vec2:  1, 1}
pub global X_vec2 = {vec2:  1, 0}
pub global Y_vec2 = {vec2:  0, 1}

pub global ZERO_vec3 = {vec3:  0, 0, 0}
pub global ONES_vec3 = {vec3:  1, 1, 1}

pub global X_vec3 = {vec3:  1, 0, 0}
pub global Y_vec3 = {vec3:  0, 1, 0}
pub global Z_vec3 = {vec3:  0, 0, 1}

pub global ZERO_vec4 = {vec4:  0, 0, 0, 0}
pub global ONES_vec4 = {vec4:  1, 1, 1, 1}
pub global X_vec4 = {vec4:  1, 0, 0, 0}
pub global Y_vec4 = {vec4:  0, 1, 0, 0}
pub global Z_vec4 = {vec4:  0, 0, 1, 0}
pub global W_vec4 = {vec4:  0, 0, 0, 1}

pub global ZERO_mat2 mat2

pub global ZERO_mat3 mat3

pub global ZERO_mat4 mat4

pub global ID_mat2 = {mat2: {: 1.0, 0.0}, {: 0.0, 1.0}}

pub global ID_mat3 = {mat3: {: 1.0, 0.0, 0.0}, {: 0.0, 1.0, 0.0}, {
        : 0.0, 0.0, 1.0}}

pub global ID_mat4 mat4 = {
        : {: 1.0, 0.0, 0.0, 0.0}, {: 0.0, 1.0, 0.0, 0.0}, {: 0.0, 0.0, 1.0, 0.0}, {
            : 0.0, 0.0, 0.0, 1.0}}

--
fun eq@(a vec2, b vec2) bool:
    return a[0] == b[0] && a[1] == b[1]

fun eq@(a vec3, b vec3) bool:
    return a[0] == b[0] && a[1] == b[1] && a[2] == b[2]

fun eq@(a vec4, b vec4) bool:
    return a[0] == b[0] && a[1] == b[1] && a[2] == b[2] && a[3] == b[3]

fun eq@(a mat2, b mat2) bool:
    return a[0][0] == b[0][0] && a[0][1] == b[0][1] &&
           a[1][0] == b[1][0] && a[1][1] == b[1][1]

fun eq@(a mat3, b mat3) bool:
    return a[0][0] == b[0][0] && a[0][1] == b[0][1] && a[0][2] == b[0][2] &&
           a[1][0] == b[1][0] && a[1][1] == b[1][1] && a[1][2] == b[1][2] &&
           a[2][0] == b[2][0] && a[2][1] == b[2][1] && a[2][2] == b[2][2]

fun eq@(a mat4, b mat4) bool:
    return a[0][0] == b[0][0] && a[0][1] == b[0][1] &&
           a[0][2] == b[0][2] && a[0][3] == b[0][3] &&
           a[1][0] == b[1][0] && a[1][1] == b[1][1] &&
           a[1][2] == b[1][2] && a[1][3] == b[1][3] &&
           a[2][0] == b[2][0] && a[2][1] == b[2][1] &&
           a[2][2] == b[2][2] && a[2][3] == b[2][3] &&
           a[3][0] == b[3][0] && a[3][1] == b[3][1] &&
           a[3][2] == b[3][2] && a[3][3] == b[3][3]


--
fun add@(a vec2, b vec2) vec2:
    return {: a[0] + b[0], a[1] + b[1]}

fun add@(a vec3, b vec3) vec3:
    return {: a[0] + b[0], a[1] + b[1], a[2] + b[2]}

fun add@(a vec4, b vec4) vec4:
    return {: a[0] + b[0], a[1] + b[1], a[2] + b[2], a[3] + b[3]}

fun add@(a mat2, b mat2) mat2:
    return {
            : {: a[0][0] + b[0][0], a[0][1] + b[0][1]}, {
                : a[1][0] + b[1][0], a[1][1] + b[1][1]}}

fun add@(a mat3, b mat3) mat3:
    return {:
            {: a[0][0] + b[0][0], a[0][1] + b[0][1], a[0][2] + b[0][2]},
            {: a[1][0] + b[1][0], a[1][1] + b[1][1], a[1][2] + b[1][2]},
            {: a[2][0] + b[2][0], a[2][1] + b[2][1], a[2][2] + b[2][2]}}

fun add@(a mat4, b mat4) mat4:
    return {:
            {: a[0][0] + b[0][0], a[0][1] + b[0][1],
               a[0][2] + b[0][2], a[0][3] + b[0][3]},
            {: a[1][0] + b[1][0], a[1][1] + b[1][1],
               a[1][2] + b[1][2], a[1][3] + b[1][3]},
            {: a[2][0] + b[2][0], a[2][1] + b[2][1],
               a[2][2] + b[2][2], a[2][3] + b[2][3]},
            {: a[3][0] + b[3][0], a[3][1] + b[3][1],
               a[3][2] + b[3][2], a[3][3] + b[3][3]}}

--
fun max@(a vec2, b vec2) vec2:
    return {: max(a[0], b[0]), max(a[1], b[1])}

fun max@(a vec3, b vec3) vec3:
    return {: max(a[0], b[0]), max(a[1], b[1]), max(a[2], b[2])}

fun max@(a vec4, b vec4) vec4:
    return {: max(a[0], b[0]), max(a[1], b[1]), max(a[2], b[2]), max(a[3], b[3])}

--
fun min@(a vec2, b vec2) vec2:
    return {: min(a[0], b[0]), min(a[1], b[1])}

fun min@(a vec3, b vec3) vec3:
    return {: min(a[0], b[0]), min(a[1], b[1]), min(a[2], b[2])}

fun min@(a vec4, b vec4) vec4:
    return {: min(a[0], b[0]), min(a[1], b[1]), min(a[2], b[2]), min(a[3], b[3])}
--

fun cross@(a vec3, b vec3) vec3:
    return {: a[1] * b[2] - a[2] * b[1],
              a[2] * b[0] - a[0] * b[2],
              a[0] * b[1] - a[1] * b[0]}
--
fun dot@(a vec2, b vec2) $T:
    return a[0] * b[0] + a[1] * b[1]

fun dot@(a vec3, b vec3) $T:
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]

fun dot@(a vec4, b vec4) $T:
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2] + a[3] * b[3]

-- b is interpreted as a column vec and the result is a column vec
fun mulmv@(a mat2, b vec2) vec2:
    return {: a[0][0] * b[0] +  a[0][1] * b[1],
              a[1][0] * b[0] +  a[1][1] * b[1]}

-- a is interpreted as a row vec and the result is a row vec
fun mulvm@(b vec2, a mat2) vec2:
    return {: a[0][0] * b[0] +  a[1][0] * b[1],
              a[0][1] * b[0] +  a[1][1] * b[1]}

fun mulmm@(a mat2, b mat2) mat2:
    return {:
        {: a[0][0] * b[0][0] +  a[0][1] * b[1][0],
           a[0][0] * b[0][1] +  a[0][1] * b[1][1]},
        {: a[1][0] * b[0][0] +  a[1][1] * b[1][0],
           a[1][0] * b[0][1] +  a[1][1] * b[1][1]}}

fun mulmv@(a mat3, b vec3) vec3:
    return {: a[0][0] * b[0] +  a[0][1] * b[1] + a[0][2] * b[2],
              a[1][0] * b[0] +  a[1][1] * b[1] + a[1][2] * b[2],
              a[2][0] * b[0] +  a[2][1] * b[1] + a[2][2] * b[2]}

-- a is interpreted as a row vec and the result is a row vec
fun mulvm@(b vec3, a mat3) vec3:
    return {: a[0][0] * b[0] +  a[1][0] * b[1] + a[2][0] * b[2],
              a[0][1] * b[0] +  a[1][1] * b[1] + a[2][1] * b[2],
              a[0][2] * b[0] +  a[1][2] * b[1] + a[2][2] * b[2]}


fun mulmm@(a mat3, b mat3) mat3:
    return {:
        {: a[0][0] * b[0][0] +  a[0][1] * b[1][0] + a[0][2] * b[2][0],
           a[0][0] * b[0][1] +  a[0][1] * b[1][1] + a[0][2] * b[2][1],
           a[0][0] * b[0][2] +  a[0][1] * b[2][2] + a[0][2] * b[2][2]},
        {: a[1][0] * b[0][0] +  a[1][1] * b[1][0] + a[1][2] * b[2][0],
           a[1][0] * b[0][1] +  a[1][1] * b[1][1] + a[1][2] * b[2][1],
           a[1][0] * b[0][2] +  a[1][1] * b[2][2] + a[1][2] * b[2][2]},
        {: a[2][0] * b[0][0] +  a[2][1] * b[1][0] + a[2][2] * b[2][0],
           a[2][0] * b[0][1] +  a[2][1] * b[1][1] + a[2][2] * b[2][1],
           a[2][0] * b[0][2] +  a[2][1] * b[2][2] + a[2][2] * b[2][2]}
    }
--
fun sub@(a vec2, b vec2) vec2:
    return {: a[0] - b[0], a[1] - b[1]}

fun sub@(a vec3, b vec3) vec3:
    return {: a[0] - b[0], a[1] - b[1], a[2] - b[2]}

fun sub@(a vec4, b vec4) vec4:
    return {: a[0] - b[0], a[1] - b[1], a[2] - b[2], a[3] - b[3]}

fun sub@(a mat2, b mat2) mat2:
    return {
            : {: a[0][0] - b[0][0], a[0][1] - b[0][1]}, {
                : a[1][0] - b[1][0], a[1][1] - b[1][1]}}

fun sub@(a mat3, b mat3) mat3:
    return {
            : {: a[0][0] - b[0][0], a[0][1] - b[0][1], a[0][2] - b[0][2]},
            {: a[1][0] - b[1][0], a[1][1] - b[1][1], a[1][2] - b[1][2]},
            {: a[2][0] - b[2][0], a[2][1] - b[2][1], a[2][2] - b[2][2]}}

fun sub@(a mat4, b mat4) mat4:
    return {:
      {: a[0][0] - b[0][0], a[0][1] - b[0][1],
         a[0][2] - b[0][2], a[0][3] - b[0][3]},
      {: a[1][0] - b[1][0], a[1][1] - b[1][1],
         a[1][2] - b[1][2], a[1][3] - b[1][3]},
      {: a[2][0] - b[2][0], a[2][1] - b[2][1],
         a[2][2] - b[2][2], a[2][3] - b[2][3]},
      {: a[3][0] - b[3][0], a[3][1] - b[3][1],
         a[3][2] - b[3][2], a[3][3] - b[3][3]}}
--
fun normalized@(a vec2) vec2:
    let x = a[0]
    let y = a[1]
    let li $T = 1.0 / sqrt(x * x + y * y)
    return {: x * li , y * li}

fun normalized@(a vec3) vec3:
    let x = a[0]
    let y = a[1]
    let z = a[2]

    let li $T = 1.0 / sqrt(x * x + y * y + z * z)
    return {: x * li , y * li, z * li}

fun normalized@(a vec4) vec4:
    let x = a[0]
    let y = a[1]
    let z = a[2]
    let w = a[3]

    let li $T = 1.0 / sqrt(x * x + y * y + z * z + w * w)
    return {: x * li , y * li, z * li, w * li}
--
fun scaled@(b vec2, a $T) vec2:
    return {: a * b[0], a * b[1]}

fun scaled@(b vec3, a $T) vec3:
    return {: a * b[0], a * b[1], a * b[2]}

fun scaled@(b vec4, a $T) vec4:
    return {: a * b[0], a * b[1], a * b[2], a * b[3]}

fun scaled@(b mat2, a $T) mat2:
    return {: {: a * b[0][0], a * b[0][1]}, {: a * b[1][0], a * b[1][1]}}

fun scaled@(b mat3, a $T) mat3:
    return {
            : {: a * b[0][0], a * b[0][1], a * b[0][2]},
            {: a * b[1][0], a * b[1][1], a * b[1][2]},
            {: a * b[2][0], a * b[2][1], a * b[2][2]}}

fun scaled@(b mat4, a $T) mat4:
    return {
            : {: a * b[0][0], a * b[0][1], a * b[0][2], a * b[0][3]},
            {: a * b[1][0], a * b[1][1], a * b[1][2], a * b[1][3]},
            {: a * b[2][0], a * b[2][1], a * b[2][2], a * b[2][3]},
            {: a * b[3][0], a * b[3][1], a * b[3][2], a * b[3][3]}}

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
