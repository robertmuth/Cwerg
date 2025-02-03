module:

import fmt

import jp = json_parser

import test

global test_empty = ""

global test_val_num = """ 0 """

global test_val_bool = """ false """

global test_val_str = """ "str" """

global test_val_str_esc = r""" "str\"" """

fun test_simple() void:
    test::AssertEq#(jp::NumJsonObjectsNeeded(test_val_bool), 1_u32)
    test::AssertEq#(jp::NumJsonObjectsNeeded(test_val_num), 1_u32)
    test::AssertEq#(jp::NumJsonObjectsNeeded(test_val_str), 1_u32)
    ;
    let! objects = {[200]jp::Object:}
    ref let! file jp::File
    ;
    set file = {jp::File: test_empty, objects}
    test::AssertIs#(jp::Parse(@!file), jp::DataError)
    ;
    set file = {jp::File: test_val_num, objects}
    test::AssertIs#(jp::Parse(@!file), jp::Success)
    test::AssertEq#(file.used_objects, jp::NumJsonObjectsNeeded(test_val_num))
    test::AssertEq#(jp::IndexGetKind(file.root), jp::ObjKind:Atom)
    test::AssertEq#(jp::AtomGetKind(@file, file.root), jp::AtomKind:Num)
    test::AssertSliceEq#(jp::AtomGetData(@file, file.root), "0")
    ;
    set file = {jp::File: test_val_bool, objects}
    test::AssertIs#(jp::Parse(@!file), jp::Success)
    test::AssertEq#(file.used_objects, jp::NumJsonObjectsNeeded(test_val_bool))
    test::AssertEq#(jp::IndexGetKind(file.root), jp::ObjKind:Atom)
    test::AssertEq#(jp::AtomGetKind(@file, file.root), jp::AtomKind:Num)
    test::AssertSliceEq#(jp::AtomGetData(@file, file.root), "false")
    ;
    set file = {jp::File: test_val_str, objects}
    test::AssertIs#(jp::Parse(@!file), jp::Success)
    test::AssertEq#(file.used_objects, jp::NumJsonObjectsNeeded(test_val_str))
    test::AssertEq#(jp::IndexGetKind(file.root), jp::ObjKind:Atom)
    test::AssertEq#(jp::AtomGetKind(@file, file.root), jp::AtomKind:Str)
    test::AssertSliceEq#(jp::AtomGetData(@file, file.root), "str")
    ;
    set file = {jp::File: test_val_str_esc, objects}
    test::AssertIs#(jp::Parse(@!file), jp::Success)
    test::AssertEq#(
            file.used_objects, jp::NumJsonObjectsNeeded(test_val_str_esc))
    test::AssertEq#(jp::IndexGetKind(file.root), jp::ObjKind:Atom)
    test::AssertEq#(jp::AtomGetKind(@file, file.root), jp::AtomKind:EscStr)
    test::AssertSliceEq#(jp::AtomGetData(@file, file.root), "str\\\"")

global test_dict_empty = """{}"""

global test_dict_simple = """{"ip": "8.8.8.8"}"""

global test_dict_small = """ {
   "string": "string",
   "bool": false,
   "num": 127664
} """

fun test_dict() void:
    test::AssertEq#(jp::NumJsonObjectsNeeded(test_dict_empty), 1_u32)
    test::AssertEq#(jp::NumJsonObjectsNeeded(test_dict_simple), 4_u32)
    test::AssertEq#(jp::NumJsonObjectsNeeded(test_dict_small), 10_u32)
    ;
    let! objects = {[200]jp::Object:}
    ref let! file jp::File
    ;
    set file = {jp::File: test_dict_empty, objects}
    test::AssertIs#(jp::Parse(@!file), jp::Success)
    test::AssertEq#(
            file.used_objects, jp::NumJsonObjectsNeeded(test_dict_empty))
    test::AssertEq#(jp::IndexGetKind(file.root), jp::ObjKind:Cont)
    test::AssertEq#(jp::ContGetKind(@file, file.root), jp::ContKind:Dict)
    ;
    set file = {jp::File: test_dict_simple, objects}
    test::AssertIs#(jp::Parse(@!file), jp::Success)
    test::AssertEq#(
            file.used_objects, jp::NumJsonObjectsNeeded(test_dict_simple))
    test::AssertEq#(jp::IndexGetKind(file.root), jp::ObjKind:Cont)
    test::AssertEq#(jp::ContGetKind(@file, file.root), jp::ContKind:Dict)
    ;
    set file = {jp::File: test_dict_small, objects}
    test::AssertIs#(jp::Parse(@!file), jp::Success)
    test::AssertEq#(
            file.used_objects, jp::NumJsonObjectsNeeded(test_dict_small))
    test::AssertEq#(jp::IndexGetKind(file.root), jp::ObjKind:Cont)
    test::AssertEq#(jp::ContGetKind(@file, file.root), jp::ContKind:Dict)

global test_vec_empty = """[]"""

global test_vec_simple = """[100]"""

global test_vec_small = """[100, 500, 300, 200, 400 ]"""

fun test_vec() void:
    test::AssertEq#(jp::NumJsonObjectsNeeded(test_vec_empty), 1_u32)
    test::AssertEq#(jp::NumJsonObjectsNeeded(test_vec_simple), 3_u32)
    test::AssertEq#(jp::NumJsonObjectsNeeded(test_vec_small), 11_u32)
    ;
    let! objects = {[200]jp::Object:}
    ref let! file jp::File
    ;
    set file = {jp::File: test_vec_empty, objects}
    test::AssertIs#(jp::Parse(@!file), jp::Success)
    test::AssertEq#(file.used_objects, jp::NumJsonObjectsNeeded(test_vec_empty))
    test::AssertEq#(jp::IndexGetKind(file.root), jp::ObjKind:Cont)
    test::AssertEq#(jp::ContGetKind(@file, file.root), jp::ContKind:Vec)
    test::AssertEq#(jp::ContGetSize(@file, file.root), 0_u32)
    ;
    set file = {jp::File: test_vec_simple, objects}
    test::AssertIs#(jp::Parse(@!file), jp::Success)
    test::AssertEq#(
            file.used_objects, jp::NumJsonObjectsNeeded(test_vec_simple))
    test::AssertEq#(jp::IndexGetKind(file.root), jp::ObjKind:Cont)
    test::AssertEq#(jp::ContGetKind(@file, file.root), jp::ContKind:Vec)
    test::AssertEq#(jp::ContGetSize(@file, file.root), 1_u32)
    ;
    set file = {jp::File: test_vec_small, objects}
    test::AssertIs#(jp::Parse(@!file), jp::Success)
    test::AssertEq#(file.used_objects, jp::NumJsonObjectsNeeded(test_vec_small))
    test::AssertEq#(jp::IndexGetKind(file.root), jp::ObjKind:Cont)
    test::AssertEq#(jp::ContGetKind(@file, file.root), jp::ContKind:Vec)
    test::AssertEq#(jp::ContGetSize(@file, file.root), 5_u32)

global test4 = """[
    {
        "string": "string",
        "bool": false,
        "num": 127664
    }
]"""

global test5 = """[
    {
        "string": "string",
        "bool": false,
        "num": 127664
    },
    {
        "string": "string",
        "bool": false,
        "num": 127664
    }
]"""

fun test_parser() void:
    test::AssertEq#(jp::NumJsonObjectsNeeded(test4), 12_u32)
    test::AssertEq#(jp::NumJsonObjectsNeeded(test5), 23_u32)
    test::AssertEq#(jp::NumJsonObjectsNeeded(test6), 99_u32)
    ;
    let! objects = {[200]jp::Object:}
    ref let! file jp::File
    ;
    set file = {jp::File: test4, objects}
    test::AssertIs#(jp::Parse(@!file), jp::Success)
    test::AssertEq#(file.used_objects, jp::NumJsonObjectsNeeded(test4))
    test::AssertEq#(jp::IndexGetKind(file.root), jp::ObjKind:Cont)
    test::AssertEq#(jp::ContGetKind(@file, file.root), jp::ContKind:Vec)
    test::AssertEq#(jp::ContGetSize(@file, file.root), 1_u32)
    ;
    set file = {jp::File: test5, objects}
    test::AssertIs#(jp::Parse(@!file), jp::Success)
    test::AssertEq#(file.used_objects, jp::NumJsonObjectsNeeded(test5))
    test::AssertEq#(jp::IndexGetKind(file.root), jp::ObjKind:Cont)
    test::AssertEq#(jp::ContGetKind(@file, file.root), jp::ContKind:Vec)
    test::AssertEq#(jp::ContGetSize(@file, file.root), 2_u32)

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
            "array": [ 100, 500, 300, 200, 400 ]

		},
	"array_of_dict": [
        {
            "string": "string",
            "bool": false,
            "num": 127664,
            "array": [ 100, 500, 300, 200, 400 ]
        },
        {
            "string": "string",
            "bool": false,
            "num": 127664,
            "array": [ 100, 500, 300, 200, 400 ]
        }]
}
"""

fun test_walk() void:
    let! objects = {[200]jp::Object:}
    ref let! file jp::File
    set file = {jp::File: test6, objects}
    test::AssertIs#(jp::Parse(@!file), jp::Success)
    test::AssertEq#(file.used_objects, jp::NumJsonObjectsNeeded(test6))
    test::AssertEq#(jp::IndexGetKind(file.root), jp::ObjKind:Cont)
    test::AssertEq#(jp::ContGetKind(@file, file.root), jp::ContKind:Dict)
    let array_item = jp::ContGetItemForKey(@file, file.root, "array_of_dict")
    test::AssertNe#(array_item, jp::NullIndex)
    let array = jp::ItemGetVal(@file, array_item)
    test::AssertEq#(jp::IndexGetKind(array), jp::ObjKind:Cont)
    let index1_item = jp::ContGetItemForIndex(@file, array, 1)
    let index1 = jp::ItemGetVal(@file, index1_item)
    let num_item = jp::ContGetItemForKey(@file, index1, "num")
    let num = jp::ItemGetVal(@file, num_item)
    test::AssertSliceEq#(jp::AtomGetData(@file, num), "127664")

fun main(argc s32, argv ^^u8) s32:
    do test_simple()
    do test_vec()
    do test_dict()
    do test_parser()
    do test_walk()
    test::Success#()
    return 0
