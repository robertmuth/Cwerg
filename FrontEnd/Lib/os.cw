(module os [] :

@pub (defrec TimeSpec :
    (field sec uint)
    (field nano_sec uint))

@pub @cdecl @extern (fun nanosleep [
    (param req (ptr TimeSpec))
    (param rem (ptr! TimeSpec))] s32 :)

@pub @cdecl @extern (fun write [
        (param fd s32)
        (param s (ptr u8))
        (param size uint)] sint :)

@pub @cdecl @extern (fun read [
        (param fd s32)
        (param s (ptr! u8))
        (param size uint)] sint :)


@pub (type @wrapped Error s32)
@pub (type @wrapped FD s32)

@pub (global Stdin auto (wrap 0 FD))
@pub (global Stdout auto (wrap 1 FD))
@pub (global Stderr auto (wrap 2 FD))

@pub (fun FileWrite [
        (param fd FD) (param buffer (slice u8))] (union [uint Error])  :
    (let res auto (write [(unwrap fd) (front buffer) (len buffer)]))
    (if (< res 0) :
          (return (wrap (as res s32) Error))
    :
          (return (as res uint))
    )

)

@pub (fun FileRead [
        (param fd FD) (param buffer (slice! u8))] (union [uint Error]):
    (let res auto (read [(unwrap fd) (front! buffer) (len buffer)]))
    (if (< res 0) :
          (return (wrap (as res s32) Error))
    :
          (return (as res uint))
    )
)


@pub (fun TimeNanoSleep [(param req (ptr TimeSpec))
                                  (param rem (ptr! TimeSpec))] Error :
    (let res auto (nanosleep [req rem]))
    (return (wrap res Error))
)

)