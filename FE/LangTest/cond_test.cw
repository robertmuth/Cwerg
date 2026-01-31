module:

import test

global! prime = {[16]u32: 1, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53}

global! global_var = true

fun test_simple() void:
    ; 3
    let! a = prime[1]
    ; 5
    let! b = prime[2]
    let! c u32 = undef
    if a < b:
       set c = 1
    else:
       set c = 2
    test::AssertEq#(c, 1_u32)

    if global_var:
        set c = 555

    test::AssertEq#(c, 555_u32)

    let! ref stack_var = global_var
    if stack_var:
        set c = 666
    test::AssertEq#(c, 666_u32)


fun main(argc s32, argv ^^u8) s32:
    do test_simple()
    ; test end
    test::Success#()
    return 0
