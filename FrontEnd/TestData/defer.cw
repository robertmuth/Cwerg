(module main [] [
(# "main module with program entry point `main`")

(fun pub extern write [(param fd s32) (param s (ptr u8)) (param size uint)] sint [])
(fun pub write_slice [(param fd s32) (param s (slice u8))] sint [
    (return (call write [fd (front s) (len s)]))
])


(fun main [(param argc s32) (param argv (ptr (ptr u8)))] s32 [
    (defer [
        (stmt (call write_slice [1 "defer fun 1\n"]))
    ])
    (defer [
        (stmt (call write_slice [1 "defer fun 2\n"]))
    ])
    (stmt (call write_slice [1 "fun start\n"]))
    (block _ [
        (defer [
            (stmt (call write_slice [1 "defer block 1\n"]))
        ])
        (defer [
            (stmt (call write_slice [1 "defer block 2\n"]))
        ])
        (stmt (call write_slice [1 "block start\n"]))
        (stmt (call write_slice [1 "block end\n"]))
    ])
    (stmt (call write_slice [1 "fun end\n"]))
    (return 0)
])

])
