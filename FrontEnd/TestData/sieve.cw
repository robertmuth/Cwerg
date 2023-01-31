(module main [] [
(# "sieve")

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

(global SIZE uint 1000000)
(global EXPECTED uint 148932)
(# "index i reprents number 3 + 2 * i")
(global mut is_prime (array SIZE u8) (array_val u8 SIZE [(IndexVal 0 0)]))

(fun sieve [] uint [
   (# "initially every number is assumed prime")
   (for i uint 0 SIZE 1 [(= (at is_prime i) 1)])
   (# "run the sieve")
   (let mut count uint 0)
   (for i uint 0 SIZE 1 [
      (if (!= (at is_prime i) 0) [
         (= count (+ count 1))
         (let p uint (+ 3 (+ i i)))
         (for k uint (+ i p) SIZE p [(= (at is_prime k) 0)])
      ] [])
   ])
   (return count)
])

(fun main [(param argc s32) (param argv (ptr (ptr u8)))] s32 [
      (if (!= (call sieve []) EXPECTED) [(trap)] [])
      (return 0)
])

])
