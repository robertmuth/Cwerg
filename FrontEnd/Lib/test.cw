@doc "test helpers"
(module test [] :
(import os)



(macro SysPrint! STMT_LIST [(mparam $msg EXPR)] [$msg_eval] :
    (macro_let $msg_eval (slice u8) $msg)
    (stmt (call os::write [(as os::Stdout s32) (front $msg_eval) (len $msg_eval)])
    ))

(macro @pub Success! STMT [] [] :
    (SysPrint! "OK"))


@doc "The two arguments must derivable types as we use `auto`"
(macro @pub AssertEq! STMT_LIST [(mparam $e_expr EXPR) (mparam $a_expr EXPR)] [$e_val $a_val] :
    (macro_let $e_val auto $e_expr)
    (macro_let $a_val auto $a_expr)
    (if (!= $e_val $a_val) :
        (SysPrint! "AssertEq failed: ")
        (SysPrint! (stringify $e_expr))
        (SysPrint! " VS ")
        (SysPrint! (stringify $a_expr))
        (SysPrint! "\n")
        (trap)
        :))


@doc "The two arguments must type derivable"
(macro @pub AssertSliceEq! STMT_LIST [(mparam $e_expr EXPR) (mparam $a_expr EXPR)] [$e_val $a_val] :
    (macro_let $e_val auto $e_expr)
    (macro_let $a_val auto $a_expr)
    (AssertEq! (len $e_val) (len $a_val))
    (for i 0 (len $a_val) 1 :
        (AssertEq! (^ (incp (front $e_val) i)) (^ (incp (front $a_val) i)))))


@doc "The first two arguments must derivable types as we use `auto`"
(macro @pub AssertApproxEq! STMT_LIST [
        (mparam $e_expr EXPR)
        (mparam $a_expr EXPR)
        (mparam $epsilon EXPR)] [$e_val $a_val] :
    (macro_let $e_val auto $e_expr)
    (macro_let $a_val auto $a_expr)
    (if (|| (< $e_val (- $a_val $epsilon)) (> $e_val (+ $a_val $epsilon))) :
        (SysPrint! "AssertApproxEq failed: ")
        (SysPrint! (stringify $e_expr))
        (SysPrint! " VS ")
        (SysPrint! (stringify $a_expr))
        (SysPrint! "\n")
        (trap)
        :))


@doc "The first two arguments must type derivable"
(macro @pub AssertSliceApproxEq! STMT_LIST [
        (mparam $e_expr EXPR)
        (mparam $a_expr EXPR)
        (mparam $epsilon EXPR)] [$e_val $a_val] :
    (macro_let $e_val auto $e_expr)
    (macro_let $a_val auto $a_expr)
    (AssertEq! (len $e_val) (len $a_val))
    (for i 0 (len $a_val) 1 :
        (AssertApproxEq! (^ (incp (front $e_val) i)) (^ (incp (front $a_val) i))))
    $epsilon)

@doc ""
(macro @pub AssertTrue! STMT_LIST [(mparam $e_expr EXPR)] [$e_val $a_val] :
    (if  $e_expr : :
        (SysPrint! "AssertTrue failed: ")
        (SysPrint! (stringify $e_expr))
        (SysPrint! "\n")
        (trap)
        ))

@doc ""
(macro @pub AssertFalse! STMT_LIST [(mparam $e_expr EXPR)] [$e_val $a_val] :
    (if  $e_expr :
        (SysPrint! "AssertFalse failed: ")
        (SysPrint! (stringify $e_expr))
        (SysPrint! "\n")
        (trap)
        : ))

)
