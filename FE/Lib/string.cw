-- String Library
module:

pub global NOT_FOUND uint = !0

fun are_two_non_empty_strings_the_same(s1 ^u8, s2 ^u8, n uint) bool:
    let! i uint = 0
    block _:
        let c1 u8 = ptr_inc(s1, i)^
        let c2 u8 = ptr_inc(s2, i)^
        if c1 != c2:
            return false
        set i += 1
        if i < n:
            continue
        else:
            return true

pub fun find(haystack span(u8), needle span(u8)) uint:
    let nlen uint = len(needle)
    let hlen uint = len(haystack)
    if nlen == 0:
        return 0
    if hlen < nlen:
        return NOT_FOUND
    -- at this point we know that both slices have len > 0
    let hptr ^u8 = front(haystack)
    let nptr ^u8 = front(needle)
    let n uint = hlen - nlen
    let! i uint = 0
    block _:
        if are_two_non_empty_strings_the_same(ptr_inc(hptr, i), nptr, nlen):
            return i
        set i += 1
        if i <= n:
            continue
        else:
            return NOT_FOUND

pub fun rfind(haystack span(u8), needle span(u8)) uint:
    let nlen uint = len(needle)
    let hlen uint = len(haystack)
    if nlen == 0:
        return 0
    if hlen < nlen:
        return NOT_FOUND
    -- at this point we know that both slices have len > 0
    let hptr ^u8 = front(haystack)
    let nptr ^u8 = front(needle)
    let! i uint = hlen - nlen
    block _:
        if are_two_non_empty_strings_the_same(ptr_inc(hptr, i), nptr, nlen):
            return i
        if i == 0:
            return NOT_FOUND
        set i -= 1
        continue

pub fun starts_with(haystack span(u8), needle span(u8)) bool:
    let hlen uint = len(haystack)
    let nlen uint = len(needle)
    if nlen == 0:
        return true
    if hlen < nlen:
        return false
    -- at this point we know that both slices have len > 0
    return are_two_non_empty_strings_the_same(
            front(haystack), front(needle), nlen)

pub fun ends_with(haystack span(u8), needle span(u8)) bool:
    let hlen uint = len(haystack)
    let nlen uint = len(needle)
    if nlen == 0:
        return true
    if hlen < nlen:
        return false
    -- at this point we know that both slices have len > 0
    return are_two_non_empty_strings_the_same(
            ptr_inc(front(haystack), hlen - nlen), front(needle), nlen)

pub fun cmp(aslice span(u8), bslice span(u8)) sint:
    let alen uint = len(aslice)
    let blen uint = len(bslice)
    let n uint = min(alen, blen)
    let aptr ^u8 = front(aslice)
    let bptr ^u8 = front(bslice)
    let! i uint = 0
    block _:
        if i < n:
        else:
            break
        let a u8 = ptr_inc(aptr, i)^
        let b u8 = ptr_inc(bptr, i)^
        cond:
            case a == b:
            case a < b:
                return -1
            case true:
                return 1
        set i += 1
        continue
    -- the common prefix is the same
    cond:
        case alen == blen:
            return 0
        case alen < blen:
            return -1
        case true:
            return 1

fun contains_char(haystack span(u8), needle u8) bool:
    -- assumes that haystack is not empty
    let n uint = len(haystack)
    let hptr ^u8 = front(haystack)
    let! i uint = 0
    block _:
        if needle == ptr_inc(hptr, i)^:
            return true
        set i += 1
        if i < n:
            continue
        else:
            return false

pub fun find_first_of(haystack span(u8), needle span(u8)) uint:
    let nlen uint = len(needle)
    let hlen uint = len(haystack)
    if hlen == 0:
        return NOT_FOUND
    if nlen == 0:
        return NOT_FOUND
    -- at this point we know that both slices have len > 0
    let hptr ^u8 = front(haystack)
    let! i uint = 0
    block _:
        if contains_char(needle, ptr_inc(hptr, i)^):
            return i
        set i += 1
        if i < hlen:
            continue
        else:
            return NOT_FOUND

pub fun find_first_not_of(haystack span(u8), needle span(u8)) uint:
    let nlen uint = len(needle)
    let hlen uint = len(haystack)
    if hlen == 0:
        return NOT_FOUND
    if nlen == 0:
        return 0
    -- at this point we know that both slices have len > 0
    let hptr ^u8 = front(haystack)
    let! i uint = 0
    block _:
        if contains_char(needle, ptr_inc(hptr, i)^):
        else:
            return i
        set i += 1
        if i < hlen:
            continue
        else:
            return NOT_FOUND

pub fun find_last_of(haystack span(u8), needle span(u8)) uint:
    let nlen uint = len(needle)
    let hlen uint = len(haystack)
    if hlen == 0:
        return NOT_FOUND
    if nlen == 0:
        return NOT_FOUND
    -- at this point we know that both slices have len > 0
    let hptr ^u8 = front(haystack)
    let! i uint = hlen
    block _:
        set i -= 1
        if contains_char(needle, ptr_inc(hptr, i)^):
            return i
        if i == 0:
            return NOT_FOUND
        continue

pub fun find_last_not_of(haystack span(u8), needle span(u8)) uint:
    let nlen uint = len(needle)
    let hlen uint = len(haystack)
    if hlen == 0:
        return NOT_FOUND
    if nlen == 0:
        return hlen - 1
    -- at this point we know that both slices have len > 0
    let hptr ^u8 = front(haystack)
    let! i uint = hlen
    block _:
        set i -= 1
        if contains_char(needle, ptr_inc(hptr, i)^):
        else:
            return i
        if i == 0:
            return NOT_FOUND
        continue
