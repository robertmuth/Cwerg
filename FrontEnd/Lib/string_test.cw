(module main [] :
(import test)

(import string)

(global STR_ABC auto "ABC")


(global STR_ABCD auto "ABCD")


(global STR_CD auto "CD")


(global STR_XYZ auto "XYZ")


(global STR_VXYZ auto "VXYZ")


(global STR_EMPTY auto "")


(global STR_TEST auto "TEST\n")


(fun @cdecl main [(param argc s32) (param argv (ptr (ptr u8)))] s32 :
    @doc "find"
    (test::AssertEq string::NOT_FOUND (call string::find [STR_ABC STR_ABCD]))
    (test::AssertEq 0_uint (call string::find [STR_ABCD STR_ABC]))
    (test::AssertEq 1_uint (call string::find [STR_VXYZ STR_XYZ]))
    (test::AssertEq 2_uint (call string::find [STR_ABCD STR_CD]))
    (test::AssertEq string::NOT_FOUND (call string::find [STR_XYZ STR_VXYZ]))
    @doc "rfind"
    (test::AssertEq string::NOT_FOUND (call string::rfind [STR_ABC STR_ABCD]))
    (test::AssertEq 0_uint (call string::rfind [STR_ABCD STR_ABC]))
    (test::AssertEq 1_uint (call string::rfind [STR_VXYZ STR_XYZ]))
    (test::AssertEq 2_uint (call string::rfind [STR_ABCD STR_CD]))
    (test::AssertEq string::NOT_FOUND (call string::find [STR_ABC STR_ABCD]))
    @doc  "cmp"
    (test::AssertEq 0_sint (call string::cmp [STR_ABCD STR_ABCD]))
    (test::AssertEq -1_sint (call string::cmp [STR_ABC STR_ABCD]))
    (test::AssertEq 1_sint (call string::cmp [STR_ABCD STR_ABC]))
    (test::AssertEq -1_sint (call string::cmp [STR_ABC STR_XYZ]))
    (test::AssertEq 1_sint (call string::cmp [STR_XYZ STR_ABC]))
    @doc "starts_with"
    (test::AssertEq false (call string::starts_with [STR_ABC STR_ABCD]))
    (test::AssertEq true (call string::starts_with [STR_ABCD STR_ABC]))
    (test::AssertEq false (call string::starts_with [STR_VXYZ STR_XYZ]))
    (test::AssertEq false (call string::starts_with [STR_ABCD STR_CD]))
    (test::AssertEq false (call string::starts_with [STR_XYZ STR_VXYZ]))
    @doc "ends_with"
    (test::AssertEq false (call string::ends_with [STR_ABC STR_ABCD]))
    (test::AssertEq false (call string::ends_with [STR_ABCD STR_ABC]))
    (test::AssertEq true (call string::ends_with [STR_VXYZ STR_XYZ]))
    (test::AssertEq true (call string::ends_with [STR_ABCD STR_CD]))
    (test::AssertEq false (call string::ends_with [STR_XYZ STR_VXYZ]))
    @doc "find_first_of"
    (test::AssertEq 0_uint (call string::find_first_of [STR_ABC STR_ABCD]))
    (test::AssertEq 2_uint (call string::find_first_of [STR_ABC STR_CD]))
    (test::AssertEq string::NOT_FOUND (call string::find_first_of [STR_ABC STR_XYZ]))
    (test::AssertEq string::NOT_FOUND (call string::find_first_of [STR_EMPTY STR_XYZ]))
    (test::AssertEq string::NOT_FOUND (call string::find_first_of [STR_ABC STR_EMPTY]))
    @doc "find_first_not_of"
    (test::AssertEq 3_uint (call string::find_first_not_of [STR_ABCD STR_ABC]))
    (test::AssertEq 0_uint (call string::find_first_not_of [STR_ABC STR_CD]))
    (test::AssertEq 0_uint (call string::find_first_not_of [STR_ABC STR_XYZ]))
    (test::AssertEq string::NOT_FOUND (call string::find_first_not_of [STR_EMPTY STR_XYZ]))
    (test::AssertEq 0_uint (call string::find_first_not_of [STR_ABC STR_EMPTY]))
    @doc "find_last_of"
    (test::AssertEq 2_uint (call string::find_last_of [STR_ABCD STR_ABC]))
    (test::AssertEq 2_uint (call string::find_last_of [STR_ABC STR_CD]))
    (test::AssertEq string::NOT_FOUND (call string::find_last_of [STR_ABC STR_XYZ]))
    (test::AssertEq string::NOT_FOUND (call string::find_last_of [STR_EMPTY STR_XYZ]))
    (test::AssertEq string::NOT_FOUND (call string::find_last_of [STR_ABC STR_EMPTY]))
    @doc "find_last_not_of"
    (test::AssertEq 3_uint (call string::find_last_not_of [STR_ABCD STR_ABC]))
    (test::AssertEq 1_uint (call string::find_last_not_of [STR_ABC STR_CD]))
    (test::AssertEq 2_uint (call string::find_last_not_of [STR_ABC STR_XYZ]))
    (test::AssertEq string::NOT_FOUND (call string::find_last_not_of [STR_EMPTY STR_XYZ]))
    (test::AssertEq 2_uint (call string::find_last_not_of [STR_ABC STR_EMPTY]))
    @doc "test end"
    (test::Success)
    (return 0))

)


