(module os [] :

(fun @pub @extern nanosleep [
    (param req (ptr TimeSpec)) 
    (param rem (ptr @mut TimeSpec))] s32 :)

(fun @pub @extern write [
        (param fd s32)
        (param s (ptr u8))
        (param size uint)] sint :)

(fun @pub @extern read [
        (param fd s32)
        (param s (ptr @mut u8))
        (param size uint)] sint :)


(type @pub @wrapped Error s32)
(type @pub @wrapped FD s32)

(global Stdin auto (as 0_u32 FD))
(global Stdout auto (as 1_u32 FD))
(global Stderr auto (as 2_u32 FD))

(fun @pub FileWrite [
        (param fd FD) (param buffer (slice u8))] (union [uint Error])  :
    (let res auto (call write [(as fd s32) (front buffer) (len buffer)]))
    (if (< res 0) :
          (return (as res Error))
    :
          (return (as res uint))
    )

)

(fun @pub FileRead [
        (param fd FD) (param buffer (slice @mut u8))] (union [uint Error]):
    (let res auto (call read [(as fd s32) (front @mut buffer) (len buffer)]))
    (if (< res 0) :
          (return (as res Error))
    :
          (return (as res uint))
    ) 
)


(defrec @pub TimeSpec :
    (field sec uint)
    (field nano_sec uint))


(fun @pub TimeNanoSleep [(param req (ptr TimeSpec)) 
                                  (param rem (ptr @mut TimeSpec))] Error :
    (let res auto (call nanosleep [req rem]))
    (return (as res Error))
)

)