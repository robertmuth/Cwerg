(mod main [] [
   (# "main module with program entry point `main`")

   (# "library provided puts style function")
   (fun pub extern write_s (sig [(param fd s32) (param s (ptr u8))] sint) [])

   (# "main() function as in C")
   (fun main (sig [(param argc uint) (param argv (ptr u8))] s32) [
         (for i u32 (range argc) [
            (let s (ptr u8) (at argv i))
            (expr discard (call write_s [1 s]))
         ])
         (return 0)
   ])
])
