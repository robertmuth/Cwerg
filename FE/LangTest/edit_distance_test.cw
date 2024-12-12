-- edit (levenshtein) distance benchmark
module:

import test

import fmt

global MAX_LEN = 1000_uint

global TEST_STRING = "abcdef"

-- pre-condition: len(tmp) >= len(a)
-- tmp hold the current row of a len(a) x len(b) dynamic programming matrix mat
-- which is filled top to botton, and left to right
-- the last value  (bottom right) is the edit distance
-- the value of mat[aindex][bindex] contains the edit_distance of substrings
--    a[0:aindex+1] and b[0:bindex+1]
-- we also define (consistent with the above definition):
--     mat[-1][-1] == 0
--     mat[-1][bindex] = bindex + 1
--     mat[aindex][-1] = aindex + 1
--
--  The value of mat[x][y] can be computed from
--    ddist  mat[x-1][y-1]
--    tdist  mat[x][y-1]
--    ldist  mat[x-1][y]
-- as follows:
-- if a[x] == b[x]: mat[x][y] = ddist
-- else:            mat[x][y] = 1 + min(ddist, tdist, ldist)
fun edit_distance(a span(u8), b span(u8), tmp span!(uint)) uint:
    let alen = len(a)
    let blen = len(b)
    if alen == 0:
        return blen
    if blen == 0:
        return alen
    if front(a) == front(b) && alen == blen:
        return 0
    if len(tmp) < alen:
        trap
    for i = 0, alen, 1:
        set tmp[i] = i + 1
    -- contains the value of tmp[aindex - 1] from the current round
    let! ldist = 0_uint
    for bindex = 0, blen, 1:
        let bchar = b[bindex]
        -- ldist = mat[-1][bindex]
        set ldist = bindex + 1
        -- ddist = mat[-1][bindex- 1]
        let! ddist = bindex
        for aindex = 0, alen, 1:
            let tdist = tmp[aindex]
            -- fmt::print#(bindex, ":", aindex, " - ", ddist, " ", tdist, " ", ldist)
            if bchar == a[aindex]:
                -- use the edit distance for both substrings being 1 char shorter
                set ldist = ddist
            else:
                set ldist = 1 + min(ldist, min(tdist, ddist))
            -- fmt::print#(" -> ", ldist, "\n")
            set tmp[aindex] = ldist
            set ddist = tdist
    return ldist

fun main(argc s32, argv ^^u8) s32:
    ref let! v = {[MAX_LEN]uint:}
    test::AssertEq#(edit_distance("", "", v), 0_uint)
    test::AssertEq#(edit_distance(TEST_STRING, TEST_STRING, v), 0_uint)
    test::AssertEq#(edit_distance("", "abc", v), 3_uint)
    test::AssertEq#(edit_distance("abc", "", v), 3_uint)
    test::AssertEq#(edit_distance("ab", "a", v), 1_uint)
    test::AssertEq#(edit_distance("abc", "ab", v), 1_uint)
    test::AssertEq#(edit_distance("ab", "abc", v), 1_uint)
    test::AssertEq#(edit_distance("a", "b", v), 1_uint)
    test::AssertEq#(edit_distance("abcde", "abxde", v), 1_uint)
    test::AssertEq#(edit_distance("abcde", "xabcd", v), 2_uint)
    test::Success#()
    return 0
