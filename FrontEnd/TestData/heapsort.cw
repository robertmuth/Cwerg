@doc "heapsort"
(module main [] :
(import random)

(import fmt)


(global SIZE uint 20)


(global! Data auto (array_val SIZE r64))


(global NEWLINE auto "\n")


(global ERROR auto "ERROR\n")


(fun cmp_lt [(param a (ptr r64)) (param b (ptr r64))] bool :
    (return (< (^ a) (^ b))))


(fun heap_sort [(param sdata (slice! r64))] void :
    (let data (ptr! r64) (front! sdata))
    (let n auto (len sdata))
    (let! ir auto n)
    (let! l auto (+ (>> n 1) 1))
    (let! rdata r64 undef)
    (while true :
        (if (> l 1) :
            (-= l 1)
            (= rdata (^ (pinc data l)))
         :
            (= rdata (^ (pinc data ir)))
            (= (^ (pinc data ir)) (^ (pinc data 1_uint)))
            (-= ir 1)
            (if (== ir 1) :
                (= (^ (pinc data ir)) rdata)
                (return)
             :))
        (let! i auto l)
        (let! j auto (<< l 1))
        (while (<= j ir) :
            (if (&& (< j ir) (cmp_lt [(pinc data j) (pinc data (+ j 1))])) :
                (+= j 1)
             :)
            (if (< rdata (^ (pinc data j))) :
                (= (^ (pinc data i)) (^ (pinc data j)))
                (= i j)
                (+= j i)
             :
                (= j (+ ir 1))))
        (= (^ (pinc data i)) rdata))
    (return))


(fun dump_array [(param size uint) (param data (ptr r64))] void :
    (@ref let! buf (array 32 u8) undef)
    (for i 0 size 1 :
        (let v auto (^ (pinc data i)))
        (fmt::print# (wrap v fmt::r64_hex) NEWLINE))
    (return))


@cdecl (fun main [(param argc s32) (param argv (ptr (ptr u8)))] s32 :
    (for i 0 SIZE 1 :
        (let v auto (random::get_random [1000]))
        (= (at Data (+ i 1)) v))
    (shed (dump_array [SIZE (& (at Data 1))]))
    (fmt::print# NEWLINE)
    (fmt::print# SIZE NEWLINE)
    (shed (heap_sort [Data]))
    (fmt::print# NEWLINE)
    (shed (dump_array [SIZE (& (at Data 1))]))
    (fmt::print# NEWLINE)
    (for i 1 SIZE 1 :
        (if (> (at Data i) (at Data (+ i 1))) :
            (fmt::print# ERROR)
            (trap)
         :))
    (return 0))
)

