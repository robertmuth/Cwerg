(module bytestream [] :
(import fmt)

@doc "the input bitstream was corrupted"
(type @pub @wrapped OutOfBoundsError void)
(global @pub OutOfBoundsErrorVal auto (wrap void_val OutOfBoundsError))


@doc ""
(fun IncSliceUnchecked  [
    (param buffer (ptr @mut (slice u8)))  (param n uint)] void :
    (let length uint (len (^ buffer)))
    (= (^ buffer) (slice_val (incp (front (^ buffer)) n) (- length n)))
)


@doc ""
(fun IncSliceOrDie  [
    (param buffer (ptr @mut (slice u8)))  (param n uint)] void :
    (let length uint (len (^ buffer)))
    (= (^ buffer) (slice_val (incp (front (^ buffer)) n length) (- length n)))
)


@doc ""
(fun @pub FrontSliceOrDie [
    (param buffer (ptr @mut (slice u8))) (param n uint)] (slice u8) :
    (let out auto (slice_val (front (^ buffer)) n))
    (stmt (IncSliceOrDie [buffer n]))
    (return out)
)

@doc ""
(fun @pub FrontSliceUnchecked [
    (param buffer (ptr @mut (slice u8))) (param n uint)] (slice u8) :
    (let out auto (slice_val (front (^ buffer)) n))
    (stmt (IncSliceUnchecked [buffer n]))
    (return out)
)

@doc ""
(fun @pub FrontSlice [
    (param buffer (ptr @mut (slice u8))) (param n uint)]
            (union [(slice u8) OutOfBoundsError]) :
    (if (<= (len  (^ buffer)) n) :
        (return OutOfBoundsErrorVal)
    :)

    (let out (slice u8) (slice_val (front (^ buffer)) n))
    (stmt (IncSliceUnchecked [buffer n]))
    (return out)
)

@doc ""
(fun @pub FrontLeU8Unchecked [(param buffer (ptr @mut (slice u8)))] u8 :
    (let out u8 (at @unchecked (^ buffer) 0))
    (stmt (IncSliceUnchecked [buffer 1]))
    (return out)
)


@doc ""
(fun @pub FrontLeU8OrDie [(param buffer (ptr @mut (slice u8)))] u8 :
    (if (== (len  (^ buffer)) 0) : (trap) :)
    (return (FrontLeU8Unchecked [buffer]))
)


@doc ""
(fun @pub FrontLeU8 [(param buffer (ptr @mut (slice u8)))] (union [u8 OutOfBoundsError]):
    (if (== (len  (^ buffer)) 0) : (return OutOfBoundsErrorVal) :)
    (return (FrontLeU8Unchecked [buffer]))
)


@doc ""
(fun @pub FrontLeU16Unchecked [(param buffer (ptr @mut (slice u8)))] u16 :
    (let out0 auto (as (at @unchecked (^ buffer) 0) u16))
    (let out1 auto (as (at @unchecked (^ buffer) 1) u16))
    (stmt (IncSliceUnchecked [buffer 2]))
    (return (+ out0 (<< out1 8)))
)


@doc ""
(fun @pub FrontLeU16OrDie [(param buffer (ptr @mut (slice u8)))] u16 :
    (if (<= (len  (^ buffer)) 1) : (trap) :)
    (return (FrontLeU16Unchecked [buffer]))
)


@doc ""
(fun @pub FrontLeU16 [(param buffer (ptr @mut (slice u8)))] (union [u16 OutOfBoundsError]):
    (if (== (len  (^ buffer)) 1) : (return OutOfBoundsErrorVal) :)
    (return (FrontLeU16Unchecked [buffer]))
)


@doc ""
(fun @pub FrontLeU32Unchecked [(param buffer (ptr @mut (slice u8)))] u32 :
    (let out0 auto (as (at @unchecked (^ buffer) 0) u32))
    (let out1 auto (as (at @unchecked (^ buffer) 1) u32))
    (let out2 auto (as (at @unchecked (^ buffer) 2) u32))
    (let out3 auto (as (at @unchecked (^ buffer) 3) u32))
    (stmt (IncSliceUnchecked [buffer 4]))
    (return (+ (+ (+ out0 (<< out1 8)) (<< out2 16)) (<< out3 24)))
)


@doc ""
(fun @pub FrontLeU32OrDie [(param buffer (ptr @mut (slice u8)))] u32 :
    (if (<= (len  (^ buffer)) 3) : (trap) :)
    (return (FrontLeU32Unchecked [buffer]))

)


@doc ""
(fun @pub FrontLeU32 [(param buffer (ptr @mut (slice u8)))] (union [u32 OutOfBoundsError]):
    (if (== (len  (^ buffer)) 3) : (return OutOfBoundsErrorVal) :)
    (return (FrontLeU32Unchecked [buffer]))
)

)