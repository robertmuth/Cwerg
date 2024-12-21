-- hashtab32
--
-- 32 refers to the width of the integer returned by the hash function.
-- This also limits the max table size to (2^32 - 1).
--
-- The approach used is linear probing with separate arrays afor keys and values
-- (and meta data) to improve reference locality.
--
module(
        -- the key type
        $ktype TYPE,
        -- the value type
        $vtype TYPE,
        -- the hash function: ptr($ktype) -> u32
        $khash CONST_EXPR,
        -- the key equality checker: ptr($ktype) X ptr($ktype) -> bool
        $keq CONST_EXPR):

import fmt

global FreeEntry u8 = 0x00

global DeletedEntry u8 = 0x01

global UsedEntryMark u8 = 0x80

--
-- The Hashtable contains pointers to 3 arrays of size `size`:
-- * meta: u8 entries with the following meaning:
--   - FreeEntry (0):              entry is unused
--   - DeletedEntry (1):           tombstone for deleted FreeEntry
--   - Highbit (UsedEntryMark) set: entry is used and low 7 bits match key hash
-- * keys: the keys
-- * vals: the value
--
--
pub rec HashTab32:
    meta ^!u8
    keys ^!$ktype
    vals ^!$vtype
    size u32
    used u32

pub fun Lookup(ht ^HashTab32, key ^$ktype) union(void, ^!$vtype):
    let h u32 = $khash(key)
    let filter u8 = as(h, u8) | UsedEntryMark
    let meta = ht^.meta
    let keys = ht^.keys
    let vals = ht^.vals
    let size = ht^.size
    let! i = h % size
    while true:
        let m = ptr_inc(meta, i)^
        if m == FreeEntry:
            fmt::print#("Not Found\n")
            return
        if m == filter && $keq(key, ptr_inc(keys, i)):
            return ptr_inc(vals, i)
        set i += 1
        if i >= size:
            set i -= size

pub fun InsertOrUpdate(ht ^!HashTab32, key ^$ktype, val ^$vtype) bool:
    let h u32 = $khash(key)
    let filter u8 = as(h, u8) | UsedEntryMark
    let meta = ht^.meta
    let keys = ht^.keys
    let size = ht^.size
    let! i = h % size
    let! seen_deleted = false
    let! first_deleted u32 = 0
    while true:
        let m = ptr_inc(meta, i)^
        if m == FreeEntry:
            if !seen_deleted:
                set first_deleted = i
            set ptr_inc(meta, first_deleted)^ = filter
            set ptr_inc(keys, first_deleted)^ = key^
            set ptr_inc(ht^.vals, first_deleted)^ = val^
            set ht^.used += 1
            return true
        if m == filter && $keq(key, ptr_inc(keys, i)):
            set ptr_inc(ht^.vals, i)^ = val^
            return false
        if !seen_deleted && m == DeletedEntry:
            set seen_deleted = true
            set first_deleted = i
        set i += 1
        if i >= size:
            set i -= size

pub fun DeleteIfPresent(ht ^!HashTab32, key ^$ktype) bool:
    let h u32 = $khash(key)
    let filter u8 = as(h, u8) | UsedEntryMark
    let meta = ht^.meta
    let keys = ht^.keys
    let size = ht^.size
    let! i = h % size
    while true:
        let m = ptr_inc(meta, i)^
        if m == FreeEntry:
            return false
        if m == filter && $keq(key, ptr_inc(keys, i)):
            set ptr_inc(meta, i)^ = DeletedEntry
            set ht^.used -= 1
            return true
        set i += 1
        if i >= size:
            set i -= size

pub fun DebugDump(ht ^HashTab32) void:
    let meta = ht^.meta
    let keys = ht^.keys
    let vals = ht^.vals
    for i = 0, ht^.size, 1:
        fmt::print#(i, " ")
        let m = ptr_inc(meta, i)^
        cond:
            case m == DeletedEntry:
                fmt::print#("DELETED")
            case m == FreeEntry:
                fmt::print#("FREE")
            case true:
                fmt::print#(m, " ", ptr_inc(keys, i)^, " ", ptr_inc(vals, i)^)
        fmt::print#("\n")
