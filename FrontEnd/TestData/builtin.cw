(module $builtin [] [
(# "Macro Examples")


(# "This gets passed to the actual formatters which decide how to interpret the options.")
(defrec pub SysFormatOptions [
    (# "min width")
    (field witdh u8 0)
    (field precission u8 0)
    (field padding u8 0)
    (field style u8 0)
    (field show_sign bool false)
    (field left_justify bool false)
])



(fun pub extern SysErrorPrint [(param buffer (slice u8))] void [])
(fun pub extern SysPrint [(param buffer (slice u8))] void [])


(# "macro for c-style -> operator")
(macro pub -> [(macro_param $pointer EXPR) (macro_param $field FIELD)] [] [
       (. (^ $pointer) $field)
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
          (+=  $it $step_eval)
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


(macro pub try [(macro_param $name ID) 
                (macro_param $type EXPR) 
                (macro_param $expr EXPR) 
                (macro_param $catch_name ID) 
                (macro_param $catch_body STMT_LIST)] [] [
    (if (is $expr $type) [] [
        (macro_let $catch_name auto (asnot $expr $type))
        (macro_id $catch_body)
        (trap)
    ]) 
    (macro_let $name (tryas $expr $type undef))
])


(fun pub extern IsLogActive [(param level u8) (param loc u32)] void [])


(fun pub extern print [(param buffer (slice u8))] void [])


(# "generic copy of data from slice/array to slice")
(macro copy_slice [(macro_param $item_type TYPE) 
                   (macro_param $src EXPR)
                   (macro_param $dst EXPR)
                   (macro_param $len EXPR)] [$psrc $pdst $n $i] [
    (macro_let $psrc auto (as $src (ptr $item_type))) 
    (macro_let $pdst auto (as $dst (ptr mut $item_type)))
    (macro_let $n uint $len)
    (for $i uint 0 $n 1 [
        (= (^(incp $pdst $i)) (^ (incp $psrc $i)))])
])


(fun pub memcpy [(param dst (ptr mut u8)) (param src (ptr u8)) (param len uint)] void [
    (for i uint 0 len 1 [
        (= (^(incp dst i)) (^ (incp src i)))])
])


(fun polymorphic SysRender [(param v bool) 
                            (param buffer (slice mut u8)) 
                            (param options (ptr mut SysFormatOptions))] uint [
    (let s auto (? v (as "true" (slice u8)) (as "false" (slice u8))))                           
    (let n uint (? (< (len buffer) (len s)) (len buffer) (len s)))
    (copy_slice u8 buffer s n)
    (return n)
])


(fun polymorphic SysRender [(param v uint) 
                            (param out (slice mut u8)) 
                            (param options (ptr mut SysFormatOptions))] uint [
    (let mut tmp auto (ValArray u8 16 []))
    (let mut pos uint 16)
    (let mut val v)
    (block _ [
        (-= pos 1)
        (let c (% val 10))
        (let mut c8 (as c u8))
        (+= c8 '0')
        (= (at tmp pos) c8)
        (/= val 10)
        (if (!= val 0) [(continue)] [])
    ])
    (let len uint (min (- 16_uint pos) (len out)))
    (stmt (call memcpy [(as out (ptr mut u8)) (incp (as tmp (ptr u8)) pos) len]))
    (return len)
])


(macro print_common [(macro_param $curr ID) (macro_param $parts STMT_LIST)] [$buffer $options] [
    (macro_let mut $buffer auto (ValArray u8 1024))
    (macro_let mut $curr (slice mut u8) $buffer)
    (macro_let mut $options auto (rec SysFormatOptions []))
    (macro_for $i $parts [
        (incp= $curr (call polymorphic SysRender [$i $curr (& mut $options)]))
    ])
    (stmt (call SysPrint [$curr])) 
])
  
(macro pub print [(macro_param $parts STMT_LIST)] [$curr] [
    (print_common $curr [$parts])
    (stmt (call SysPrint [$curr])) 
])


(macro pub log [(macro_param $level EXPR) 
                (macro_param $parts STMT_LIST)] [$curr] [
    (if (call IsLogActive [$level (src_loc)]) [
        (print_common $curr [$parts])
        (stmt (call SysErrorPrint [$curr]))
    ] [])
])

(macro pub assert [(macro_param $cond EXPR) (macro_param $parts STMT_LIST)] [$curr] [
      (if $cond [] [
        (print_common $curr [$parts])
        (stmt (call SysErrorPrint [$curr]))
        (trap)
    ]) 
    
])


])