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

(# "macro for while-loop")
(macro pub while [(macro_param $cond EXPR) 
                  (macro_param $body STMT_LIST)] [] [
    (block _ [
          (if $cond [] [(break)])
          $body
          (continue)
    ])
])      

(fun pub memcpy [(param dst (ptr mut u8)) (param src (ptr u8)) (param len uint)] uint [
    (for i uint 0 len 1 [
        (= (^(incp dst i)) (^ (incp src i)))])
    (return len)
])

(global INF_POS auto "inf")
(global INF_NEG auto "-inf")
(global NAN_POS auto "nan")
(global NAN_NEG auto "-nan")

(fun u64_to_str [(param val u64) (param base u64) (param buf (ptr mut u8))] uint [
    (let mut v auto val)
    (let mut tmp (array 32 u8) undef)
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
    (return (call memcpy [buf (& (at tmp pos)) (- 32 pos)]))
])


(# "r64 format (IEEE 754):  sign (1 bit) exponent (11 bits) fraction (52 bits)")
(# "exponentiation bias is 1023")
(# "https://en.wikipedia.org/wiki/Double-precision_floating-point_format")
(# "https://observablehq.com/@jrus/hexfloat")
(fun r64_to_hex_fmt [(param val r64) (param buf (ptr mut u8))] uint [
   (let val_bits auto (bitcast val s64))
   (let mut frac_bits auto (and val_bits 0xf_ffff_ffff_ffff))
   (let exp_bits auto (and (>> val_bits 52) 0x7ff))
   (let sign_bit auto (and (>> val_bits 63) 1))
   
   (if (== exp_bits 0x7ff) [
      (if (== frac_bits 0) [
         (if (== sign_bit 0) [(return (call memcpy [buf (& (at INF_POS 0)) (len INF_POS)]))] 
         [(return (call memcpy [buf (& (at INF_NEG 0)) (len INF_NEG)]))])       
      ] [
         (if (== sign_bit 0) [(return (call memcpy [buf (& (at NAN_POS 0)) (len NAN_POS)]))] 
         [(return (call memcpy [buf (& (at NAN_NEG 0)) (len NAN_NEG)]))])       
      ])
   ] [])

   (let mut exp auto (- exp_bits 1023))
   (let mut i uint 0)
   (if (!= sign_bit 0) [(= (^ (incp buf i)) '-')] [])
   (+= i 1)
   (= (^ (incp buf i)) '0')
   (+= i 1)
   (= (^ (incp buf i)) 'x')
   (+= i 1)
   (= (^ (incp buf i)) (? (== exp_bits 0) '0' '1'))
   (+= i 1)
   (= (^ (incp buf i)) '.')
   (while (!= frac_bits 0) [
      (let c auto (as (>> frac_bits 48) u8))
      (+= i 1)
      (= (^ (incp buf i)) 
         (? (<= c 9) (+ c '0') (+ c (- 'a' 10))))
      (and= frac_bits 0xffff_ffff_ffff)
      (<<= frac_bits 4)
   ])
   (+= i 1)
   (= (^ (incp buf i)) 'p')
   (if (< exp 0) [
      (= (^ (incp buf i)) '-')
      (= exp (- 0_s64 exp))
    ] [])
   (+= i (call u64_to_str [(as exp u64) 10 (incp buf i)]))
   (return i)
])


(global IM uint 139968)
(global IA uint 3877)
(global IC uint 29573)
(global mut LAST uint 42)

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
