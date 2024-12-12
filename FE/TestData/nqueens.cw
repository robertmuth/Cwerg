-- nqueens
module:

import fmt

import test

global DIM = 10_s32

type Board = [DIM][DIM]bool

fun DumpBoard(board ^Board) void:
    for i = 0, DIM, 1:
        for j = 0, DIM, 1:
            fmt::print#(board^[i][j] ? "Q" : ".")
        fmt::print#("\n")
    fmt::print#("\n")

fun HasConflict(board ^Board, row s32, col s32) bool:
    for i = 0, row, 1:
        if board^[i][col]:
            return true
        let j = row - i
        if col - j + 1 > 0 && board^[i][col - j]:
            return true
        if col + j < DIM && board^[i][col + j]:
            return true
    return false

fun Solve(board ^!Board, row s32) uint:
    if row >= DIM:
        -- (do (DumpBoard [board]))
        return 1
    let! n = 0_uint
    for i = 0, DIM, 1:
        if !HasConflict(board, row, i):
            set board^[row][i] = true
            set n += Solve(board, row + 1)
            set board^[row][i] = false
    return n

fun main(argc s32, argv ^^u8) s32:
    -- initialized to false
    ref let! board = {[DIM][DIM]bool:}
    let n = Solve(&!board, 0)
    fmt::print#(n, "\n")
    test::AssertEq#(n, 724_uint)
    test::Success#()
    return 0
