-- Macro Examples
module:

pub rec MyRec:
    s1 s32
    s2 u32

fun TestRightArrowMacro(pointer ^MyRec) u32:
    return pointer^.s2

fun TestWhileMacro(end u32) u32:
    let! sum u32 = 0
    while sum < end:
        set sum += 1
    return sum

fun TestForMacro(end u32) u32:
    let! sum u32 = 0
    for i = 0, end, 1:
        set sum += i
    return sum

macro nested0# STMT_LIST()[]:

macro nested1# STMT_LIST()[]:
    nested0#()

macro nested2# STMT_LIST()[]:
    nested1#()

macro nested3# STMT_LIST()[]:
    nested2#()

macro nested4# STMT_LIST()[]:
    nested3#()

fun TestRecursiveMacro() u32:
    nested3#()
    return 0

macro product# STMT_LIST($result ID, $factors STMT_LIST)[]:
    mfor $x $factors:
        set $result = $result * $x

fun TestProductMacro() u32:
    let! result u32 = 1
    product#(result,{111, 2 * 111, 333, 444, 555, 666})
    return result

fun TestForMacroStringify() span(u8):
    return stringify(TestForMacroStringify)

fun TestSwap(array span!(u8)) void:
    swap#(array[1], array[2])

-- just a compilation test
fun main(argc s32, argv ^^u8) s32:
    return 0
