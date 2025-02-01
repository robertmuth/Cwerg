; permute benchmark adapted from https://github.com/smarr/are-we-fast-yet/
; Note: some changes from the original to actually produce permutations
module:

import test

global DIM = 7_s32

global! COUNT = 0_u32

fun swapit(v ^![DIM]s32, i s32, j s32) void:
    let t = v^[i]
    set v^[i] = v^[j]
    set v^[j] = t

fun permute(v ^![DIM]s32, n s32) void:
    ; Note: some changes to actually produce permutations
    if n == 0:
        set COUNT += 1
        return
    let n1 = n - 1
    for i = n1, -1_s32, -1:
        do swapit(v, n1, i)
        do permute(v, n1)
        do swapit(v, n1, i)

fun main(argc s32, argv ^^u8) s32:
    ref let! v = {[DIM]s32:}
    do permute(@!v, DIM)
    ; DIM! = 5040
    test::AssertEq#(COUNT, 5040_u32)
    test::Success#()
    return 0
