-- module
module m1:

@pub rec type_rec2:
    s1 slice(u8)
    -- field comment
    s2 s32
    s3 s32

-- global with rec literal
global r02 = type_rec2{s2 : 9, 
    -- field_val comment
    7}

-- enum decl
enum type_enum s32:
    -- enum entry comment
    e1 7
    e2 auto
    e3 19
    e4 auto

global c31 = [30]uint{10, 
    -- index_val
    20, 30}

-- fun
fun main(argc s32, 
    -- param
    argv ^^u8) s32:
    let! loc11 = [30]uint{10, 
        -- index_val
        20, 30}
    let! loc22 = type_rec2{s2 : 9, 
        -- field_val comment
        7}
    -- cond
    cond:
        -- in block
        case argc % 15 == 0:
            -- in block
            return 1
        -- in another block2
        case argc % 3 == 0:
            return 2
        case argc % 5 == 0:
            return 3
        case true:
            return 4
    return 0
