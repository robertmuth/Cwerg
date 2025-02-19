module:

import test

fun assoc1(a u32, b u32, c u32, d u32) u32:
    return a + b - c + d

fun assoc2(a u32, b u32, c u32, d u32) u32:
    return (a + b) * (c + d)

fun assoc3(a u32, b u32, c u32, d u32) u32:
    return max(min(a, b), min(c, d))

fun sign1(x s32) s32:
    cond:
        case x == 0:
            return 0_s32
        case x < 0:
            return -1_s32
        case true:
            return 1_s32

fun sign2(x s32) s32:
    let out s32 = expr:
        cond:
            case x == 0:
                return 0_s32
            case x < 0:
                return -1_s32
            case true:
                return 1_s32
    return out

fun sign3(x s32) s32:
    return expr:
        cond:
            case x == 0:
                return 0_s32
            case x < 0:
                return -1_s32
            case true:
                return 1_s32

fun main(argc s32, argv ^^u8) s32:
    test::AssertEq#(assoc3(5, 7, 1, 2), 5_u32)
    ;
    test::AssertEq#(sign1(20), 1_s32)
    test::AssertEq#(sign2(20), 1_s32)
    test::AssertEq#(sign3(20), 1_s32)
    ;
    test::AssertEq#(sign1(0), 0_s32)
    test::AssertEq#(sign2(0), 0_s32)
    test::AssertEq#(sign3(0), 0_s32)
    ;
    test::AssertEq#(sign1(-20), -1_s32)
    test::AssertEq#(sign2(-20), -1_s32)
    test::AssertEq#(sign3(-20), -1_s32)
    ; test end
    test::Success#()
    return 0
