(module main [] [
   (# "main module with program entry point `main`")

   (# "library provided puts style function") 
   (fun pub extern write [(param fd s32) (param s (ptr u8)) (param size uint)] sint [])


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

   (# "macro for while-loop")
   (macro pub while [(macro_param $cond EXPR) 
                     (macro_param $body STMT_LIST)] [] [
      (block _ [
            (if $cond [] [(break)])
            $body
            (continue)
      ])
   ])   

   (fun strlen [(param s (ptr u8))] uint [
      (let mut i uint 0)
      (while (!= (^ (incp s i)) 0) [
         (= i (+ i 1))
      ])
      (return i)
   ])

   (global NEWLINE auto "\n")

   (fun main [(param argc s32) (param argv (ptr (ptr u8)))] s32 [
         (for i u32 0 (as argc u32) 1 [
            (let s (ptr u8) (^ (incp argv i)))
            (stmt (call write [1 s (call strlen [s])]))
            (stmt (call write [1 (front NEWLINE) (len NEWLINE)]))
         ])
         (return 0)
   ])
])
