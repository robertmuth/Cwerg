(module bytestream [] :
(import fmt)

@doc "the input bitstream was corrupted"
@pub (@wrapped type OutOfBoundsError void)
@pub (global OutOfBoundsErrorVal auto (wrap void_val OutOfBoundsError))


@doc ""
(fun IncSliceUnchecked  [
    (param buffer (ptr! (slice u8)))  (param n uint)] void :
    (let length uint (len (^ buffer)))
    (= (^ buffer) (slice_val (pinc (front (^ buffer)) n) (- length n)))
)


@doc ""
(fun IncSliceOrDie  [
    (param buffer (ptr! (slice u8)))  (param n uint)] void :
    (let length uint (len (^ buffer)))
    (= (^ buffer) (slice_val (pinc (front (^ buffer)) n length) (- length n)))
)


@doc ""
@pub (fun FrontSliceOrDie [
    (param buffer (ptr! (slice u8))) (param n uint)] (slice u8) :
    (let out auto (slice_val (front (^ buffer)) n))
    (shed (IncSliceOrDie [buffer n]))
    (return out)
)

@doc ""
@pub (fun FrontSliceUnchecked [
    (param buffer (ptr! (slice u8))) (param n uint)] (slice u8) :
    (let out auto (slice_val (front (^ buffer)) n))
    (shed (IncSliceUnchecked [buffer n]))
    (return out)
)

@doc ""
@pub (fun FrontSlice [
    (param buffer (ptr! (slice u8))) (param n uint)]
            (union [(slice u8) OutOfBoundsError]) :
    (if (<= (len  (^ buffer)) n) :
        (return OutOfBoundsErrorVal)
    :)

    (let out (slice u8) (slice_val (front (^ buffer)) n))
    (shed (IncSliceUnchecked [buffer n]))
    (return out)
)

@doc ""
@pub (fun FrontLeU8Unchecked [(param buffer (ptr! (slice u8)))] u8 :
    (let out u8 (@unchecked at (^ buffer) 0))
    (shed (IncSliceUnchecked [buffer 1]))
    (return out)
)


@doc ""
@pub (fun FrontLeU8OrDie [(param buffer (ptr! (slice u8)))] u8 :
    (if (== (len  (^ buffer)) 0) : (trap) :)
    (return (FrontLeU8Unchecked [buffer]))
)


@doc ""
@pub (fun FrontLeU8 [(param buffer (ptr! (slice u8)))] (union [u8 OutOfBoundsError]):
    (if (== (len  (^ buffer)) 0) : (return OutOfBoundsErrorVal) :)
    (return (FrontLeU8Unchecked [buffer]))
)


@doc ""
@pub (fun FrontLeU16Unchecked [(param buffer (ptr! (slice u8)))] u16 :
    (let out0 auto (as (@unchecked at (^ buffer) 0) u16))
    (let out1 auto (as (@unchecked at (^ buffer) 1) u16))
    (shed (IncSliceUnchecked [buffer 2]))
    (return (+ out0 (<< out1 8)))
)


@doc ""
@pub (fun FrontLeU16OrDie [(param buffer (ptr! (slice u8)))] u16 :
    (if (<= (len  (^ buffer)) 1) : (trap) :)
    (return (FrontLeU16Unchecked [buffer]))
)


@doc ""
@pub (fun FrontLeU16 [(param buffer (ptr! (slice u8)))] (union [u16 OutOfBoundsError]):
    (if (== (len  (^ buffer)) 1) : (return OutOfBoundsErrorVal) :)
    (return (FrontLeU16Unchecked [buffer]))
)


@doc ""
@pub (fun FrontLeU32Unchecked [(param buffer (ptr! (slice u8)))] u32 :
    (let out0 auto (as (@unchecked at (^ buffer) 0) u32))
    (let out1 auto (as (@unchecked at (^ buffer) 1) u32))
    (let out2 auto (as (@unchecked at (^ buffer) 2) u32))
    (let out3 auto (as (@unchecked at (^ buffer) 3) u32))
    (shed (IncSliceUnchecked [buffer 4]))
    (return (+ (+ (+ out0 (<< out1 8)) (<< out2 16)) (<< out3 24)))
)


@doc ""
@pub (fun FrontLeU32OrDie [(param buffer (ptr! (slice u8)))] u32 :
    (if (<= (len  (^ buffer)) 3) : (trap) :)
    (return (FrontLeU32Unchecked [buffer]))

)


@doc ""
@pub (fun FrontLeU32 [(param buffer (ptr! (slice u8)))] (union [u32 OutOfBoundsError]):
    (if (== (len  (^ buffer)) 3) : (return OutOfBoundsErrorVal) :)
    (return (FrontLeU32Unchecked [buffer]))
)

)