-- JSON Parser
-- Limit is 4GB of data and 1B objects where
-- * each atom uses up one objects
-- * each dict or vec use an additional object
-- * each dict and vec entry use an additional object
--
-- This is very barebones parser that does not do any
-- massaging of the data.
--
-- If you do not want to hardcode an upperbound use
-- NumJsonObjectsNeeded() to determine the number of
-- objects in a JSON string
-- The instantiate a File rec with the object pool like so:
-- let! objects = [200]jp::Object{}
-- @ref let! file = jp::File{"""{ "a": "str", "b": false, "c": 6}""", objects}
-- next parse the json inside the File:
-- let result = jp::Parse(&!file)
-- Finally walk the json starting with the root in file.root
-- Thw following helpers are avaiable:
-- * IndexGetKind()
-- * AtomGetKind()
-- * AtomGetData()
-- * ItemGetNext()
-- * ItemGetKey()
-- * ItemGetVal()
-- * ContGetKind()
-- * ContGetFirst()
-- * ContGetSize()

module:

import fmt

pub type Object = @untagged union(Cont, Item, Atom)

pub @wrapped type Success = void
pub global SuccessVal = wrap_as(void, Success)

pub @wrapped type AllocError = void
pub global AllocErrorVal = wrap_as(void, AllocError)

pub @wrapped type DataError = void
pub global DataErrorVal = wrap_as(void, DataError)


pub enum ObjKind u32:
    Invalid 0
    Cont 1
    Item 2
    Atom 3

@wrapped type Index = u32
global NullIndex = wrap_as(0, Index)

fun MakeIndex(index u32, kind ObjKind) Index:
    if index >= 1_u32 << 30:
        trap
    return wrap_as(unwrap(kind) << 30 or index, Index)

pub fun IndexGetKind(index Index) ObjKind:
    return wrap_as(unwrap(index) >> 30, ObjKind)

fun IndexGetValue(index Index) u32:
    return unwrap(index) and ((1_u32 << 30) - 1)

pub enum AtomKind u8:
    Invalid 0
    Num 1
    Str 2
    EscStr 3

-- an atom, for strings the leading and trailing double quotes have been stripped
rec Atom:
    offset u32
    length u32
    kind AtomKind

pub fun AtomGetKind(file ^File, index Index)  AtomKind:
    if IndexGetKind(index) != ObjKind:Atom:
        trap
    let ptr = bitwise_as(&file^.objects[IndexGetValue(index)], ^Atom)
    return ptr^.kind

pub fun AtomGetData(file ^File, index Index)  span(u8):
    if IndexGetKind(index) != ObjKind:Atom:
        trap
    let ptr = bitwise_as(&file^.objects[IndexGetValue(index)], ^Atom)
    return span(&file^.data[ptr^.offset] , as(ptr^.length, uint))

pub enum ContKind u8:
    Invalid 0
    Vec 1
    Dict 2

rec Cont:
    -- first cont entry
    first Index
    kind ContKind

-- Items make up the contents of Cont
rec Item:
    -- next entry inside Cont
    next Index
    -- key is not used for Vecs
    key Index
    val Index

pub fun ItemGetNext(file ^File, item Index) Index:
    if IndexGetKind(item) != ObjKind:Item:
        trap
    let ptr = bitwise_as(&file^.objects[IndexGetValue(item)], ^Item)
    return ptr^.next

pub fun ItemGeKey(file ^File, item Index) Index:
    if IndexGetKind(item) != ObjKind:Item:
        trap
    let ptr = bitwise_as(&file^.objects[IndexGetValue(item)], ^Item)
    return ptr^.key

pub fun ItemGetVal(file ^File, item Index) Index:
    if IndexGetKind(item) != ObjKind:Item:
        trap
    let ptr = bitwise_as(&file^.objects[IndexGetValue(item)], ^Item)
    return ptr^.val

pub fun ContGetKind(file ^File, index Index) ContKind:
    if IndexGetKind(index) != ObjKind:Cont:
        trap
    let ptr = bitwise_as(&file^.objects[IndexGetValue(index)], ^Cont)
    return ptr^.kind

pub fun ContGetFirst(file ^File, cont Index) Index:
    if IndexGetKind(cont) != ObjKind:Cont:
        trap
    let ptr = bitwise_as(&file^.objects[IndexGetValue(cont)], ^Cont)
    return ptr^.first

pub fun ContGetSize(file ^File, cont Index) u32:
    let! out = 0_u32
    let! index = ContGetFirst(file, cont)
    while index != NullIndex:
        set index = ItemGetNext(file, index)
        set out += 1
    return out

pub rec File:
    -- the raw json data - must out-live the `file` rec
    -- because `objects` contain internal references to it
    data span(u8)
    -- objects[0] will contain the root of the tree after parsing
    objects span!(Object)
    root Index
    --
    used_objects u32
    -- index into  `data`. Only used during parsing
    next_byte u32


fun IsEndOfNum(c u8) bool:
    return c == ' ' || c == ']' || c == '}' || c == ',' ||
           c == '\n' || c == ':' || c == '\t'


fun MaybeConsume(file ^!File, c u8) bool:
    let! i = file^.next_byte
    if i < as(len(file^.data), u32):
        if c == file^.data[i]:
            set file^.next_byte += 1
            return true
    return false

fun SkipWS(file ^!File) bool:
    let! i = file^.next_byte
    let end = as(len(file^.data), u32)
    while i < end:
        let c = file^.data[i]
        if c != ' ' && c != '\n' && c != '\t':
            break
        set i += 1
    set file^.next_byte = i
    return i < end

fun AllocObj(file ^!File) union(u32, AllocError):
    if file^.used_objects == as(len(file^.objects), u32):
        return AllocErrorVal
    let index = file^.used_objects
    set file^.used_objects += 1
    return index

fun ParseAtom(file ^!File) union(Index, AllocError, DataError):
    -- fmt::print#("ParseAtom ", file^.next_byte, "\n")
    trylet index u32 = AllocObj(file), err:
        return err

    let! start = file^.next_byte
    let length = as(len(file^.data), u32)
    if file^.data[start] == '"':
        -- parsing Str or EscStr
        set start += 1
        let! end = start
        let! seen_esc = false
        while end < length:
            let d = file^.data[end]
            if d == '"':
                set file^.objects[index] = Atom{start, end - start, seen_esc ? AtomKind:EscStr : AtomKind:Str}
                set file^.next_byte = end + 1
                -- fmt::print#("ParseAtom End: [", span(&file^.data[start], as(end - start, uint)), "]\n")
                return MakeIndex(index, ObjKind:Atom)
            if d == '\\':
                set seen_esc = true
                set end += 2
                continue
            set end += 1
        -- string was not terminated
        return DataErrorVal
    -- parsinglNum
    let! end = start + 1
    while end < length:
        if IsEndOfNum(file^.data[end]):
            break
        set end += 1
    set file^.objects[index] = Atom{start, end - start, AtomKind:Num}
    -- fmt::print#("ParseAtom End: [", span(&file^.data[start], as(end - start, uint)), "]\n")
    set file^.next_byte = end
    return MakeIndex(index, ObjKind:Atom)



fun ParseVec(file ^!File) union(Index, AllocError, DataError):
    -- fmt::print#("ParseVec ", file^.next_byte, "\n")
    let! first_entry = 0_u32
    let! last_entry = 0_u32
    let! last_val = NullIndex

    let! n = 0_u32
    while true:
        -- fmt::print#("ParseVec Loop ", file^.next_byte, " round=", n, "\n")
        if  !SkipWS(file):
            -- corrupted
            return DataErrorVal
        if MaybeConsume(file, ']'):
            -- fmt::print#("ParseVec End ", file^.next_byte, "\n")
            if n == 0:
                return NullIndex
            else:
                set file^.objects[last_entry] = Item{NullIndex, NullIndex, last_val}
                return MakeIndex(first_entry, ObjKind:Item)
        if n != 0:
            if !MaybeConsume(file, ',') || !SkipWS(file):
                -- fmt::print#("comma corruption\n")
                return DataErrorVal
        trylet entry u32 = AllocObj(file), err:
            return err
        trylet val Index = ParseNext(file), err:
            return err
        if n == 0:
            set first_entry = entry
        else:
            -- now that we know the next pointer, finalize the previous entry
            set file^.objects[last_entry] = Item{MakeIndex(entry, ObjKind:Item), NullIndex, last_val}
        set last_entry = entry
        set last_val = val
        set n += 1
    -- unreachable
    trap

fun ParseDict(file ^!File) union(Index, AllocError, DataError):
    -- fmt::print#("ParseDict ", file^.next_byte, "\n")
    let! first_entry = 0_u32
    let! last_entry = 0_u32
    let! last_val = NullIndex
    let! last_key = NullIndex

    let! n = 0_u32
    while true:
        -- fmt::print#("ParseDict Loop ", file^.next_byte, " round=", n, "\n")
        if !SkipWS(file):
            return DataErrorVal
        if MaybeConsume(file, '}'):
            -- fmt::print#("ParseDict End ", file^.next_byte, "\n")
            if n == 0:
                return NullIndex
            else:
                set file^.objects[last_entry] = Item{NullIndex, last_key, last_val}
                return MakeIndex(first_entry, ObjKind:Item)
        if n != 0:
            if !MaybeConsume(file, ',') || !SkipWS(file):
                -- fmt::print#("comma corruption\n")
                return DataErrorVal
        trylet entry u32 = AllocObj(file), err:
            return err
        trylet key Index = ParseNext(file), err:
            return err
        if  !SkipWS(file) || !MaybeConsume(file, ':') || !SkipWS(file):
            -- fmt::print#("colon corruption\n")
            return DataErrorVal
        trylet val Index = ParseNext(file), err:
            return err
        if n == 0:
            set first_entry = entry
        else:
            -- now that we know the next pointer, finalize the previous entry
            set file^.objects[last_entry] = Item{MakeIndex(entry, ObjKind:Item), last_key, last_val}
        set last_entry = entry
        set last_key = key
        set last_val = val
        set n += 1
    -- unreachable
    trap

-- assumes the next char is valid and not a WS
fun ParseNext(file ^!File) union(Index, AllocError, DataError):
    -- fmt::print#("ParseNext ", file^.next_byte, "\n")
    if MaybeConsume(file, '{'):
        trylet container u32 = AllocObj(file), err:
            return err
        trylet first Index = ParseDict(file), err:
            return err
        set file^.objects[container] = Cont{first, ContKind:Dict}
        return MakeIndex(container, ObjKind:Cont)
    if MaybeConsume(file, '['):
        trylet container u32 = AllocObj(file), err:
            return err
        trylet first Index = ParseVec(file), err:
            return err
        set file^.objects[container] = Cont{first, ContKind:Vec}
        return MakeIndex(container, ObjKind:Cont)
    return ParseAtom(file)


pub fun Parse(file ^!File) union(Success, AllocError, DataError):
    -- fmt::print#("Parse ",  file^.next_byte,"\n")
    if !SkipWS(file):
        -- empty json is an error for now
        return DataErrorVal
    tryset file^.root = ParseNext(file), err:
        return err
    -- fmt::print#("Parse End ",  file^.next_byte, "\n")
    if SkipWS(file):
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