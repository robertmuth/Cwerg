module:

import test
import os
import fmt

global gThreads uint = 10
global gIterations uint = 10000
global gStackSize uint = 8 * 1024

global gCounters [gThreads]uint
ref global! gStacks [gThreads + 1][gStackSize]u8

fun thread_runner(no uint) void:
    fmt\print#("hi from ", no, "\n")
    return

fun run() uint:
    fmt\print#("running with ", gThreads, " threads\n")
    ref let req = {os\TimeSpec: 0, 100000000}
    ref let! rem os\TimeSpec = undef
    ref let! params os\CloneArgs
    set params.flags = os\CLONE_VM | os\CLONE_FS | os\CLONE_FILES | os\CLONE_SIGHAND |
                       os\CLONE_THREAD | os\CLONE_SYSVSEM
    for i = 0, gThreads, 1:
        fmt\print#("spawning ", i, "\n")
        ; do os\nanosleep(@req, @!rem)
        set params.stack = front!(gStacks[i + 1])
        set params.stack_size = gStackSize
        fmt\print#("stack ", wrap_as(bitwise_as(params.stack, uint), fmt\uint_hex), "\n")
        trylet pid u32 = os\Clone3Wrapper(thread_runner, i, @!params), err:
            fmt\print#("clone failed at ", i, " with ", unwrap(err), "\n")
            continue

    do os\nanosleep(@req, @!rem)
    return  gIterations * gThreads


fun main(argc s32, argv ^^u8) s32:
    test\AssertEq#(run(), gIterations * gThreads)
    test\Success#()
    return 0