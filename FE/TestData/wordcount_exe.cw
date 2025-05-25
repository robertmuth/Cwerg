; Word Count Example
module:

import os

import fmt

fun is_white_space(c u8) bool:
    return c == ' ' || c == '\n' || c == '\t' || c == '\r'

; word, line and character count statistics
rec TextStats:
    num_lines uint
    num_words uint
    num_chars uint

; Returns either a TextStat or an Error
fun WordCount(fd os::FD) union(TextStats, os::Error):
    ; note limited type inference in next two stmts
    let! stats = {TextStats:}
    let! in_word = false
    ; do not initialize buf with zeros
    let! buf [1024]u8 = undef
    while true:
        ; if FileRead returns an uint, assign it to n else return it
        trylet n uint = os::FileRead(fd, buf), err:
            return err
        if n == 0:
            break
        set stats.num_chars += n
        ; index variable has the same type as n.
        for i = 0, n, 1:
            let c = buf[i]
            cond:
                case c == '\n':
                    set stats.num_lines += 1
                case is_white_space(c):
                    set in_word = false
                case !in_word:
                    set in_word = true
                    set stats.num_words += 1
        if n != len(buf):
            break
    return stats

fun main(argc s32, argv ^^u8) s32:
    trylet stats TextStats = WordCount(os::Stdin), err:
        return 1
    ; print# is a stmt macro for printing arbitrary values.
    ; (It is possible to define formatters for custom types.)
    fmt::print#(stats.num_lines, " ", stats.num_words, " ", stats.num_chars,
                "\n")
    return 0
