(module main [] [
   (# "main module with program entry point `main`")

   (# "library provided puts style function") 
   (fun pub extern write [(param fd s32) (param s (ptr u8)) (param size uint)] sint [])

   (fun strlen [(param s (ptr u8))] uint [
      (let mut i uint 0)
      (while (!= (^ (incp s i)) 0) [
         (= i (+ i 1))
      ])
      (return i)
   ])

   (fun main [(param argc u32) (param argv (ptr (ptr u8)))] s32 [
         (for i u32 0 argc 1 [
            (let s (ptr u8) (^ (incp argv i)))
            (stmt discard (call write [1 s (call strlen [s])]))
         ])
         (return 0)
   ])
])
