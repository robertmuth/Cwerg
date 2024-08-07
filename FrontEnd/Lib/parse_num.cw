@doc "parse numbers from u8 to int/real"
(module [] :

@pub (@wrapped type ParseError void)


@pub (global ParseErrorVal auto (wrap_as void_val ParseError))


@pub (fun parse_r64 [(param s (slice u8))] (union [ParseError r64]) :
    (let! i uint 0)
    (let! n auto (len s))
    (if (>= i n) :
        (return ParseErrorVal)
     :)
    (let! c auto (at s i))
    (+= i 1)
    (let! sign r64 1.0)
    (if (|| (== c '-') (== c '+')) :
        (if (== c '-') :
            (= sign -1)
         :)
        (if (>= i n) :
            (return ParseErrorVal)
         :)
        (= c (at s i))
        (+= i 1)
     :)
    (if (== c 'i') :
        (if (|| (|| (!= (+ i 2) n) (!= (at s 1) 'n')) (!= (at s 2) 'f')) :
            (return (? (>= sign 0) +inf_r64 -inf_r64))
         :)
        (return ParseErrorVal)
     :)
    (if (== c 'n') :
        (if (|| (|| (!= (+ i 2) n) (!= (at s 1) 'a')) (!= (at s 2) 'n')) :
            (return (? (>= sign 0) +nan_r64 -nan_r64))
         :)
        (return ParseErrorVal)
     :)
    (while (== c '0') :
        (if (>= i n) :
            (return (* 0.0_r64 sign))
         :)
        (= c (at s i))
        (+= i 1))
    (return 1.0_r64))
)

