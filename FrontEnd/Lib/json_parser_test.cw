module:

import fmt
import jp = json_parser
import test

global test_empty = ""

global test_leaf_num = """ 0 """
global test_leaf_bool = """ false """
global test_leaf_str = """ "str" """


global test_vec_simple = """[100, 500, 300, 200, 400 ]"""


global test1 = """{"ip": "8.8.8.8"}"""

global test2 = """ {
   "string": "string",
   "bool": false,
   "num": 127664,
} """



global test4 = """[
    {
        "string": "string",
        "bool": false,
        "num": 127664,
    }
]"""

global test5 = """[
    {
        "string": "string",
        "bool": false,
        "num": 127664,
    },
    {
        "string": "string",
        "bool": false,
        "num": 127664,
    }
]"""

global test6 = """
{
   "string": "string",
   "bool": false,
   "num": 127664,
   "array": [ 100, 500, 300, 200, 400 ],
   "dict":
		{
            "string": "string",
            "bool": false,
            "num": 127664,
            "array": [ 100, 500, 300, 200, 400 ],

		},
	"array_of_dict": [
		{
            "string": "string",
            "bool": false,
            "num": 127664,
            "array": [ 100, 500, 300, 200, 400 ],
		},
        {
            "string": "string",
            "bool": false,
            "num": 127664,
            "array": [ 100, 500, 300, 200, 400 ],
        }]
}
"""


fun test_counter() void:
    test::AssertEq#(jp::NumJsonObjectsNeeded(test_leaf_bool), 1_u32)
    test::AssertEq#(jp::NumJsonObjectsNeeded(test_leaf_num), 1_u32)
    test::AssertEq#(jp::NumJsonObjectsNeeded(test_leaf_str), 1_u32)
    test::AssertEq#(jp::NumJsonObjectsNeeded(test1), 3_u32)
    test::AssertEq#(jp::NumJsonObjectsNeeded(test2), 7_u32)
    test::AssertEq#(jp::NumJsonObjectsNeeded(test_vec_simple), 11_u32)
    test::AssertEq#(jp::NumJsonObjectsNeeded(test4), 9_u32)
    test::AssertEq#(jp::NumJsonObjectsNeeded(test5), 17_u32)
    test::AssertEq#(jp::NumJsonObjectsNeeded(test6), 85_u32)

fun test_parser() void:
    let! objects = [100]jp::Object{void}
    @ref let! file jp::File
    --
    set file = jp::File{test_empty, objects}
    test::AssertIs#(jp::FileParse(&!file), jp::DataError)
    --
    set file = jp::File{test_leaf_num, objects}
    test::AssertIs#(jp::FileParse(&!file), jp::Success)
    test::AssertEq#(file.used_objects,
                    jp::NumJsonObjectsNeeded(test_leaf_num))
    test::AssertIs#(file.objects[0], jp::ValNum)
    --
    set file = jp::File{test_leaf_bool, objects}
    test::AssertIs#(jp::FileParse(&!file), jp::Success)
    test::AssertEq#(file.used_objects,
                   jp::NumJsonObjectsNeeded(test_leaf_bool))
    test::AssertIs#(file.objects[0], jp::ValNum)
    --
    set file = jp::File{test_leaf_str, objects}
    test::AssertIs#(jp::FileParse(&!file), jp::Success)
    test::AssertEq#(file.used_objects,
                    jp::NumJsonObjectsNeeded(test_leaf_str))
    test::AssertIs#(file.objects[0], jp::ValStr)

    --
    set file = jp::File{test_vec_simple, objects}
    test::AssertIs#(jp::FileParse(&!file), jp::Success)
    test::AssertEq#(file.used_objects,
                    jp::NumJsonObjectsNeeded(test_vec_simple))
    test::AssertIs#(file.objects[0], jp::Vec)

fun main(argc s32, argv ^^u8) s32:
    do test_counter()
    do test_parser()

    test::Success#()
    return 0