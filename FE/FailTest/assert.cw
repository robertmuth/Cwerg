module:

import test

fun main(argc s32, argv ^^u8) s32:
    test::AssertEq#(0_uint, 1_uint)
    test::Success#()
    return 0