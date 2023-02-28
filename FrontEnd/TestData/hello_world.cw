(module main [] [
   (# "main module with program entry point `main`")

   (fun pub extern write [(param fd s32) (param s (ptr u8)) (param size uint)] sint [])

   (global msg auto "hello world\n")

   (fun main [(param argc s32) (param argv (ptr (ptr u8)))] s32 [
            (stmt discard (call write [1 (front msg) (len msg)]))
         (return 0)
   ])
])
