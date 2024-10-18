module:

import fmt
import jp = json_parser
import test

global test_empty = ""

global test0 = """0"""

global test1 = """{"ip": "8.8.8.8"}"""

global test2 = """ {
   "string": "string",
   "bool": false,
   "num": 127664,
} """


global test3 = """[ 100, 500, 300, 200, 400 ]"""

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
    test::AssertEq#(jp::NumJsonObjectsNeeded(test0), 1_u32)
    test::AssertEq#(jp::NumJsonObjectsNeeded(test1), 3_u32)
    test::AssertEq#(jp::NumJsonObjectsNeeded(test2), 7_u32)
    test::AssertEq#(jp::NumJsonObjectsNeeded(test3), 11_u32)
    test::AssertEq#(jp::NumJsonObjectsNeeded(test4), 9_u32)
    test::AssertEq#(jp::NumJsonObjectsNeeded(test5), 17_u32)
    test::AssertEq#(jp::NumJsonObjectsNeeded(test6), 85_u32)

fun test_parser() void:
    let! objects = [100]jp::Object{void}
    @ref let! file = jp::File{test_empty, objects}
    test::AssertIs#(jp::FileParse(&!file), jp::DataError)

fun main(argc s32, argv ^^u8) s32:
    do test_counter()
    do test_parser()

    test::Success#()
    return 0