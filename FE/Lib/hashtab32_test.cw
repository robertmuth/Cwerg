-- hash_test
module:

import fmt

import test

fun hash_32(xx ^u32) u32:
    let x u32 = xx^
    return x << 16_u32 ~ x * 123456789

fun eq_32(a ^u32, b ^u32) bool:
    return a^ == b^

import hashtab = hashtab32_gen(u32, u32, hash_32, eq_32)

global SIZE u32 = 32

global! meta = {[SIZE]u8: 0}

global! keys = {[SIZE]u32: 0}

global! vals = {[SIZE]u32: 0}

global! ht = {hashtab::HashTab32: front!(meta), front!(keys), front!(vals), SIZE, 
    0}

fun main(argc s32, argv ^^u8) s32:
    ref let! key u32 = 6
    ref let! val u32 = 6
    for i = 0, SIZE / 2, 1:
        set key = i
        set val = !i
        let p = hashtab::InsertOrUpdate(@!ht, @key, @val)
        fmt::print#("Insert key: ", key, " val: ", val, " ->  ", p, "\n")
    do hashtab::DebugDump(@ht)
    for i = 0, SIZE / 2, 1:
        set key = i
        let v_expected = !i
        trylet pval ^!u32 = hashtab::Lookup(@!ht, @key), err:
        test::AssertEq#(pval^, v_expected)
    -- if we delete one element and re-insert, it should
    --     end up in the same spit
    --     
    set key = 6
    trylet lookup1 ^!u32 = hashtab::Lookup(@!ht, @key), err:
    test::AssertTrue#(hashtab::DeleteIfPresent(@!ht, @key))
    test::AssertTrue#(hashtab::InsertOrUpdate(@!ht, @key, @val))
    trylet lookup2 ^!u32 = hashtab::Lookup(@!ht, @key), err:
    test::AssertEq#(lookup1, lookup2)
    set key = 6
    set val = 66
    test::AssertFalse#(hashtab::InsertOrUpdate(@!ht, @key, @val))
    trylet pval ^!u32 = hashtab::Lookup(@!ht, @key), err:
    test::AssertEq#(pval^, val)
    test::Success#()
    return 0
