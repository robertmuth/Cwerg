@doc "test helpers"
(module test [] :

@doc "The two arguments must derivable types as we use `auto`"
(macro @pub AssertEq STMT_LIST [(mparam $e_expr EXPR) (mparam $a_expr EXPR)] [$e_val $a_val] :
    (macro_let $e_val auto $e_expr)
    (macro_let $a_val auto $a_expr)
    (if (!= $e_val $a_val) :
        (stmt (call SysPrint ["AssertEq failed: "]))
        (stmt (call SysPrint [(stringify $e_expr)]))
        (stmt (call SysPrint [" VS "]))
        (stmt (call SysPrint [(stringify $a_expr)]))
        (stmt (call SysPrint ["\n"]))
        (trap)
        :))


@doc "The two arguments must type derivable"
(macro @pub AssertSliceEq STMT_LIST [(mparam $e_expr EXPR) (mparam $a_expr EXPR)] [$e_val $a_val] :
    (macro_let $e_val auto $e_expr)
    (macro_let $a_val auto $a_expr)
    (AssertEq (len $e_val) (len $a_val))
    (for i 0 (len $a_val) 1 :
        (AssertEq (^ (incp (front $e_val) i)) (^ (incp (front $a_val) i)))))


@doc "The first two arguments must derivable types as we use `auto`"
(macro @pub AssertApproxEq STMT_LIST [
        (mparam $e_expr EXPR)
        (mparam $a_expr EXPR)
        (mparam $epsilon EXPR)] [$e_val $a_val] :
    (macro_let $e_val auto $e_expr)
    (macro_let $a_val auto $a_expr)
    (if (|| (< $e_val (- $a_val $epsilon)) (> $e_val (+ $a_val $epsilon))) :
        (stmt (call SysPrint ["AssertApproxEq failed: "]))
        (stmt (call SysPrint [(stringify $e_expr)]))
        (stmt (call SysPrint [" VS "]))
        (stmt (call SysPrint [(stringify $a_expr)]))
        (stmt (call SysPrint ["\n"]))
        (trap)
        :))


@doc "The first two arguments must type derivable"
(macro @pub AssertSliceApproxEq STMT_LIST [
        (mparam $e_expr EXPR)
        (mparam $a_expr EXPR)
        (mparam $epsilon EXPR)] [$e_val $a_val] :
    (macro_let $e_val auto $e_expr)
    (macro_let $a_val auto $a_expr)
    (AssertEq (len $e_val) (len $a_val))
    (for i 0 (len $a_val) 1 :
        (AssertApproxEq (^ (incp (front $e_val) i)) (^ (incp (front $a_val) i))))
    $epsilon)

@doc ""
(macro @pub AssertTrue STMT_LIST [(mparam $e_expr EXPR)] [$e_val $a_val] :
    (if  $e_expr : : 
        (stmt (call SysPrint ["AssertTrue failed: "]))
        (stmt (call SysPrint [(stringify $e_expr)]))
        (stmt (call SysPrint ["\n"]))
        (trap)
        ))

@doc ""
(macro @pub AssertFalse STMT_LIST [(mparam $e_expr EXPR)] [$e_val $a_val] :
    (if  $e_expr : 
        (stmt (call SysPrint ["AssertFalse failed: "]))
        (stmt (call SysPrint [(stringify $e_expr)]))
        (stmt (call SysPrint ["\n"]))
        (trap)
        : ))

)

