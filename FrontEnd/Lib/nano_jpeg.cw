(module [] :
(import BS bytestream)


(global W1 s32 2841)


(global W2 s32 2676)


(global W3 s32 2408)


(global W5 s32 1609)


(global W6 s32 1108)


(global W7 s32 565)


@doc "updates blk in place"
(fun RowIDCT [(param blk (ptr! (array 8 s32)))] void :
    (let! x1 auto (<< (at (^ blk) 4) 11))
    (let! x2 auto (at (^ blk) 6))
    (let! x3 auto (at (^ blk) 2))
    (let! x4 auto (at (^ blk) 1))
    (let! x5 auto (at (^ blk) 7))
    (let! x6 auto (at (^ blk) 5))
    (let! x7 auto (at (^ blk) 3))
    (if (== (paren (or (or (or (or (or (or x1 x2) x3) x4) x5) x6) x7)) 0) :
        (let t auto (<< (at (^ blk) 0) 3))
        (for i 0 8_u32 1 :
            (= (at (^ blk) i) t))
        (return)
     :)
    (let! x0 auto (+ (paren (<< (at (^ blk) 0) 11)) 128))
    (let! x8 auto (* (+ x4 x5) W7))
    (= x4 (+ x8 (* x4 (- W1 W7))))
    (= x5 (- x8 (* x5 (+ W1 W7))))
    (= x8 (* (+ x6 x7) W3))
    (= x6 (- x8 (* x6 (- W3 W5))))
    (= x7 (- x8 (* x7 (+ W3 W5))))
    (= x8 (+ x0 x1))
    (-= x0 x1)
    (= x1 (* (+ x3 x2) W6))
    (= x2 (- x1 (* x2 (+ W2 W6))))
    (= x3 (+ x1 (* x3 (- W2 W6))))
    (= x1 (+ x4 x6))
    (-= x4 x6)
    (= x6 (+ x5 x7))
    (-= x5 x7)
    (= x7 (+ x8 x3))
    (-= x8 x3)
    (= x3 (+ x0 x2))
    (-= x0 x2)
    (= x2 (>> (+ (* (+ x4 x5) 181) 128) 8))
    (= x4 (>> (+ (* (- x4 x5) 181) 128) 8))
    (= (at (^ blk) 0) (>> (+ x7 x1) 8))
    (= (at (^ blk) 1) (>> (+ x3 x2) 8))
    (= (at (^ blk) 2) (>> (+ x0 x4) 8))
    (= (at (^ blk) 3) (>> (+ x8 x6) 8))
    (= (at (^ blk) 4) (>> (- x8 x6) 8))
    (= (at (^ blk) 5) (>> (- x0 x4) 8))
    (= (at (^ blk) 6) (>> (- x3 x2) 8))
    (= (at (^ blk) 7) (>> (- x7 x1) 8)))


@doc "clamp x to [0:255]"
(fun ClampU8 [(param x s32)] u8 :
    (cond :
        (case (< x 0) :
            (return 0))
        (case (>= x 0xff) :
            (return 0xff))
        (case true :
            (return (as x u8)))))


(fun ColIDCT [
        (param blk (ptr (array (* 8 8) s32)))
        (param out (slice! u8))
        (param stride uint)] void :
    (let! x1 auto (<< (at (^ blk) (* 8 4)) 8))
    (let! x2 auto (at (^ blk) (* 8 6)))
    (let! x3 auto (at (^ blk) (* 8 2)))
    (let! x4 auto (at (^ blk) (* 8 1)))
    (let! x5 auto (at (^ blk) (* 8 7)))
    (let! x6 auto (at (^ blk) (* 8 5)))
    (let! x7 auto (at (^ blk) (* 8 3)))
    (if (== (paren (or (or (or (or (or (or x1 x2) x3) x4) x5) x6) x7)) 0) :
        (let t auto (ClampU8 [(+ (paren (>> (+ (at (^ blk) 0) 32) 6)) 128)]))
        (for i 0 8_u32 1 :
            (= (at out (* i 8)) t))
        (return)
     :)
    (let! x0 auto (+ (paren (<< (at (^ blk) 0) 8)) 8192))
    (let! x8 auto (+ (* (+ x4 x5) W7) 4))
    (= x4 (>> (+ x8 (* x4 (- W1 W7))) 3))
    (= x5 (>> (- x8 (* x5 (+ W1 W7))) 3))
    (= x8 (+ (* (+ x6 x7) W3) 4))
    (= x6 (>> (- x8 (* x6 (- W3 W5))) 3))
    (= x7 (>> (- x8 (* x7 (+ W3 W5))) 3))
    (= x8 (+ x0 x1))
    (-= x0 x1)
    (= x1 (+ (* (+ x3 x2) W6) 4))
    (= x2 (>> (- x1 (* x2 (+ W2 W6))) 3))
    (= x3 (>> (+ x1 (* x3 (- W2 W6))) 3))
    (= x1 (+ x4 x6))
    (-= x4 x6)
    (= x6 (+ x5 x7))
    (-= x5 x7)
    (= x7 (+ x8 x3))
    (-= x8 x3)
    (= x3 (+ x0 x2))
    (-= x0 x2)
    (= x2 (>> (+ (* (+ x4 x5) 181) 128) 8))
    (= x4 (>> (+ (* (- x4 x5) 181) 128) 8))
    (= (at out (* 0 stride)) (ClampU8 [(+ (paren (>> (+ x7 x1) 14)) 128)]))
    (= (at out (* 1 stride)) (ClampU8 [(+ (paren (>> (+ x3 x2) 14)) 128)]))
    (= (at out (* 2 stride)) (ClampU8 [(+ (paren (>> (+ x0 x4) 14)) 128)]))
    (= (at out (* 3 stride)) (ClampU8 [(+ (paren (>> (+ x8 x6) 14)) 128)]))
    (= (at out (* 4 stride)) (ClampU8 [(+ (paren (>> (- x8 x6) 14)) 128)]))
    (= (at out (* 5 stride)) (ClampU8 [(+ (paren (>> (- x0 x4) 14)) 128)]))
    (= (at out (* 6 stride)) (ClampU8 [(+ (paren (>> (- x3 x2) 14)) 128)]))
    (= (at out (* 7 stride)) (ClampU8 [(+ (paren (>> (- x7 x1) 14)) 128)])))


(defrec Code :
    (field bits u8)
    (field code u8))


(defrec Component :
    (field cid u8)
    (field ssx u32)
    (field ssy u32)
    (field qtsel u8)
    (field width u32)
    (field height u32)
    (field stride u32))


(defrec Context :
    (field width u32)
    (field height u32)
    (field ncomp u8)
    (field mbsizex u32)
    (field mbsizey u32)
    (field mbwidth u32)
    (field mbheight u32)
    (field size s32)
    (field length s32)
    (field comp (array 3 Component))
    (field qtab (array 64 (array 4 u8))))


@pub (@wrapped type Success void)


@pub (global SuccessVal auto (wrap_as void_val Success))


@pub (@wrapped type CorruptionError void)


@pub (global CorruptionErrorVal auto (wrap_as void_val CorruptionError))


@pub (@wrapped type UnsupportedError void)


@pub (global UnsupportedErrorVal auto (wrap_as void_val UnsupportedError))


(fun DecodeScan [(param data (ptr! (slice u8)))] (union [
        Success
        CorruptionError
        UnsupportedError
        BS::OutOfBoundsError]) :
    (trylet l u16 (BS::FrontBeU16 [data]) err :
        (return err))
    (return SuccessVal))


(fun div_roundup [(param a u32) (param b u32)] u32 :
    (return (/ (- (+ a b) 1) b)))


(fun DecodeHufmanTable [(param chunk (slice u8)) (param vlctab (ptr (array 4 (array 65536 Code))))] (union [
        Success
        CorruptionError
        UnsupportedError
        BS::OutOfBoundsError]) :
    (@ref let! data auto chunk)
    (while (>= (len data) 17) :
        (let kind auto (BS::FrontU8Unchecked [(&! data)]))
        (if (!= (and kind 0xec) 0) :
            (return CorruptionErrorVal)
         :)
        (if (!= (and kind 0x02) 0) :
            (return UnsupportedErrorVal)
         :)
        @doc "combined DC/AC + tableid value"
        (let pos u32 (or (paren (>> (and (as kind u32) 0x1f) 3)) (paren (and (as kind u32) 1))))
        (let counts auto (BS::FrontSliceUnchecked [(&! data) 16]))
        (let! remain s32 65536)
        (let! spread s32 65536)
        (for codelen 0 16_s32 1 :
            (>>= spread 1)
            (let n auto (as (at counts codelen) s32))
            (if (== n 0) :
                (continue)
             :)
            (-= remain (<< n (- 15 codelen)))
            (if (< remain 0) :
                (return CorruptionErrorVal)
             :)
            (let words auto (BS::FrontSlice [(&! data) (as n uint)]))
            (for i 0 n 1 :
                (return SuccessVal)))))


(fun DecodeStartOfFrame [(param chunk (slice u8)) (param out (ptr! Context))] (union [
        Success
        CorruptionError
        UnsupportedError
        BS::OutOfBoundsError]) :
    (@ref let! data auto chunk)
    (trylet format u8 (BS::FrontU8 [(&! data)]) err :
        (return err))
    (if (!= format 8) :
        (return UnsupportedErrorVal)
     :)
    (trylet height u16 (BS::FrontBeU16 [(&! data)]) err :
        (return err))
    (= (^. out height) (as height u32))
    (trylet width u16 (BS::FrontBeU16 [(&! data)]) err :
        (return err))
    (= (^. out width) (as width u32))
    (trylet ncomp u8 (BS::FrontU8 [(&! data)]) err :
        (return err))
    (= (^. out ncomp) ncomp)
    (if (&& (!= ncomp 1) (!= ncomp 3)) :
        (return UnsupportedErrorVal)
     :)
    (let! ssxmax u32 0)
    (let! ssymax u32 0)
    (for i 0 ncomp 1 :
        (let comp (ptr! Component) (&! (paren (at (^. out comp) i))))
        (tryset (^. comp cid) (BS::FrontU8 [(&! data)]) err :
            (return err))
        (trylet ss u8 (BS::FrontU8 [(&! data)]) err :
            (return err))
        (let ssx auto (as (>> ss 4) u32))
        (let ssy auto (as (and ss 0xf) u32))
        @doc "ssy must be a power of two"
        (if (|| (|| (== ssx 0) (== ssy 0)) (!= (and ssy (- ssy 1)) 0)) :
            (return CorruptionErrorVal)
         :)
        (= (^. comp ssx) ssx)
        (= (^. comp ssy) ssy)
        (max= ssxmax ssx)
        (max= ssymax ssy)
        (trylet! qtsel u8 (BS::FrontU8 [(&! data)]) err :
            (return err))
        (and= qtsel 0xfc)
        (if (== qtsel 0) :
            (return CorruptionErrorVal)
         :)
        (= (^. comp qtsel) (and qtsel 0xfc)))
    (if (== ncomp 1) :
        (= ssxmax 1)
        (= ssymax 1)
        (= (. (at (^. out comp) 0) ssx) 1)
        (= (. (at (^. out comp) 0) ssy) 1)
     :)
    (let mbsizex u32 (* (as ssxmax u32) 8))
    (let mbsizey u32 (* (as ssymax u32) 8))
    (= (^. out mbsizex) mbsizex)
    (= (^. out mbsizey) mbsizey)
    (= (^. out mbwidth) (div_roundup [(^. out width) mbsizex]))
    (= (^. out mbheight) (div_roundup [(^. out height) mbsizey]))
    (for i 0 ncomp 1 :
        (let comp (ptr! Component) (&! (paren (at (^. out comp) i))))
        (= (^. comp width) (div_roundup [(* (^. out width) (^. comp ssx)) ssxmax]))
        (= (^. comp height) (div_roundup [(* (^. out height) (^. comp ssy)) ssymax]))
        (= (^. comp stride) (* (* (^. out mbwidth) (^. comp ssx)) 8))
        (if (&& (< (^. comp width) 3) (!= (^. comp ssx) ssxmax)) :
            (return CorruptionErrorVal)
         :)
        (if (&& (< (^. comp height) 3) (!= (^. comp ssy) ssymax)) :
            (return CorruptionErrorVal)
         :))
    (return SuccessVal))


@pub (fun DecodeImage [(param a_data (slice u8))] (union [
        Success
        CorruptionError
        UnsupportedError
        BS::OutOfBoundsError]) :
    (@ref let! ctx Context undef)
    (@ref let! data auto a_data)
    (trylet magic u16 (BS::FrontBeU16 [(&! data)]) err :
        (return err))
    (if (!= magic 0xffda) :
        (return CorruptionErrorVal)
     :)
    (while true :
        (trylet chunk_kind u16 (BS::FrontBeU16 [(&! data)]) err :
            (return err))
        (trylet chunk_length u16 (BS::FrontBeU16 [(&! data)]) err :
            (return err))
        (trylet chunk_slice (slice u8) (BS::FrontSlice [(&! data) (as chunk_length uint)]) err :
            (return err))
        (cond :
            (case (== chunk_kind 0xffc0) :
                (trylet dummy Success (DecodeStartOfFrame [chunk_slice (&! ctx)]) err :
                    (return err)))
            (case (== chunk_kind 0xffc4) :)
            (case (== chunk_kind 0xffdb) :)
            (case (== chunk_kind 0xffdd) :)
            (case (== chunk_kind 0xffda) :)
            @doc "TBD"
            (case (== chunk_kind 0xfffe) :)
            @doc "TBD"
            (case (== (and chunk_kind 0xfff0) 0xffe0) :)
            (case true :
                (return UnsupportedErrorVal))))
    (return SuccessVal))
)

