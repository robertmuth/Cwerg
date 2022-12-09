(defmod main [] [
(# "Macro Examples")

(# "macro for c-style -> operator")
(macro -> [(macro_param $pointer LAZY_EXPR) (macro_param $field FIELD)] [
       (. (^ $pointer) $field)
])



(# "macro for number range for-loop")
(macro forM [(macro_param $index ID) 
            (macro_param $start EXPR) 
            (macro_param $end EXPR) 
            (macro_param $step EXPR) 
            (macro_param $body STMT_LIST)] [
    (macro_let $it auto $start)
    (block _ [
          (if (>= $it $end) [(break)] [])
          (macro_let_indirect $index auto $it)
          (+=  $it $step)
          $body
          (continue)
    ])
])

(# "macro for while-loop")
(macro whileM [(macro_param $cond LAZY_EXPR) 
              (macro_param $body STMT_LIST)] [
    (block _ [
          (if $cond [] [(break)])
          $body
          (continue)
    ])
])        

(macro try [(macro_param $name ID) 
            (macro_param $type EXPR) 
            (macro_param $expr EXPR) 
            (macro_param $catch_name ID) 
            (macro_param $catch_body STMT_LIST)] [
    (if (is $expr $type) [] [
        (macro_let_indirect $catch_name auto (asnot $expr $type))
        (macro_id catch_body)
        (trap)
    ]) 
    (macro_let_indirect $name (tryas $expr $type undef))
])

(defun pub extern IsLogActive [(param level u8) (param loc u32)] void [])

(defun pub extern print [(param buffer (slice u8))] void [])

(macro log [(macro_param $level EXPR) 
            (macro_param repeat $x LAZY_EXPR)] [
    (if (call IsLogActive [$level (src_loc)]) [
        (macro_let mut $buffer auto (ValArray u8 1024 [(IndexVal undef)]))
        (# "TODO complete this")
    ] [])
])


(defrec pub MyRec [
    (field s1 s32 undef)
    (field s2 u32 undef)
])


(defun TestRightArrowMacro [(param pointer (ptr MyRec))] u32 [
    (return (-> pointer s2))
])
  
(defun TestWhileMacro [(param end u32)] u32 [
    (let mut sum u32 0)
    (whileM (< sum end) [
        (+= sum i)
    ])
    (return sum)
])


(defun TestForMacro [(param end u32)] u32 [
    (let mut sum u32 0)
    (forM i 0_u32 end 1 [
        (+= sum i)
    ])
    (return sum)
])




])