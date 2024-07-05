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
    (field cid s32)
    (field ssx s32)
    (field ssy s32)
    (field width u32)
    (field height u32)
    (field stride s32)
    (field qtsel s32)
    (field actabsel s32)
    (field dctabsel s32)
    (field dcpred s32))


(defrec Context :
    (field size s32)
    (field length s32)
    (field width u16)
    (field height u16)
    (field mbwidth s32)
    (field mbheight s32)
    (field mbsizex s32)
    (field mbsizey s32)
    (field ncomp u8)
    (field comp (array 3 Component))
    (field qtused s32)
    (field qtavail s32)
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


(fun DecodeStartOfFrame [(param data (ptr! (slice u8))) (param out (ptr! Context))] (union [
        Success
        CorruptionError
        UnsupportedError
        BS::OutOfBoundsError]) :
    (let start_size auto (len (^ data)))
    (trylet l u16 (BS::FrontBeU16 [data]) err :
        (return err))
    (trylet format u8 (BS::FrontU8 [data]) err :
        (return err))
    (if (!= format 8) :
        (return UnsupportedErrorVal)
     :)
    (tryset (^. out height) (BS::FrontBeU16 [data]) err :
        (return err))
    (tryset (^. out width) (BS::FrontBeU16 [data]) err :
        (return err))
    (tryset (^. out ncomp) (BS::FrontU8 [data]) err :
        (return err))
    (if (&& (!= (^. out ncomp) 1) (!= (^. out ncomp) 3)) :
        (return UnsupportedErrorVal)
     :))


@pub (fun DecodeImage [(param a_data (slice u8))] (union [
        Success
        CorruptionError
        UnsupportedError
        BS::OutOfBoundsError]) :
    (@ref let ctx Context undef)
    (@ref let! data auto a_data)
    (trylet magic u16 (BS::FrontBeU16 [(&! data)]) err :
        (return err))
    (if (!= magic 0xffda) :
        (return CorruptionErrorVal)
     :)
    (while true :
        (trylet kind u16 (BS::FrontBeU16 [(&! data)]) err :
            (return err))
        (cond :
            (case (== kind 0xffc0) :)
            (case (== kind 0xffc4) :)
            (case (== kind 0xffdb) :)
            (case (== kind 0xffdd) :)
            (case (== kind 0xffda) :)
            @doc "TBD"
            (case (== kind 0xfffe) :
                (trylet l u16 (BS::FrontBeU16 [(&! data)]) err :
                    (return err))
                (do (BS::Skip [(&! data) (as l uint)])))
            @doc "TBD"
            (case (== (and kind 0xfff0) 0xffe0) :
                (trylet l u16 (BS::FrontBeU16 [(&! data)]) err :
                    (return err))
                (do (BS::Skip [(&! data) (as l uint)])))
            (case true :
                (return UnsupportedErrorVal))))
    (return SuccessVal))
)

