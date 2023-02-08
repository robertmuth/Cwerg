(module main [] [
(# "heapsort")

(fun pub extern memcpy [(param dst (ptr mut u8)) (param src (ptr u8)) (param size uint)] (ptr mut u8) [])
(fun pub extern write [(param fd s32) (param s (ptr u8)) (param size uint)] sint [])

(fun mymemcpy [(param dst (ptr mut u8)) (param src (ptr u8)) (param size uint)] uint [
   (stmt discard (call memcpy [dst src size]))
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

(# "macro for while-loop")
(macro pub while [(macro_param $cond EXPR) 
                  (macro_param $body STMT_LIST)] [] [
    (block _ [
          (if $cond [] [(break)])
          $body
          (continue)
    ])
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
    (return (call mymemcpy [buf (& (at tmp pos)) (- 32 pos)]))
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
         (if (== sign_bit 0) [(return (call mymemcpy [buf (& (at INF_POS 0)) (len INF_POS)]))] 
         [(return (call mymemcpy [buf (& (at INF_NEG 0)) (len INF_NEG)]))])       
      ] [
         (if (== sign_bit 0) [(return (call mymemcpy [buf (& (at NAN_POS 0)) (len NAN_POS)]))] 
         [(return (call mymemcpy [buf (& (at NAN_NEG 0)) (len NAN_NEG)]))])       
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
   (+= i 1)

   (while (!= frac_bits 0) [
      (let c auto (as (>> frac_bits 48) u8))
      (= (^ (incp buf i)) 
         (? (<= c 9) (+ c '0') (+ c (- 'a' 10))))
      (+= i 1)
      (and= frac_bits 0xffff_ffff_ffff)
      (<<= frac_bits 4)
   ])
      
   (= (^ (incp buf i)) 'p')
   (+= i 1)
   (if (< exp 0) [
      (= (^ (incp buf i)) '-')
      (+= i 1)
      (= exp (- 0_s64 exp))
    ] [])
   (+= i (call u64_to_str [(as exp u64) 10 (incp buf i)]))
   (return i)
])


(global IM u32 139968)
(global IA u32 3877)
(global IC u32 29573)
(global mut LAST u32 42)

(fun get_random [(param max r64)] r64 [
   (= LAST (% (+ (* LAST IA) IC) IM))
   (return (/ (* max (as LAST r64)) (as IM r64)))
])

(global SIZE uint 20)

(global mut Data (array SIZE r64) (array_val SIZE r64 []))

(global NEWLINE auto "\n")

(fun heap_sort [(param n uint) (param data (ptr mut r64))] void [
  (let mut ir auto n)
  (let mut l auto (+ (>> n 1) 1))
  (let mut rdata r64 undef)
  (while true [
      (if (> l 1) [
         (-= l 1)
         (= rdata (^ (incp data l)))
      ] [
         (= rdata (^(incp data ir)))
         (= (^(incp data ir)) (^(incp data 1_uint)))
         (-= ir 1)
         (if (== ir 1) [
            (= (^(incp data ir)) rdata)
            (return)
         ] [])
      ])
    (let mut i auto l)
    (let mut j auto (<< l 1))
    (while (<= j ir) [
       (if (&& (< j ir) (< (^(incp data j)) (^(incp data (+ j 1))))) [(+= j 1)][])
       (if (< rdata (^(incp data j))) [
         (= (^(incp data i)) (^(incp data j)))
         (= i j)
         (+= j i)
       ][
         (= j (+ ir 1))
       ])
    ])
    (= (^(incp data i)) rdata)
  ])
  (return)
])

(fun dump_array [(param size uint) (param data (ptr r64))] void [
  (let mut buf (array 32 u8) undef)
  (for i u64 0 size 1 [
    (let v auto (^ (incp data i)))
    (let n auto (call r64_to_hex_fmt [v (& mut (at buf 0))]))
    (stmt discard (call write [1 (& (at buf 0)) n]))
    (stmt discard (call write [1 (& (at NEWLINE 0)) (len NEWLINE)]))
  ])
  (return)
])


(fun test [(param a uint)(param b uint)(param c uint)(param d uint) ] uint [
    (if (&& (< a b) (< c d)) [(return 666)][(return 777)])

])

(fun main [(param argc s32) (param argv (ptr (ptr u8)))] s32 [
   (for i u64 0 SIZE 1 [
     (let v auto (call get_random [1000]))
     (= (at Data i) v)
   ])

   (stmt (call dump_array [SIZE  (& (at Data 0))]))
   (stmt discard (call write [1 (& (at NEWLINE 0)) (len NEWLINE)]))
   (stmt (call heap_sort [SIZE (& mut (at Data 0))]))
   (stmt (call dump_array [SIZE  (& (at Data 0))]))

   (return 0)
])

])
