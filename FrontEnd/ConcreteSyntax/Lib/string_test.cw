module:

import test

import string

global STR_ABC = "ABC"

global STR_ABCD = "ABCD"

global STR_CD = "CD"

global STR_XYZ = "XYZ"

global STR_VXYZ = "VXYZ"

global STR_EMPTY = ""

global STR_TEST = "TEST\n"

@cdecl fun main(argc s32, argv ^^u8) s32:
    -- find
    test::AssertEq#(string::NOT_FOUND, string::find(STR_ABC, STR_ABCD))
    test::AssertEq#(0_uint, string::find(STR_ABCD, STR_ABC))
    test::AssertEq#(1_uint, string::find(STR_VXYZ, STR_XYZ))
    test::AssertEq#(2_uint, string::find(STR_ABCD, STR_CD))
    test::AssertEq#(string::NOT_FOUND, string::find(STR_XYZ, STR_VXYZ))
    -- rfind
    test::AssertEq#(string::NOT_FOUND, string::rfind(STR_ABC, STR_ABCD))
    test::AssertEq#(0_uint, string::rfind(STR_ABCD, STR_ABC))
    test::AssertEq#(1_uint, string::rfind(STR_VXYZ, STR_XYZ))
    test::AssertEq#(2_uint, string::rfind(STR_ABCD, STR_CD))
    test::AssertEq#(string::NOT_FOUND, string::find(STR_ABC, STR_ABCD))
    -- cmp
    test::AssertEq#(0_sint, string::cmp(STR_ABCD, STR_ABCD))
    test::AssertEq#(-1_sint, string::cmp(STR_ABC, STR_ABCD))
    test::AssertEq#(1_sint, string::cmp(STR_ABCD, STR_ABC))
    test::AssertEq#(-1_sint, string::cmp(STR_ABC, STR_XYZ))
    test::AssertEq#(1_sint, string::cmp(STR_XYZ, STR_ABC))
    -- starts_with
    test::AssertEq#(false, string::starts_with(STR_ABC, STR_ABCD))
    test::AssertEq#(true, string::starts_with(STR_ABCD, STR_ABC))
    test::AssertEq#(false, string::starts_with(STR_VXYZ, STR_XYZ))
    test::AssertEq#(false, string::starts_with(STR_ABCD, STR_CD))
    test::AssertEq#(false, string::starts_with(STR_XYZ, STR_VXYZ))
    -- ends_with
    test::AssertEq#(false, string::ends_with(STR_ABC, STR_ABCD))
    test::AssertEq#(false, string::ends_with(STR_ABCD, STR_ABC))
    test::AssertEq#(true, string::ends_with(STR_VXYZ, STR_XYZ))
    test::AssertEq#(true, string::ends_with(STR_ABCD, STR_CD))
    test::AssertEq#(false, string::ends_with(STR_XYZ, STR_VXYZ))
    -- find_first_of
    test::AssertEq#(0_uint, string::find_first_of(STR_ABC, STR_ABCD))
    test::AssertEq#(2_uint, string::find_first_of(STR_ABC, STR_CD))
    test::AssertEq#(string::NOT_FOUND, string::find_first_of(STR_ABC, STR_XYZ))
    test::AssertEq#(string::NOT_FOUND, string::find_first_of(STR_EMPTY, STR_XYZ))
    test::AssertEq#(string::NOT_FOUND, string::find_first_of(STR_ABC, STR_EMPTY))
    -- find_first_not_of
    test::AssertEq#(3_uint, string::find_first_not_of(STR_ABCD, STR_ABC))
    test::AssertEq#(0_uint, string::find_first_not_of(STR_ABC, STR_CD))
    test::AssertEq#(0_uint, string::find_first_not_of(STR_ABC, STR_XYZ))
    test::AssertEq#(
            string::NOT_FOUND, string::find_first_not_of(STR_EMPTY, STR_XYZ))
    test::AssertEq#(0_uint, string::find_first_not_of(STR_ABC, STR_EMPTY))
    -- find_last_of
    test::AssertEq#(2_uint, string::find_last_of(STR_ABCD, STR_ABC))
    test::AssertEq#(2_uint, string::find_last_of(STR_ABC, STR_CD))
    test::AssertEq#(string::NOT_FOUND, string::find_last_of(STR_ABC, STR_XYZ))
    test::AssertEq#(string::NOT_FOUND, string::find_last_of(STR_EMPTY, STR_XYZ))
    test::AssertEq#(string::NOT_FOUND, string::find_last_of(STR_ABC, STR_EMPTY))
    -- find_last_not_of
    test::AssertEq#(3_uint, string::find_last_not_of(STR_ABCD, STR_ABC))
    test::AssertEq#(1_uint, string::find_last_not_of(STR_ABC, STR_CD))
    test::AssertEq#(2_uint, string::find_last_not_of(STR_ABC, STR_XYZ))
    test::AssertEq#(
            string::NOT_FOUND, string::find_last_not_of(STR_EMPTY, STR_XYZ))
    test::AssertEq#(2_uint, string::find_last_not_of(STR_ABC, STR_EMPTY))
    -- test end
    test::Success#()
    return 0
