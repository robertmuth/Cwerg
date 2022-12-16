(module $builtin [] [
(# "Macro Examples")


(# "This gets passed to the actual formatters which decide how to interpret the options.")
(defrec SysFormatOptions [
    (# "min width")
    (field witdh u8 0)
    (field precission u8 0)
    (field padding u8 0)
    (field style u8 0)
    (field show_sign bool false)
    (field left_justify bool false)
])



(fun pub extern SysErrorPrint [(param buffer (slice u8))] void [])


(# "macro for c-style -> operator")
(macro -> [(macro_param $pointer EXPR) (macro_param $field FIELD)] [
       (. (^ $pointer) $field)
])


(# "macro for number range for-loop")
(macro for [(macro_param $index ID) 
            (macro_param $type TYPE) 
            (macro_param $start EXPR) 
            (macro_param $end EXPR) 
            (macro_param $step EXPR) 
            (macro_param $body STMT_LIST)] [
    
    (macro_gen_id $end_eval)
    (macro_let $end_eval $type $end)
    (macro_gen_id $step_eval)
    (macro_let $step_eval $type $step)
    (macro_gen_id $it)
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
(macro while [(macro_param $cond EXPR) 
              (macro_param $body STMT_LIST)] [
    (block _ [
          (if $cond [] [(break)])
          $body
          (continue)
    ])
])        


(macro assert [(macro_param $cond EXPR)] [
      (if $cond [] [
        (macro_gen_id $buffer)
        (macro_let mut $buffer auto (ValArray u8 1024 [(IndexVal undef)]))
        (macro_gen_id $curr)
        (macro_let mut $curr (slice mut u8) $buffer)
        (stmt (call SysErrorPrint [$curr]))
        (trap)
    ]) 
    
])


(macro try [(macro_param $name ID) 
            (macro_param $type EXPR) 
            (macro_param $expr EXPR) 
            (macro_param $catch_name ID) 
            (macro_param $catch_body STMT_LIST)] [
    (if (is $expr $type) [] [
        (macro_let $catch_name auto (asnot $expr $type))
        (macro_id $catch_body)
        (trap)
    ]) 
    (macro_let $name (tryas $expr $type undef))
])


(fun pub extern IsLogActive [(param level u8) (param loc u32)] void [])


(fun pub extern print [(param buffer (slice u8))] void [])


(macro log [(macro_param $level EXPR) 
            (macro_param $parts STMT_LIST)] [
    (if (call IsLogActive [$level (src_loc)]) [
        (macro_gen_id $buffer)
        (macro_let mut $buffer auto (ValArray u8 1024 [(IndexVal undef)]))
        (macro_gen_id $curr)
        (macro_let mut $curr (slice mut u8) $buffer)
        (# "TODO complete this")
        (macro_for $i $parts [
            (= $curr (call SysStringfy [$i $curr]))
        ])
        (stmt (call SysErrorPrint [$curr]))
    ] [])
])



(# "generic copy of data from slice/array to slice")
(macro copy_slice [(macro_param $item_type TYPE) 
                   (macro_param $src EXPR)
                   (macro_param $dst EXPR)
                   (macro_param $len EXPR)] [
    (macro_gen_id $psrc)   
    (macro_let $psrc auto (as $src (ptr $item_type))) 
    (macro_gen_id $pdst)   
    (macro_let $pdst auto (as $dst (ptr mut $item_type)))
    (macro_gen_id $n)              
    (macro_let $n uint $len)
    (macro_gen_id $i)              
    (for $i uint 0 $n 1 [
        (= (^(+ $pdst $i)) (^ (+ $psrc $i)))])
])


(fun polymorphic SysRender [(param v bool) 
                            (param buffer (slice mut u8)) 
                            (param options (ptr mut SysFormatOptions))] uint [
    (let s auto (? v (as "true" (slice u8)) (as "false" (slice u8))))                           
    (let n uint (? (< (len buffer) (len s)) (len buffer) (len s)))
    (copy_slice u8 buffer s n)
    (return n)
])

])