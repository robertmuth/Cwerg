@doc "fizzbuzz"
(module [] :
(import fmt)


(global NEWLINE auto "\n")


(global FIZZ auto "FIZZ")


(global BUZZ auto "BUZZ")


(global FIZZBUZZ auto "FIBU")


(fun main [(param argc s32) (param argv (ptr (ptr u8)))] s32 :
    (for i 0 31_uint 1 :
        (cond :
            (case (== (% i 15) 0) :
                (fmt::print# FIZZBUZZ))
            (case (== (% i 3) 0) :
                (fmt::print# FIZZ))
            (case (== (% i 5) 0) :
                (fmt::print# BUZZ))
            (case true :
                (fmt::print# i)))
        (fmt::print# NEWLINE))
    (return 0))
)

