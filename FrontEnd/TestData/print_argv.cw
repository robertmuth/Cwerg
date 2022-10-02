(mod main [] [
   (# "main module woth program entry point `main`")
   (fun pub extern write_s (sig [(param fd s32) (param s (ptr u8))] sint) [])

   (# "this is a comment with \" with quotes \t ")
   (fun main (sig [(param argc uint32) (param argv (ptr u8))] s32) [
         (for i u32 (range argc) [
            (let s (ptr u8) (at argv i))
         ])
         (return 0)
   ])
])
