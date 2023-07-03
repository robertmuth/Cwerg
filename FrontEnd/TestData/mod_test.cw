(module test [] :
(# "The two arguments must derivable types as we use `auto`")
(macro pub AssertEq STMT_LIST [(mparam $e_expr EXPR) (mparam $a_expr EXPR)] [$e_val $a_val] :
    (macro_let $e_val auto (macro_id $e_expr))
    (macro_let $a_val auto (macro_id $a_expr))
    (if (!= (macro_id $e_val) (macro_id $a_val)) :
        (stmt (call SysPrint ["CheckEq failed: "]))
        (stmt (call SysPrint [(stringify (macro_id $a_expr))]))
        (stmt (call SysPrint ["\n"]))
        (trap)
        :))


(# "The two arguments must type derivable")
(macro pub AssertSliceEq STMT_LIST [(mparam $e_expr EXPR) (mparam $a_expr EXPR)] [$e_val $a_val] :
    (macro_let $e_val auto (macro_id $e_expr))
    (macro_let $a_val auto (macro_id $a_expr))
    (AssertEq (len (macro_id $e_val)) (len (macro_id $a_val)))
    (for i u64 0 (len (macro_id $a_val)) 1 [(AssertEq (^ (incp (front (macro_id $e_val)) i undef)) (^ (incp (front (macro_id $a_val)) i undef)))]))

)


