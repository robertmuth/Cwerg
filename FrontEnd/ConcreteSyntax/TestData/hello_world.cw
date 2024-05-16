-- main module with program entry point `main`
module main:

import fmt

@cdecl fun main(argc s32, argv ^^u8) s32:
    fmt::print#("""hello world

    line 1
    line 2
""")
    return 0
