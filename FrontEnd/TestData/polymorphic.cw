(module $builtin [] [

(fun pub extern memcpy [(param dst (ptr mut u8)) (param src (ptr u8)) (param size uint)] (ptr mut u8) [])
(fun pub extern write [(param fd s32) (param s (ptr u8)) (param size uint)] sint [])
(fun pub extern SysErrorPrint [(param buffer (slice u8))] void [])

(fun pub SysPrint [(param buffer (slice u8))] void [
     (stmt (call write [1_s32 (front buffer) (len buffer)]))
])

(fun pub mymemcpy [(param dst (ptr mut u8)) (param src (ptr u8)) (param size uint)] uint [
    (for i uint 0 size 1 [
        (= (^(incp dst i)) (^ (incp src i)))])
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

(# "This gets passed to the actual formatters which decide how to interpret the options.")
(defrec pub SysFormatOptions [
    (# "min width")
    (field witdh u8)
    (field precission u8)
    (field padding u8)
    (field style u8)
    (field show_sign bool)
    (field left_justify bool)
])

(fun polymorphic SysRender [(param v bool) 
                            (param buffer (slice mut u8)) 
                            (param options (ptr mut SysFormatOptions))] uint [
    (let s auto (? v (as "true" (slice u8)) (as "false" (slice u8))))                           
    (let n uint (min (len buffer) (len s)))
    (return (call mymemcpy [(front mut buffer) (front s) n]))
])

(macro unsigned_to_str [(macro_param $val EXPR) 
                        (macro_param $base EXPR)
                        (macro_param $max_width EXPR)
                        (# "a slice for the output string")
                        (macro_param $out ID)]  [$v $tmp $pos] [
    (# "unsigned to str with give base")
    (macro_let mut $v auto $val)
    (macro_let mut $tmp auto (array_val $max_width u8 []))
    (macro_let mut $pos uint $max_width)
    (block _ [
        (-= $pos 1)
        (let c auto (% $v $base))
        (let mut c8 auto (as c u8))
        (+= c8 (? (<= c8 9) '0' (- 'a' 10)))
        (= (at $tmp $pos) c8)
        (/= $v $base)
        (if (!= $v 0) [(continue)] [])
    ])
    (let n uint (min (- $max_width $pos) (len $out)))
    (return (call mymemcpy [(front mut $out) (incp (front $tmp) $pos) n]))
])

(fun polymorphic SysRender [(param v u8) 
                            (param out (slice mut u8)) 
                            (param options (ptr mut SysFormatOptions))] uint [
    
    (unsigned_to_str v 10 32_uint out)
])


(fun polymorphic SysRender [(param v u16) 
                            (param out (slice mut u8)) 
                            (param options (ptr mut SysFormatOptions))] uint [
    
    (unsigned_to_str v 10 32_uint out)
])


(fun polymorphic SysRender [(param v u32) 
                            (param out (slice mut u8)) 
                            (param options (ptr mut SysFormatOptions))] uint [
    
    (unsigned_to_str v 10 32_uint out)
])


(fun polymorphic SysRender [(param v u64) 
                            (param out (slice mut u8)) 
                            (param options (ptr mut SysFormatOptions))] uint [
    
    (unsigned_to_str v 10 32_uint out)
])


(fun polymorphic SysRender [(param v (slice u8)) 
                            (param buffer (slice mut u8)) 
                            (param options (ptr mut SysFormatOptions))] uint [
    (let n uint (min (len buffer) (len v)))
    (return (call mymemcpy [(front mut buffer) (front v) n]))
])

(macro print_common [(macro_param $curr ID) (macro_param $parts STMT_LIST)] 
                    [$buffer $options $buffer_orig] [
    (macro_let mut $buffer auto (array_val 1024 u8))
    (macro_let mut $curr (slice mut u8) $buffer)
    (macro_let mut ref $options auto (rec_val SysFormatOptions []))
    (macro_for $i $parts [
        (= $curr (incp $curr (call polymorphic SysRender [$i $curr (& mut $options)])))
    ])
    (macro_let $buffer_orig (slice u8) $buffer)
    (stmt (call SysPrint [(pdelta $buffer_orig $curr)])) 
])


(macro pub print [(macro_param $parts STMT_LIST)] [$curr] [
    (print_common $curr [$parts])
    (stmt (call SysPrint [$curr])) 
])

])


(module main [] [
    (fun main [(param argc s32) (param argv (ptr (ptr u8)))] s32 [   
        (let mut ref opt auto (rec_val SysFormatOptions []))
        (let mut buffer auto (array_val 1024 u8))
        (let mut ref s (slice mut u8) buffer)
        (let mut n uint 0)
        (= n (call polymorphic SysRender [666_uint s (& mut opt)]))
        (let s2 auto (slice_val (front s) n))
        (stmt (call SysPrint [s2]))
        (stmt (call SysPrint ["OK\n"]))
        (return 0)
])


])