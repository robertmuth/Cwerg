(module os [] :

(defrec @pub TimeSpec :
    (field sec uint)
    (field nano_sec uint))

(fun @pub @cdecl @extern nanosleep [
    (param req (ptr TimeSpec))
    (param rem (ptr! TimeSpec))] s32 :)

(fun @pub @cdecl @extern write [
        (param fd s32)
        (param s (ptr u8))
        (param size uint)] sint :)

(fun @pub @cdecl @extern read [
        (param fd s32)
        (param s (ptr! u8))
        (param size uint)] sint :)


(type @pub @wrapped Error s32)
(type @pub @wrapped FD s32)

(global @pub Stdin auto (wrap 0 FD))
(global @pub Stdout auto (wrap 1 FD))
(global @pub Stderr auto (wrap 2 FD))

(fun @pub FileWrite [
        (param fd FD) (param buffer (slice u8))] (union [uint Error])  :
    (let res auto (write [(unwrap fd) (front buffer) (len buffer)]))
    (if (< res 0) :
          (return (wrap (as res s32) Error))
    :
          (return (as res uint))
    )

)

(fun @pub FileRead [
        (param fd FD) (param buffer (slice! u8))] (union [uint Error]):
    (let res auto (read [(unwrap fd) (front! buffer) (len buffer)]))
    (if (< res 0) :
          (return (wrap (as res s32) Error))
    :
          (return (as res uint))
    )
)


(fun @pub TimeNanoSleep [(param req (ptr TimeSpec))
                                  (param rem (ptr! TimeSpec))] Error :
    (let res auto (nanosleep [req rem]))
    (return (wrap res Error))
)

)