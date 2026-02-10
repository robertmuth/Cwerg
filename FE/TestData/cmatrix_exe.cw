module:

import ansi

import os

import fmt


fun main(argc s32, argv ^^u8) s32:
    ref let! win_size os::WinSize = undef
    trylet res uint = os::Ioctl(os::Stdout, os::IoctlOp:TIOCGWINSZ, bitwise_as(@!win_size, ^!void)), err:
        fmt::print#("cannot determine terminal resolution\n")
        return 1
    fmt::print#("Res ", win_size.ws_row, "x", win_size.ws_col, "\n")
    fmt::print#(ansi::CURSOR_HIDE)
    fmt::print#(ansi::CURSOR_SHOW)

    return 0