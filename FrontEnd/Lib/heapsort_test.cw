@doc "heapsort"
(module [] :
(import random)

(import fmt)


(type real64 r64)


(fun cmp_r64_lt [(param a (ptr real64)) (param b (ptr real64))] bool :
    (return (< (^ a) (^ b))))

(import rhs heapsort_gen [real64 cmp_r64_lt])


(global SIZE uint 20)


(global! Data auto (array_val SIZE r64))


(global NEWLINE auto "\n")


(global ERROR auto "ERROR\n")


(fun dump_array [(param size uint) (param data (ptr r64))] void :
    (@ref let! buf (array 32 u8) undef)
    (for i 0 size 1 :
        (let v auto (^ (pinc data i)))
        (fmt::print# (wrap_as v fmt::r64_hex) NEWLINE))
    (return))


@cdecl (fun main [(param argc s32) (param argv (ptr (ptr u8)))] s32 :
    (for i 0 SIZE 1 :
        (let v auto (random::get_random [1000]))
        (= (at Data (+ i 1)) v))
    (do (dump_array [SIZE (& (at Data 1))]))
    (fmt::print# NEWLINE)
    (fmt::print# SIZE NEWLINE)
    (do (rhs::sort [Data]))
    (fmt::print# NEWLINE)
    (do (dump_array [SIZE (& (at Data 1))]))
    (fmt::print# NEWLINE)
    (for i 1 SIZE 1 :
        (if (> (at Data i) (at Data (+ i 1))) :
            (fmt::print# ERROR)
            (trap)
         :))
    (return 0))
)
