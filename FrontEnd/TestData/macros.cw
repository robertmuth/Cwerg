(defmod main [] [
(# "Macro Examples")

(# "macro for c-style -> operator")
(macro -> [(macro_param pointer EXPR) (macro_param field ID)] [
       (. (^ (macro_id pointer)) id)
])



(# "macro for number range for-loop")
(macro for [(macro_param index ID) 
            (macro_param start EXPR) 
            (macro_param end EXPR) 
            (macro_param step EXPR) 
            (macro_param body STMT_LIST)] [
    (macro_let it auto (macro_id start))
    (block _ [
          (if (>= it (macro_id end)) [(break)] [])
          (macro_let_indirect index auto it)
          (+= it (macro_id step))
          (macro_id body)
          (continue)
    ])
])

(# "macro for while-loop")
(macro while [(macro_param cond LAZY_EXPR) 
              (macro_param body STMT_LIST)] [
    (block _ [
          (if (macro_id cond) [] [(break)])
          (macro_id body)
          (continue)
    ])
])        

(macro try [(macro_param name ID) 
            (macro_param type EXPR) 
            (macro_param expr EXPR) 
            (macro_param catch_name ID) 
            (macro_param catch_body STMT_LIST)] [
    (if (is (macro_id expr) (macro_id type)) [] [
        (macro_let_indirect catch_name auto (asnot (macro_id expr) (macro_id type)))
        (macro_id catch_body)
        (trap)
    ]) 
    (macro_let_indirect name (tryas (macro_id expr) (macro_id type) undef))
])

(defun pub extern IsLogActive [(param level u8) (param loc u32)] void [])

(defun pub extern print [(param buffer (slice u8))] void [])

(macro log [(macro_param level EXPR) 
            (macro_param repeat x LAZY_EXPR)] [
    (if (call IsLogActive [level (src_loc)]) [
        (macro_let mut buffer auto (ValArray u8 1024 [(IndexVal undef)]))
        (# "TODO complete this")
    ] [])
])


])