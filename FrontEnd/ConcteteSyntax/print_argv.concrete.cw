-- print command-line args
module main:

import fmt

fun strlen(s ptr(u8)) uint:
    let! i uint = 0
    -- pinc is adds an integer to a pointer it also has an options bound
    while *pinc(s, i) != 0:
        set i += 1
    return i

@cdecl fun main(argc s32, argv ptr(ptr(u8))) s32:
    for i = 0, as(argc, u32), 1:
        let s ptr(u8) = *pinc(argv, i)
        -- the print# macro does not supprt zero terminated strings
        -- but it does support slices.
        let t = slice(s, strlen(s))
        fmt::print#(t, "\n")
    return 0

