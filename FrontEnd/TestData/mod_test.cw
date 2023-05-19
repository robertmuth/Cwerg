(module test [] [

(# "The two arguments must type derivable")
(macro pub AssertEq [(macro_param $e_expr EXPR) 
                     (macro_param $a_expr EXPR)] [$e_val $a_val] [
    (macro_let $e_val auto $e_expr) 
    (macro_let $a_val auto $a_expr) 
    (if (!= $e_val $a_val) [
        (stmt (call SysPrint ["CheckEq failed: "]))
        (stmt (call SysPrint [(stringify $a_expr)]))
        (stmt (call SysPrint ["\n"]))
        (trap)
    ] []) 
])

])
