
module:

import fmt
import test


rec Item:
    key uint
    val uint
    
rec File:
    data uint
    objects span!(Item)


fun setter(file ^!File, index uint, key uint, val uint) void:
    ; set file^.objects[index].key = key
    set file^.objects[index].val = val
    
fun checker(file ^!File, index uint, key uint, val uint) void:
     ; test::AssertEq#(key, file^.objects[index].key)
     test::AssertEq#(val, file^.objects[index].val)

fun test_simple() void:
    let! objects = {[200]Item:}
    ref let! file = {File: 666, objects}
    do  setter(@!file, 1, 1, 2)
    do  setter(@!file, 66, 3, 4)
    do  setter(@!file, 111, 5, 6)
    ;
    do  checker(@!file, 1, 1, 2)
    do  checker(@!file, 66, 3, 4)
    do  checker(@!file, 111, 5, 6)

fun main(argc s32, argv ^^u8) s32:
    do test_simple()
    test::Success#()
    return 0
