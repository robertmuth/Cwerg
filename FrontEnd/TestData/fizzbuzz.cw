(module main [] [
(# "heapsort")

(fun pub extern memcpy [(param dst (ptr mut u8)) (param src (ptr u8)) (param size uint)] (ptr mut u8) [])
(fun pub extern write [(param fd s32) (param s (ptr u8)) (param size uint)] sint [])

(fun mymemcpy [(param dst (ptr mut u8)) (param src (ptr u8)) (param size uint)] uint [
   (stmt (call memcpy [dst src size]))
   (return size)
])

(# "macro for number range for-loop")
(macro pub for [(macro_param $index ID) 
                (macro_param $type TYPE) 
                (macro_param $start EXPR) 
                (macro_param $end EXPR) 
                (macro_param $step EXPR) 
                (macro_param $body STMT_LIST)] [$end_eval $step_eval $it] [
    
    (macro_let $end_eval $type $end)
    (macro_let $step_eval $type $step)
    (macro_let mut $it $type $start)
    (block _ [
          (if (>= $it $end_eval) [(break)] [])
          (macro_let $index auto $it)
          (= $it (+ $it $step_eval))
          $body
          (continue)
    ])
])


(fun u64_to_str [(param val u64) (param base u64) (param buf (ptr mut u8))] uint [
    (let mut v auto val)
    (let mut ref tmp (array 32 u8) undef)
    (let mut pos uint 32)
    (block _ [
        (-= pos 1)
        (let c auto (% v base))
        (let mut c8 auto (as c u8))
        (+= c8 (? (<= c8 9) '0' (- 'a' 10)))
        (= (at tmp pos) c8)
        (/= v base)
        (if (!= v 0) [(continue)] [])
    ])
    (return (call mymemcpy [buf (& (at tmp pos)) (- 32 pos)]))
])


(global NEWLINE auto "\n")
(global FIZZ auto "FIZZ")
(global BUZZ auto "BUZZ")
(global FIZZBUZZ auto "FIBU")


(fun main [(param argc s32) (param argv (ptr (ptr u8)))] s32 [
   (for i u64 0 31 1 [
      (cond [
         (case (== (% i 15) 0) [
            (stmt (call write [1 (front FIZZBUZZ) (len FIZZBUZZ)]))]) 
         (case (== (% i 3) 0) [
            (stmt (call write [1 (front FIZZ) (len FIZZ)]))])
         (case (== (% i 5) 0) [
            (stmt (call write [1 (front BUZZ) (len BUZZ)]))])
         (case true [
            (let mut ref buf (array 32 u8) undef)
            (let n auto (call u64_to_str [i 10 (& mut (at buf 0))]))
            (stmt (call write [1 (& (at buf 0)) n]))
         ]) 
      ])
      (stmt (call write [1 (front NEWLINE) (len NEWLINE)]))

   ])

   (return 0)
])

])
