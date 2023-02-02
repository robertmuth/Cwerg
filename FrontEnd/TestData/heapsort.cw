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

(global IM uint 139968)
(global IA uint 3877)
(global IC uint 29573)
(global mut LAST uint 42)

(# "r64 format (IEEE 754):  sign (1 bit) exponent (11 bits) fraction (52 bits)")
(# "exponentiation bias is 1023")
(# "https://en.wikipedia.org/wiki/Double-precision_floating-point_format")
(fun real_to_hex_fmt [(param val r64) (param buf (ptr mut u8))] uint [
   (let val_bits auto (bitcast val u64))
   (let frac auto (and val_bits 0xf_ffff_ffff_ffff))
   (let exp auto (and (>> val_bits 52) 0x7ff))
   (let sign auto (!= (>> val_bits 63) 0))
   (return 0)
])

(fun get_random [(param max r64)] r64 [
   (= LAST (% (+ (* LAST IA) IC) IM))
   (return (/ (* max (as LAST r64)) (as IM r64)))
])

(global SIZE uint 2000000)

(global mut data (array SIZE r64) (array_val SIZE r64 []))


(fun main [(param argc s32) (param argv (ptr (ptr u8)))] s32 [
      (return 0)
])

])
