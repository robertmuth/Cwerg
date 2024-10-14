module:

type Object = union(Dict, DictEntry, Vec, VecEntry, ValString, ValNum, void)


@wrapped type Index = u32


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


rec File:
    data span(u8)
    objects span!(Object)

enum State u8:
    invalid auto
    between_tokens auto
    in_string auto
    in_string_esc auto
    in_number auto



fun NumJsonObjectsNeeded(raw span(u8)) u32:
    let! state = State:between_tokens
    let! n = 0_u32
    for i = 0, len(raw), 1:
        let c = raw[i]
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
            -- here we can assume that state == State:between_tokens
            case c == ':':
                 set n -= 2
            case c == ' '|| c == ']' || c == '}' || c == ',' || c == '\n':
                continue
            case c == '[' ||  c == '{':
                set n += 1
            case c == '"':
                set n += 2
                set state = State:in_string
            case true:
                set n += 2
                set state = State:in_number
    return n