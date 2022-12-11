(module $builtin [] [
(# "Macro Examples")


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
    
    (macro_let $end_eval $type $end)
    (macro_let $step_eval $type $step)
    (macro_let mut $it $type $start)
    (block _ [
          (if (>= $it $end_eval) [(break)] [])
          (macro_let_indirect $index auto $it)
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
        (macro_let mut $buffer auto (ValArray u8 1024 [(IndexVal undef)]))
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
        (macro_let_indirect $catch_name auto (asnot $expr $type))
        (macro_id $catch_body)
        (trap)
    ]) 
    (macro_let_indirect $name (tryas $expr $type undef))
])


(fun pub extern IsLogActive [(param level u8) (param loc u32)] void [])


(fun pub extern print [(param buffer (slice u8))] void [])


(macro log [(macro_param $level EXPR) 
            (macro_param repeat $x EXPR)] [
    (if (call IsLogActive [$level (src_loc)]) [
        (macro_let mut $buffer auto (ValArray u8 1024 [(IndexVal undef)]))
        (# "TODO complete this")
    ] [])
])

])