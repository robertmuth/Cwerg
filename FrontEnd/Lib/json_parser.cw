-- JSON Parser
-- Limit is 4GB of data
module:

import fmt

type Object = union(Dict, DictEntry, Vec, VecEntry, ValString, ValNum, void)

pub @wrapped type Success = void
pub global SuccessVal = wrap_as(void, Success)

pub @wrapped type AllocError = void
pub global AllocErrorVal = wrap_as(void, AllocError)

pub @wrapped type DataError = void
pub global DataErrorVal = wrap_as(void, DataError)

@wrapped type Index = u32
global Null = wrap_as(0xffffffff, Index)

-- numeric atom
rec ValNum:
    offset u32
    length u32

-- a string atom, the leading and trailing double quotes have been stripped
rec ValString:
    offset u32
    length u32
    has_esc bool

rec Dict:
    -- next sibling
    next Index
    -- first dict entry
    first Index

rec DictEntry:
    -- next dict entry
    next Index
    -- value of entry
    val Index
    key_offset u32
    key_length u32

rec Vec:
    -- next sibling
    next Index
    -- first vec entry
    first Index

rec VecEntry:
    -- next vec entry
    next Index
    val Index


pub rec File:
    -- the raw json data - must out-live the `file` rec
    -- because `objects` contain internal references to it
    data span(u8)
    -- objects[0] will contain the root of the tree after parsing
    objects span!(Object)
    used_objects u32

global z = """
fun FileAllocObject(file ^!File) union(AllocError, ^!Object):
    if file^.used_objects < as(len(file^.objects), u32):
        set file^.used_objects += 1
        return &!file^.objects[file^.used_objects - 1]
    return AllocErrorVal
"""

global ERROR = 0_u32


fun IsEndOfNum(c u8) bool:
    return c == ' ' || c == ']' || c == '}' || c == ',' || c == '\n' || c == ':'

global y = """
fun ReadNextObject(data span(u8), offset u32, obj ^!Object) u32:
    let c = data[offset]
    if c == '[':
        set obj^ = Vec{Null, Null}
        return offset + 1
    if c == '{':
        set obj^ = Dict{Null, Null}
        return offset + 1
    if c == '"':
        let start = offset + 1
        let! end = start
        let! seen_esc = false
        while end < as(len(data), u32):
            let d = data[end]
            if d == '"':
                set obj^ = ValString{start, end - start, seen_esc}
                return end + 1
            if d == '\\':
                set seen_esc = true
                set end += 2
                continue
            set end += 1
        -- error
        set obj^ = void
        return 0
    let start = offset
    let! end = start + 1
    while end < as(len(data), u32):
        if IsEndOfNum(data[offset]):
            break
        set end += 1
    set obj^ = ValNum{start, end - start}
    return end
"""

fun NextNonWS(data span(u8), offset u32) u32:
    let! i = offset
    while i < as(len(data), u32):
        let c = data[i]
        if c != ' ' && c != '\n':
            break
        set i += 1
    return i

global x = """
pub fun FileParse(file ^!File) union(Success, AllocError, DataError):
    let data = file^.data
    -- skip initial ws
    let! start = NextNonWS(data, 0)
    if start >= as(len(data), u32):
        -- empty json is an error for now
        return DataErrorVal
    trylet obj ^!Object = FileAllocObject(file), err :
        return err
    set start = ReadNextObject(file^.data, start, obj)
    cond:
        case is(obj^, Dict):
            return DataErrorVal
        case is(obj^, Vec):
            return DataErrorVal
        case is(obj^, DictEntry) or is(obj^, DictEntry):
            return DataErrorVal
        case is(obj^, ValString) || is(obj^, ValNum):
        case true:
            return DataErrorVal
    -- there should only be ws left
    set start = NextNonWS(data, start)
    if start != as(len(data), u32):
        -- garbage at end of file
        return DataErrorVal
    return SuccessVal
"""

enum State u8:
    invalid auto
    between_tokens auto
    in_string auto
    in_string_esc auto
    in_number auto

pub fun NumJsonObjectsNeeded(raw span(u8)) u32:
    let! state = State:between_tokens
    let! n = 0_u32
    for i = 0, len(raw), 1:
        let c = raw[i]
        -- fmt::print#(i, " ", wrap_as(c, fmt::rune), " ", n,"\n")
        cond:
            case state == State:in_string:
                if c == '"':
                    set state = State:between_tokens
                if c == '\\':
                    set state = State:in_string_esc
            case state == State:in_string_esc:
                set state = State:in_string
            case state == State:in_number:
                if c == ':':
                    set n -= 2
                    set state = State:between_tokens
                if c == ' ' || c == ']' || c == '}' || c == ',' || c == '\n':
                    set state = State:between_tokens
            -- from here on we can assume that state == State:between_tokens
            case IsEndOfNum(c):
                if c == ':':
                    set n -= 2
                continue
            case c == '[' ||  c == '{':
                set n += n == 0 ? 1 : 2
            case c == '"':
                set n += n == 0 ? 1 : 2
                set state = State:in_string
            case true:
                set n += n == 0 ? 1 : 2
                set state = State:in_number
    -- fmt::print#("RESULT ",  n, "\n")
    return n