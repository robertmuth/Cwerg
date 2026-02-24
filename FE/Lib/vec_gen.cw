module($T TYPE):

import fmt

; vecX may be interpreted as row or column vectors
pub type vec2 = [2]$T

pub type vec3 = [3]$T

pub type vec4 = [4]$T

; matX is organized in row major form
; https://en.wikipedia.org/wiki/Row-_and_column-major_order
; matX[i] denotes the row vector of row i
pub type mat2 = [2][2]$T

pub type mat3 = [3][3]$T

pub type mat4 = [4][4]$T

pub global ZERO_vec2 = {vec2: 0, 0}

pub global ONES_vec2 = {vec2: 1, 1}

pub global X_vec2 = {vec2: 1, 0}

pub global Y_vec2 = {vec2: 0, 1}

pub global ZERO_vec3 = {vec3: 0, 0, 0}

pub global ONES_vec3 = {vec3: 1, 1, 1}

pub global X_vec3 = {vec3: 1, 0, 0}

pub global Y_vec3 = {vec3: 0, 1, 0}

pub global Z_vec3 = {vec3: 0, 0, 1}

pub global ZERO_vec4 = {vec4: 0, 0, 0, 0}

pub global ONES_vec4 = {vec4: 1, 1, 1, 1}

pub global X_vec4 = {vec4: 1, 0, 0, 0}

pub global Y_vec4 = {vec4: 0, 1, 0, 0}

pub global Z_vec4 = {vec4: 0, 0, 1, 0}

pub global W_vec4 = {vec4: 0, 0, 0, 1}

pub global ZERO_mat2 mat2

pub global ZERO_mat3 mat3

pub global ZERO_mat4 mat4

pub global ID_mat2 = {mat2:
                      {: 1.0, 0.0}, {: 0.0, 1.0}}

pub global ID_mat3 = {mat3:
                      {: 1.0, 0.0, 0.0}, {: 0.0, 1.0, 0.0}, {: 0.0, 0.0, 1.0}}

pub global ID_mat4 mat4 = {:
                           {: 1.0, 0.0, 0.0, 0.0}, {: 0.0, 1.0, 0.0, 0.0},
                           {: 0.0, 0.0, 1.0, 0.0}, {: 0.0, 0.0, 0.0, 1.0}}

;
poly pub fun eq(a vec2, b vec2) bool:
    return a[0] == b[0] && a[1] == b[1]

poly fun eq(a vec3, b vec3) bool:
    return a[0] == b[0] && a[1] == b[1] && a[2] == b[2]

poly fun eq(a vec4, b vec4) bool:
    return a[0] == b[0] && a[1] == b[1] && a[2] == b[2] && a[3] == b[3]

poly fun eq(a mat2, b mat2) bool:
    return a[0][0] == b[0][0] && a[0][1] == b[0][1] && a[1][0] == b[1][0] &&
      a[1][1] == b[1][1]

poly fun eq(a mat3, b mat3) bool:
    return a[0][0] == b[0][0] && a[0][1] == b[0][1] && a[0][2] == b[0][2] &&
      a[1][0] == b[1][0] && a[1][1] == b[1][1] && a[1][2] == b[1][2] && a[2][0]
      == b[2][0] && a[2][1] == b[2][1] && a[2][2] == b[2][2]

poly fun eq(a mat4, b mat4) bool:
    return a[0][0] == b[0][0] && a[0][1] == b[0][1] && a[0][2] == b[0][2] &&
      a[0][3] == b[0][3] && a[1][0] == b[1][0] && a[1][1] == b[1][1] && a[1][2]
      == b[1][2] && a[1][3] == b[1][3] && a[2][0] == b[2][0] && a[2][1] ==
      b[2][1] && a[2][2] == b[2][2] && a[2][3] == b[2][3] && a[3][0] == b[3][0]
      && a[3][1] == b[3][1] && a[3][2] == b[3][2] && a[3][3] == b[3][3]

;
poly pub fun add(a vec2, b vec2) vec2:
    return {: a[0] + b[0], a[1] + b[1]}

poly fun add(a vec3, b vec3) vec3:
    return {: a[0] + b[0], a[1] + b[1], a[2] + b[2]}

poly fun add(a vec4, b vec4) vec4:
    return {: a[0] + b[0], a[1] + b[1], a[2] + b[2], a[3] + b[3]}

poly fun add(a mat2, b mat2) mat2:
    return {:
            {: a[0][0] + b[0][0], a[0][1] + b[0][1]},
            {: a[1][0] + b[1][0], a[1][1] + b[1][1]}}

poly fun add(a mat3, b mat3) mat3:
    return {:
            {: a[0][0] + b[0][0], a[0][1] + b[0][1], a[0][2] + b[0][2]},
            {: a[1][0] + b[1][0], a[1][1] + b[1][1], a[1][2] + b[1][2]},
            {: a[2][0] + b[2][0], a[2][1] + b[2][1], a[2][2] + b[2][2]}}

poly fun add(a mat4, b mat4) mat4:
    return {:
            {: a[0][0] + b[0][0], a[0][1] + b[0][1], a[0][2] + b[0][2],
             a[0][3] + b[0][3]},
            {: a[1][0] + b[1][0], a[1][1] + b[1][1], a[1][2] + b[1][2],
             a[1][3] + b[1][3]},
            {: a[2][0] + b[2][0], a[2][1] + b[2][1], a[2][2] + b[2][2],
             a[2][3] + b[2][3]},
            {: a[3][0] + b[3][0], a[3][1] + b[3][1], a[3][2] + b[3][2],
             a[3][3] + b[3][3]}}

;
poly pub fun pmax(a vec2, b vec2) vec2:
    return {: max(a[0], b[0]), max(a[1], b[1])}

poly fun pmax(a vec3, b vec3) vec3:
    return {: max(a[0], b[0]), max(a[1], b[1]), max(a[2], b[2])}

poly fun pmax(a vec4, b vec4) vec4:
    return {: max(a[0], b[0]), max(a[1], b[1]), max(a[2], b[2]), max(a[3], b[3])
            }

;
poly pub fun pmin(a vec2, b vec2) vec2:
    return {: min(a[0], b[0]), min(a[1], b[1])}

poly fun pmin(a vec3, b vec3) vec3:
    return {: min(a[0], b[0]), min(a[1], b[1]), min(a[2], b[2])}

poly fun pmin(a vec4, b vec4) vec4:
    return {: min(a[0], b[0]), min(a[1], b[1]), min(a[2], b[2]), min(a[3], b[3])
            }

;
poly pub fun cross(a vec3, b vec3) vec3:
    return {: a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2],
            a[0] * b[1] - a[1] * b[0]}

;
poly pub fun dot(a vec2, b vec2) $T:
    return a[0] * b[0] + a[1] * b[1]

poly fun dot(a vec3, b vec3) $T:
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]

poly fun dot(a vec4, b vec4) $T:
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2] + a[3] * b[3]

; b is interpreted as a column vec and the result is a column vec
poly pub fun mulmv(a mat2, b vec2) vec2:
    return {: a[0][0] * b[0] + a[0][1] * b[1], a[1][0] * b[0] + a[1][1] * b[1]}

; a is interpreted as a row vec and the result is a row vec
poly pub fun mulvm(b vec2, a mat2) vec2:
    return {: a[0][0] * b[0] + a[1][0] * b[1], a[0][1] * b[0] + a[1][1] * b[1]}

poly pub fun mulmm(a mat2, b mat2) mat2:
    return {:
            {: a[0][0] * b[0][0] + a[0][1] * b[1][0],
             a[0][0] * b[0][1] + a[0][1] * b[1][1]},
            {: a[1][0] * b[0][0] + a[1][1] * b[1][0],
             a[1][0] * b[0][1] + a[1][1] * b[1][1]}}

poly fun mulmv(a mat3, b vec3) vec3:
    return {: a[0][0] * b[0] + a[0][1] * b[1] + a[0][2] * b[2],
            a[1][0] * b[0] + a[1][1] * b[1] + a[1][2] * b[2],
            a[2][0] * b[0] + a[2][1] * b[1] + a[2][2] * b[2]}

; a is interpreted as a row vec and the result is a row vec
poly fun mulvm(b vec3, a mat3) vec3:
    return {: a[0][0] * b[0] + a[1][0] * b[1] + a[2][0] * b[2],
            a[0][1] * b[0] + a[1][1] * b[1] + a[2][1] * b[2],
            a[0][2] * b[0] + a[1][2] * b[1] + a[2][2] * b[2]}

poly fun mulmm(a mat3, b mat3) mat3:
    return {:
            {: a[0][0] * b[0][0] + a[0][1] * b[1][0] + a[0][2] * b[2][0],
             a[0][0] * b[0][1] + a[0][1] * b[1][1] + a[0][2] * b[2][1],
             a[0][0] * b[0][2] + a[0][1] * b[1][2] + a[0][2] * b[2][2]},
            {: a[1][0] * b[0][0] + a[1][1] * b[1][0] + a[1][2] * b[2][0],
             a[1][0] * b[0][1] + a[1][1] * b[1][1] + a[1][2] * b[2][1],
             a[1][0] * b[0][2] + a[1][1] * b[1][2] + a[1][2] * b[2][2]},
            {: a[2][0] * b[0][0] + a[2][1] * b[1][0] + a[2][2] * b[2][0],
             a[2][0] * b[0][1] + a[2][1] * b[1][1] + a[2][2] * b[2][1],
             a[2][0] * b[0][2] + a[2][1] * b[1][2] + a[2][2] * b[2][2]}}

;
poly pub fun sub(a vec2, b vec2) vec2:
    return {: a[0] - b[0], a[1] - b[1]}

poly fun sub(a vec3, b vec3) vec3:
    return {: a[0] - b[0], a[1] - b[1], a[2] - b[2]}

poly fun sub(a vec4, b vec4) vec4:
    return {: a[0] - b[0], a[1] - b[1], a[2] - b[2], a[3] - b[3]}

poly fun sub(a mat2, b mat2) mat2:
    return {:
            {: a[0][0] - b[0][0], a[0][1] - b[0][1]},
            {: a[1][0] - b[1][0], a[1][1] - b[1][1]}}

poly fun sub(a mat3, b mat3) mat3:
    return {:
            {: a[0][0] - b[0][0], a[0][1] - b[0][1], a[0][2] - b[0][2]},
            {: a[1][0] - b[1][0], a[1][1] - b[1][1], a[1][2] - b[1][2]},
            {: a[2][0] - b[2][0], a[2][1] - b[2][1], a[2][2] - b[2][2]}}

poly fun sub(a mat4, b mat4) mat4:
    return {:
            {: a[0][0] - b[0][0], a[0][1] - b[0][1], a[0][2] - b[0][2],
             a[0][3] - b[0][3]},
            {: a[1][0] - b[1][0], a[1][1] - b[1][1], a[1][2] - b[1][2],
             a[1][3] - b[1][3]},
            {: a[2][0] - b[2][0], a[2][1] - b[2][1], a[2][2] - b[2][2],
             a[2][3] - b[2][3]},
            {: a[3][0] - b[3][0], a[3][1] - b[3][1], a[3][2] - b[3][2],
             a[3][3] - b[3][3]}}

;
poly pub fun normalized(a vec2) vec2:
    let x = a[0]
    let y = a[1]
    let li $T = 1.0 / sqrt(x * x + y * y)
    return {: x * li, y * li}

poly fun normalized(a vec3) vec3:
    let x = a[0]
    let y = a[1]
    let z = a[2]
    let li $T = 1.0 / sqrt(x * x + y * y + z * z)
    return {: x * li, y * li, z * li}

poly fun normalized(a vec4) vec4:
    let x = a[0]
    let y = a[1]
    let z = a[2]
    let w = a[3]
    let li $T = 1.0 / sqrt(x * x + y * y + z * z + w * w)
    return {: x * li, y * li, z * li, w * li}

;
poly pub fun scaled(b vec2, a $T) vec2:
    return {: a * b[0], a * b[1]}

poly fun scaled(b vec3, a $T) vec3:
    return {: a * b[0], a * b[1], a * b[2]}

poly fun scaled(b vec4, a $T) vec4:
    return {: a * b[0], a * b[1], a * b[2], a * b[3]}

poly fun scaled(b mat2, a $T) mat2:
    return {:
            {: a * b[0][0], a * b[0][1]}, {: a * b[1][0], a * b[1][1]}}

poly fun scaled(b mat3, a $T) mat3:
    return {:
            {: a * b[0][0], a * b[0][1], a * b[0][2]},
            {: a * b[1][0], a * b[1][1], a * b[1][2]},
            {: a * b[2][0], a * b[2][1], a * b[2][2]}}

poly fun scaled(b mat4, a $T) mat4:
    return {:
            {: a * b[0][0], a * b[0][1], a * b[0][2], a * b[0][3]},
            {: a * b[1][0], a * b[1][1], a * b[1][2], a * b[1][3]},
            {: a * b[2][0], a * b[2][1], a * b[2][2], a * b[2][3]},
            {: a * b[3][0], a * b[3][1], a * b[3][2], a * b[3][3]}}

;
pub global NO_HIT $T = -1

pub rec HitInfo:
    ; distance of hit from ray_origin
    distance $T
    ; position of hit
    position vec3
    ; normal at hit
    normal vec3

poly fun fmt\SysRender(v HitInfo, out span!(u8), opt ^!fmt\SysFormatOptions)
  uint:
    let! t = out
    set t = span_inc(t, fmt\SysRender("{", t, opt))
    set t = span_inc(t, fmt\SysRender(v.distance, t, opt))
    set t = span_inc(t, fmt\SysRender(",", t, opt))
    set t = span_inc(t, fmt\SysRender(v.position, t, opt))
    set t = span_inc(t, fmt\SysRender(",", t, opt))
    set t = span_inc(t, fmt\SysRender(v.normal, t, opt))
    set t = span_inc(t, fmt\SysRender("}", t, opt))
    return as(span_diff(t, out), uint)

; returns true if the ray hits the sphere, also fills in out if we have hit
pub fun CheckRayHitsSphere(ray_origin vec3, ray_direction vec3,
                           sphere_center vec3, sphere_radius $T, epsilon $T,
                           out ^!HitInfo) bool:
    let sr2 = sphere_radius * sphere_radius
    let ro2 = dot(ray_origin, ray_origin)
    let rd2 = dot(ray_direction, ray_direction)
    let sc2 = dot(sphere_center, sphere_center)
    ; vector from ray_origin to sphere_center
    let l = sub(ray_origin, sphere_center)
    let a = rd2
    let b = dot(ray_direction, l) * 2.0
    let c = sc2 + ro2 - sr2 - 2.0 * dot(sphere_center, ray_origin)
    let d = b * b - 4.0 * a * c
    if d < 0.0:
        return false
    let sqrt_d = sqrt(d)
    let t1 = (-b + sqrt_d) / 2.0 / a
    let t2 = (-b - sqrt_d) / 2.0 / a
    if t1 < epsilon && t2 < epsilon || t1 > 1.0 && t2 > 1.0:
        ; fmt\print#("EPS ", t1, " ", t2, "\n")
        return false
    let dist $T = expr:
        cond:
            case t1 < epsilon:
                return t2
            case t2 < epsilon:
                return t1
            case true:
                return min(t1, t2)
    ; TODO: maybe handle inside as negative dist
    set out^.distance = dist
    set out^.position = add(ray_origin, scaled(ray_direction, dist))
    set out^.normal =
      scaled(sub(out^.position, sphere_center), 1.0 / sphere_radius)
    return true

pub fun CheckRayHitsSphere2(ray_origin vec3, ray_direction vec3,
                            sphere_center vec3, sphere_radius $T, epsilon $T,
                            out ^!HitInfo) bool:
    return true

pub fun CheckHitRayPlane(ray_origin vec3, ray_direction vec3, plane_point vec3,
                         plane_normal vec3, epsilon $T, out ^HitInfo) bool:
    return true

;
poly fun fmt\SysRender(v vec2, out span!(u8), opt ^!fmt\SysFormatOptions)
  uint:
    let! t = out
    set t = span_inc(t, fmt\SysRender("{", t, opt))
    set t = span_inc(t, fmt\SysRender(v[0], t, opt))
    set t = span_inc(t, fmt\SysRender(",", t, opt))
    set t = span_inc(t, fmt\SysRender(v[1], t, opt))
    set t = span_inc(t, fmt\SysRender("}", t, opt))
    return as(span_diff(t, out), uint)

poly fun fmt\SysRender(v vec3, out span!(u8), opt ^!fmt\SysFormatOptions)
  uint:
    let! t = out
    set t = span_inc(t, fmt\SysRender("{", t, opt))
    set t = span_inc(t, fmt\SysRender(v[0], t, opt))
    set t = span_inc(t, fmt\SysRender(",", t, opt))
    set t = span_inc(t, fmt\SysRender(v[1], t, opt))
    set t = span_inc(t, fmt\SysRender(",", t, opt))
    set t = span_inc(t, fmt\SysRender(v[2], t, opt))
    set t = span_inc(t, fmt\SysRender("}", t, opt))
    return as(span_diff(t, out), uint)

poly fun fmt\SysRender(v vec4, out span!(u8), opt ^!fmt\SysFormatOptions)
  uint:
    let! t = out
    set t = span_inc(t, fmt\SysRender("{", t, opt))
    set t = span_inc(t, fmt\SysRender(v[0], t, opt))
    set t = span_inc(t, fmt\SysRender(",", t, opt))
    set t = span_inc(t, fmt\SysRender(v[1], t, opt))
    set t = span_inc(t, fmt\SysRender(",", t, opt))
    set t = span_inc(t, fmt\SysRender(v[2], t, opt))
    set t = span_inc(t, fmt\SysRender(",", t, opt))
    set t = span_inc(t, fmt\SysRender(v[3], t, opt))
    set t = span_inc(t, fmt\SysRender("}", t, opt))
    return as(span_diff(t, out), uint)

poly fun fmt\SysRender(v mat2, out span!(u8), opt ^!fmt\SysFormatOptions)
  uint:
    let! t = out
    set t = span_inc(t, fmt\SysRender("{", t, opt))
    set t = span_inc(t, fmt\SysRender(v[0], t, opt))
    set t = span_inc(t, fmt\SysRender(",", t, opt))
    set t = span_inc(t, fmt\SysRender(v[1], t, opt))
    set t = span_inc(t, fmt\SysRender("}", t, opt))
    return as(span_diff(t, out), uint)

poly fun fmt\SysRender(v mat3, out span!(u8), opt ^!fmt\SysFormatOptions)
  uint:
    let! t = out
    set t = span_inc(t, fmt\SysRender("{", t, opt))
    set t = span_inc(t, fmt\SysRender(v[0], t, opt))
    set t = span_inc(t, fmt\SysRender(",", t, opt))
    set t = span_inc(t, fmt\SysRender(v[1], t, opt))
    set t = span_inc(t, fmt\SysRender(",", t, opt))
    set t = span_inc(t, fmt\SysRender(v[2], t, opt))
    set t = span_inc(t, fmt\SysRender("}", t, opt))
    return as(span_diff(t, out), uint)

poly fun fmt\SysRender(v mat4, out span!(u8), opt ^!fmt\SysFormatOptions)
  uint:
    let! t = out
    set t = span_inc(t, fmt\SysRender("{", t, opt))
    set t = span_inc(t, fmt\SysRender(v[0], t, opt))
    set t = span_inc(t, fmt\SysRender(",", t, opt))
    set t = span_inc(t, fmt\SysRender(v[1], t, opt))
    set t = span_inc(t, fmt\SysRender(",", t, opt))
    set t = span_inc(t, fmt\SysRender(v[2], t, opt))
    set t = span_inc(t, fmt\SysRender(",", t, opt))
    set t = span_inc(t, fmt\SysRender(v[3], t, opt))
    set t = span_inc(t, fmt\SysRender("}", t, opt))
    return as(span_diff(t, out), uint)
