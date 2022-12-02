(defmod main [] [
(# "Macro Examples")

(# "macro for c-style -> operator")
(macro -> [(macro_param pointer EXPR) (macro_param field ID)] [
       (. (^ (macro_node pointer)) id)
])

(# "macro for number range for-loop")
(macro for [(macro_param index ID) 
            (macro_param start EXPR) 
            (macro_param end EXPR) 
            (macro_param step EXPR) 
            (macro_param body STMT_LIST)] [
    (macro_let it (macro_node start))
    (block _ [
          (if (>= it (macro_node end)) [(break)] [])
          (let index it)
          (+= it (macro_node step))
          (macro_node body)
          (continue)
    ])
])

(# "macro for while-loop")
(macro while [(macro_param cond LAZY_EXPR) 
              (macro_param body STMT_LIST)] [
    (block _ [
          (if (macro_node cond) [] [(break)])
          (macro_node body)
          (continue)
    ])
])        

])