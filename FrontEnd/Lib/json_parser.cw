-- JSON Parser
-- Limit is 4GB of data and 527M objects where
-- * each atom uses up one objects
-- * each dict or vec use an additional object
-- * each dict and vec entry use an  addition object
module:

import fmt

pub type Object = union(Dict, DictEntry, Vec, VecEntry, Val, void)

pub @wrapped type Success = void
pub global SuccessVal = wrap_as(void, Success)

pub @wrapped type AllocError = void
pub global AllocErrorVal = wrap_as(void, AllocError)

pub @wrapped type DataError = void
pub global DataErrorVal = wrap_as(void, DataError)

@wrapped type Index = u32
global Null = wrap_as(0xffffffff, Index)


pub enum ObjKind u8:
    Invalid 0
    Vec 1
    Dict 2
    Other 3


pub enum ValKind u8:
    Invalid 0
    Num 1
    Str 2
    EscStr 3

-- an atom, for strings the leading and trailing double quotes have been stripped
pub rec Val:
    offset u32
    length u32
    kind ValKind

pub rec Dict:
    -- next sibling
    next Index
    -- first dict entry
    first Index

pub rec DictEntry:
    -- next dict entry
    next Index
    key Index
    val Index

pub rec Vec:
    -- next sibling
    next Index
    -- first vec entry
    first Index
    length u32

pub rec VecEntry:
    -- next vec entry
    next Index
    val Index
    index u32

pub rec File:
    -- the raw json data - must out-live the `file` rec
    -- because `objects` contain internal references to it
    data span(u8)
    -- objects[0] will contain the root of the tree after parsing
    objects span!(Object)
    used_objects u32


fun FileAllocObject(file ^!File) union(AllocError, ^!Object):
    fmt::print#("alloc obj\n")
    if file^.used_objects < as(len(file^.objects), u32):
        set file^.used_objects += 1
        return &!file^.objects[file^.used_objects - 1]
    return AllocErrorVal

global ERROR = 0_u32


fun IsEndOfNum(c u8) bool:
    return c == ' ' || c == ']' || c == '}' || c == ',' || c == '\n' || c == ':'

fun ReadNextObject(data span(u8), offset u32, obj ^!Object) u32:
    let c = data[offset]
    if c == '[':
        set obj^ = Vec{Null, Null, 0}
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
                set obj^ = Val{start, end - start, seen_esc ? ValKind:EscStr : ValKind:Str}
                return end + 1
            if d == '\\':
                set seen_esc = true
                set end += 2
                continue
            set end += 1
        -- error
        set obj^ = void
        return 0
    -- parsinglNum
    let start = offset
    let! i = start + 1
    while i < as(len(data), u32):
        if IsEndOfNum(data[i]):
            break
        set i += 1
    set obj^ = Val{start, i - start, ValKind:Num}
    return i

fun NextNonWS(data span(u8), start u32) u32:
    let! i = start
    while i < as(len(data), u32):
        let c = data[i]
        if c != ' ' && c != '\n':
            break
        set i += 1
    return i

fun ParseVec(file ^!File, container ^!Vec, start u32) union(u32, AllocError, DataError):
    fmt::print#("ParseVec ",  start, "\n")
    let! i = start
    let! n = 0_u32
    while true:
        set i = NextNonWS(file^.data, i)
        fmt::print#("ParseVec Loop ", n, " ", i, "\n")
        if i >= as(len(file^.data), u32):
            return DataErrorVal
        let c = file^.data[i]
        if c == ']':
            fmt::print#("ParseVec End ",  i, "\n")
            set i += 1
            set container^.length = n
            return i
        if n != 0:
            if c != ',':
                return DataErrorVal
            set i = NextNonWS(file^.data, i + 1)
        trylet entry ^!Object = FileAllocObject(file), err :
            return err
        set entry^ = VecEntry{Null, Null ,n}
        trylet val ^!Object = FileAllocObject(file), err :
            return err
        tryset i = ParseNextRecursively(file, i, val), err:
            return err
        set n += 1
    return 0_u32

fun ParseNextRecursively(file ^!File, start u32, obj ^!Object) union(u32, AllocError, DataError):
    fmt::print#("ParseNextRecursively ",  start, "\n")
    let! i = ReadNextObject(file^.data, start, obj)
    cond:
        case is(obj^, Dict):
            return DataErrorVal
        case is(obj^, Vec):
            return ParseVec(file, bitwise_as(obj, ^!Vec), i)
        case is(obj^, Val):
            fmt::print#("string or num seen\n")
            return i
    return DataErrorVal

pub fun Parse(file ^!File) union(Success, AllocError, DataError):
    fmt::print#("FileParse\n")
    -- skip initial ws
    let! i = 0_u32
    set i = NextNonWS(file^.data, i)
    if i >= as(len(file^.data), u32):
        -- empty json is an error for now
        return DataErrorVal
    trylet obj ^!Object = FileAllocObject(file), err :
        return err
    tryset i = ParseNextRecursively(file, i, obj), err:
        return err
    fmt::print#("FileParse End ", i, "\n")
    -- there should only be ws left
    set i = NextNonWS(file^.data, i)
    if i != as(len(file^.data), u32):
        -- garbage at end of file
        return DataErrorVal
    return SuccessVal


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
                    -- probably impossible as numbers are not allowed as keys
                    set n -= 1
                    set state = State:between_tokens
                if c == ' ' || c == ']' || c == '}' || c == ',' || c == '\n':
                    set state = State:between_tokens
            -- from here on we can assume that state == State:between_tokens
            case IsEndOfNum(c):
                if c == ':':
                    set n -= 1
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