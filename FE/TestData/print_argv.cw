-- print command-line args
module:

import fmt

fun strlen(s ^u8) uint:
    let! i uint = 0
    -- ptr_inc is adds an integer to a pointer it also has an options bound
    while ptr_inc(s, i)^ != 0:
        set i += 1
    return i

fun main(argc s32, argv ^^u8) s32:
    for i = 0, as(argc, u32), 1:
        let s ^u8 = ptr_inc(argv, i)^
        -- the print# macro does not supprt zero terminated strings
        -- but it does support slices.
        let t = make_span(s, strlen(s))
        fmt::print#(t, "\n")
    return 0
