@doc "heapsort"
(module heapsort [(modparam $type TYPE) (modparam $cmp_lt CONST_EXPR)] :

@pub (fun sort [(param sdata (slice! $type))] void :
    (let data (ptr! $type) (front! sdata))
    (let n auto (len sdata))
    (let! ir auto n)
    (let! l auto (+ (>> n 1) 1))
    (let! rdata $type undef)
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
            (if (&& (< j ir) (call $cmp_lt [(pinc data j) (pinc data (+ j 1))])) :
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
)

