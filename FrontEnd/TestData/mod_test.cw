(module test [] :
(# "The two arguments must derivable types as we use `auto`")
(macro pub AssertEq STMT_LIST [(mparam $e_expr EXPR) (mparam $a_expr EXPR)] [$e_val $a_val] :
    (macro_let $e_val auto $e_expr)
    (macro_let $a_val auto $a_expr)
    (if (!= $e_val $a_val) :
        (stmt (call SysPrint ["CheckEq failed: "]))
        (stmt (call SysPrint [(stringify $a_expr)]))
        (stmt (call SysPrint ["\n"]))
        (trap)
        :))


(# "The two arguments must type derivable")
(macro pub AssertSliceEq STMT_LIST [(mparam $e_expr EXPR) (mparam $a_expr EXPR)] [$e_val $a_val] :
    (macro_let $e_val auto $e_expr)
    (macro_let $a_val auto $a_expr)
    (AssertEq (len $e_val) (len $a_val))
    (for i u64 0 (len $a_val) 1 :
        (AssertEq (^ (incp (front $e_val) i undef)) (^ (incp (front $a_val) i undef)))))


(# "eom"))
