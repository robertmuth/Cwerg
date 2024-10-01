@doc "BigInts: fixed with and eventually variable widths"
(module [] :

@pub (global CLEAR_ALL auto "\x1b[2J")


(type b_u128 (vec 2 u64))


(type b_u256 (vec 4 u64))


@pub (fun add_b_u128 [(param x b_u128) (param y b_u128)] b_u128 :
    (let z0 auto (+ (at x 0) (at y 0)))
    (let z1 auto (+ (at x 1) (at y 1)))
    (let carry auto (? (< z0 (at x 0)) 1_u64 0_u64))
    (return (vec_val 2 u64 [z0 (+ z1 carry)])))


@pub (fun mul_u64_by_u64_to_b_u128 [(param x u64) (param y u64)] b_u128 :
    (let x0 auto (as (as x u32) u64))
    (let x1 auto (>> x 32))
    (let y0 auto (as (as y u32) u64))
    (let y1 auto (>> y 32))
    (let p00 auto (* x0 y0))
    (let p01 auto (* x0 y1))
    (let p10 auto (* x1 y0))
    (let p11 auto (* x1 y1))
    @doc """we would like to use
middle =  p10 + p00 >> 32 +  p10
but this might cause an overflow in the high bits"""
    (let middle0 auto (+ (+ p10 (>> p00 32)) (as (as p01 u32) u64)))
    @doc "add missing component after shifting to right"
    (let middle1 auto (+ (>> middle0 32) (>> p01 32)))
    (return (vec_val 2 u64 [(or (as (as p00 u32) u64) (<< middle0 32)) (+ p11 middle1)])))
)

