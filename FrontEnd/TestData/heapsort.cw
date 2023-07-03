(module main [] :
(# "heapsort")
(import random )

(global SIZE uint 20)


(global mut Data auto (array_val (+ SIZE 1) r64 []))


(global NEWLINE auto "\n")


(global ERROR auto "ERROR\n")


(fun heap_sort [(param n uint) (param data (ptr mut r64))] void :
    (let mut ref buf (array 32 u8) undef)
    (let mut ir auto n)
    (let mut l auto (+ (>> n 1) 1))
    (let mut rdata r64 undef)
    (while true :
        (if (> l 1) :
            (-= l 1)
            (= rdata (^ (incp data l undef)))
            :
            (= rdata (^ (incp data ir undef)))
            (= (^ (incp data ir undef)) (^ (incp data 1_uint undef)))
            (-= ir 1)
            (if (== ir 1) :
                (= (^ (incp data ir undef)) rdata)
                (return void_val)
                :))
        (let mut i auto l)
        (let mut j auto (<< l 1))
        (while (<= j ir) :
            (if (&& (< j ir) (< (^ (incp data j undef)) (^ (incp data (+ j 1) undef)))) :
                (+= j 1)
                :)
            (if (< rdata (^ (incp data j undef))) :
                (= (^ (incp data i undef)) (^ (incp data j undef)))
                (= i j)
                (+= j i)
                :
                (= j (+ ir 1))))
        (= (^ (incp data i undef)) rdata))
    (return void_val))


(fun dump_array [(param size uint) (param data (ptr r64))] void :
    (let mut ref buf (array 32 u8) undef)
    (for i u64 0 size 1 [(let v auto (^ (incp data i undef))) (print [(as v r64_hex) NEWLINE])])
    (return void_val))


(fun main [(param argc s32) (param argv (ptr (ptr u8)))] s32 :
    (for i u64 0 SIZE 1 [(let v auto (call random::get_random [1000])) (= (at Data (+ i 1)) v)])
    (stmt (call dump_array [SIZE (& (at Data 1))]))
    (print [NEWLINE])
    (print [SIZE NEWLINE])
    (stmt (call heap_sort [SIZE (& mut (at Data 0))]))
    (print [NEWLINE])
    (stmt (call dump_array [SIZE (& (at Data 1))]))
    (print [NEWLINE])
    (for i u64 1 SIZE 1 :
        (if (> (at Data i) (at Data (+ i 1))) :
            (print [ERROR])
            (trap)
            :))
    (return 0))

)


