module:

import fmt
import jp = json_parser
import test

global test_empty = ""

global test_val_num = """ 0 """
global test_val_bool = """ false """
global test_val_str = """ "str" """
global test_val_str_esc = """ "str\"" """

global test_vec_empty = """[]"""
global test_vec_simple = """[100, 500, 300, 200, 400 ]"""

global test_dict_empty = """{}"""
global test_dict_simple = """{"ip": "8.8.8.8"}"""

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
    test::AssertEq#(jp::NumJsonObjectsNeeded(test_val_bool), 1_u32)
    test::AssertEq#(jp::NumJsonObjectsNeeded(test_val_num), 1_u32)
    test::AssertEq#(jp::NumJsonObjectsNeeded(test_val_str), 1_u32)
    test::AssertEq#(jp::NumJsonObjectsNeeded(test_dict_empty), 1_u32)
    test::AssertEq#(jp::NumJsonObjectsNeeded(test_dict_simple), 4_u32)
    test::AssertEq#(jp::NumJsonObjectsNeeded(test_vec_empty), 1_u32)
    test::AssertEq#(jp::NumJsonObjectsNeeded(test_vec_simple), 11_u32)
    test::AssertEq#(jp::NumJsonObjectsNeeded(test2), 10_u32)
    test::AssertEq#(jp::NumJsonObjectsNeeded(test4), 12_u32)
    test::AssertEq#(jp::NumJsonObjectsNeeded(test5), 23_u32)
    test::AssertEq#(jp::NumJsonObjectsNeeded(test6), 103_u32)

fun test_parser() void:
    let! objects = [200]jp::Object{}
    @ref let! file jp::File
    --
    set file = jp::File{test_empty, objects}
    test::AssertIs#(jp::Parse(&!file), jp::DataError)
    --
    set file = jp::File{test_val_num, objects}
    test::AssertIs#(jp::Parse(&!file), jp::Success)
    test::AssertEq#(file.used_objects,
                    jp::NumJsonObjectsNeeded(test_val_num))
    test::AssertEq#(jp::IndexKind(file.root), jp::ObjKind:Val)
    --
    set file = jp::File{test_val_bool, objects}
    test::AssertIs#(jp::Parse(&!file), jp::Success)
    test::AssertEq#(file.used_objects,
                   jp::NumJsonObjectsNeeded(test_val_bool))
    test::AssertEq#(jp::IndexKind(file.root), jp::ObjKind:Val)
    --
    set file = jp::File{test_val_str, objects}
    test::AssertIs#(jp::Parse(&!file), jp::Success)
    test::AssertEq#(file.used_objects,
                    jp::NumJsonObjectsNeeded(test_val_str))
    test::AssertEq#(jp::IndexKind(file.root), jp::ObjKind:Val)
    --
    set file = jp::File{test_vec_empty, objects}
    test::AssertIs#(jp::Parse(&!file), jp::Success)
    test::AssertEq#(file.used_objects,
                    jp::NumJsonObjectsNeeded(test_vec_empty))
    test::AssertEq#(jp::IndexKind(file.root), jp::ObjKind:Vec)
    --
    set file = jp::File{test_vec_simple, objects}
    test::AssertIs#(jp::Parse(&!file), jp::Success)
    test::AssertEq#(file.used_objects,
                    jp::NumJsonObjectsNeeded(test_vec_simple))
    test::AssertEq#(jp::IndexKind(file.root), jp::ObjKind:Vec)
    --
    set file = jp::File{test_dict_empty, objects}
    test::AssertIs#(jp::Parse(&!file), jp::Success)
    test::AssertEq#(file.used_objects,
                    jp::NumJsonObjectsNeeded(test_dict_empty))
    test::AssertEq#(jp::IndexKind(file.root), jp::ObjKind:Dict)
    --
    set file = jp::File{test_dict_simple, objects}
    test::AssertIs#(jp::Parse(&!file), jp::Success)
    test::AssertEq#(file.used_objects,
                    jp::NumJsonObjectsNeeded(test_dict_simple))
    test::AssertEq#(jp::IndexKind(file.root), jp::ObjKind:Dict)

fun main(argc s32, argv ^^u8) s32:
    do test_counter()
    do test_parser()

    test::Success#()
    return 0