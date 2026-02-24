module:

import test


poly pub fun foo(a bool) u32:
    return 1

poly pub fun foo(a u8) u32:
    return 2

poly pub fun foo(a u16) u32:
    return 3

poly pub fun foo(a u32) u32:
    return 4

poly pub fun foo(a u64) u32:
    return 5

fun test_poly() void:
    let! res u32 = undef
    set res = foo(true)
    test\AssertEq#(res, 1_u32)
    set res = foo(1_u8)
    test\AssertEq#(res, 2_u32)
    set res = foo(2_u16)
    test\AssertEq#(res, 3_u32)
    set res = foo(3_u32)
    test\AssertEq#(res, 4_u32)
    set res = foo(4_u64)
    test\AssertEq#(res, 5_u32)


fun bar1() u32:
    return 1

fun bar2() u32:
    return 2

fun bar3() u32:
    return 3

fun bar4() u32:
    return 4

fun bar5() u32:
    return 5

type funptr = funtype() u32


pub rec rec_funptr:
    fp1 funptr
    fp2 funptr
    fp3 funptr


global! global_funptr = bar3

fun test_simple() void:
    let! res u32 = undef
    set res = bar1()
    test\AssertEq#(res, 1_u32)
    set res = bar2()
    test\AssertEq#(res, 2_u32)
    ; indirect local var
    let! local_funptr = bar3
    set res = local_funptr()
    test\AssertEq#(local_funptr, bar3)
    test\AssertNe#(local_funptr, bar4)
    test\AssertEq#(res, 3_u32)
    ;
    set local_funptr = bar4
    test\AssertEq#(local_funptr, bar4)
    test\AssertNe#(local_funptr, bar3)
    set res = local_funptr()
    test\AssertEq#(res, 4_u32)
    ; indirect global var
    set global_funptr = bar3
    test\AssertEq#(global_funptr, bar3)
    test\AssertNe#(global_funptr, bar4)
    set res = global_funptr()
    test\AssertEq#(res, 3_u32)
    ;
    set global_funptr = bar4
    test\AssertEq#(global_funptr, bar4)
    test\AssertNe#(global_funptr, bar3)
    set res = global_funptr()
    test\AssertEq#(res, 4_u32)
    ;
    let! r = {rec_funptr: bar5, bar4, bar3}
    set res = r.fp1()
    test\AssertEq#(res, 5_u32)
    set res = r.fp2()
    test\AssertEq#(res, 4_u32)
    set res = r.fp3()
    test\AssertEq#(res, 3_u32)

fun main(argc s32, argv ^^u8) s32:
    do test_simple()
    do test_poly()
    ; test end
    test\Success#()
    return 0
