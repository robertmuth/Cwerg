@doc """test helpers macros

This intentionally does not import the fmt module to keep
the footprint/dependencies small.
(We may change our mind on this.)
"""
(module test [] :
(import os)



(macro SysPrint! STMT_LIST [(mparam $msg EXPR)] [$msg_eval] :
    ($let $msg_eval (slice u8) $msg)
    (shed (os::write [(unwrap os::Stdout) (front $msg_eval) (len $msg_eval)])
    ))

(macro @pub Success! STMT [] [] :
    (SysPrint! "OK\n"))


@doc """The two scalar arguments must be the same

Both must have derivable types as we use `auto`"""
(macro @pub AssertEq! STMT_LIST [(mparam $e_expr EXPR) (mparam $a_expr EXPR)] [$e_val $a_val] :
    ($let $e_val auto $e_expr)
    ($let $a_val auto $a_expr)
    (if (!= $e_val $a_val) :
        (SysPrint! "AssertEq failed: ")
        (SysPrint! (stringify $e_expr))
        (SysPrint! " VS ")
        (SysPrint! (stringify $a_expr))
        (SysPrint! "\n")
        (trap)
        :))

@doc "First argument must have the type denoted by the second"
(macro @pub AssertIs! STMT_LIST [(mparam $expr EXPR) (mparam $type TYPE)] [] :
    (if (is $expr $type) : :
        (SysPrint! "AssertIs failed: ")
        (SysPrint! (stringify (typeof $expr)))
        (SysPrint! " VS ")
        (SysPrint! (stringify $type))
        (SysPrint! "\n")
        (trap)
        ))

@doc "The two arguments must type derivable"
(macro @pub AssertSliceEq! STMT_LIST [(mparam $e_expr EXPR) (mparam $a_expr EXPR)]
        [$e_val $a_val $i] :
    ($let $e_val auto $e_expr)
    ($let $a_val auto $a_expr)
    (AssertEq! (len $e_val) (len $a_val))
    (for $i 0 (len $a_val) 1 :
        (AssertEq! (^ (&+ (front $e_val) $i)) (^ (&+ (front $a_val) $i)))))


@doc "The first two arguments must derivable types as we use `auto`"
(macro @pub AssertApproxEq! STMT_LIST [
        (mparam $e_expr EXPR)
        (mparam $a_expr EXPR)
        (mparam $epsilon EXPR)] [$e_val $a_val] :
    ($let $e_val auto $e_expr)
    ($let $a_val auto $a_expr)
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
        (mparam $epsilon EXPR)] [$e_val $a_val $i] :
    ($let $e_val auto $e_expr)
    ($let $a_val auto $a_expr)
    (AssertEq! (len $e_val) (len $a_val))
    (for $i 0 (len $a_val) 1 :
        (AssertApproxEq! (^ (&+ (front $e_val) $i)) (^ (&+ (front $a_val) $i))))
    $epsilon)

@doc ""
(macro @pub AssertTrue! STMT_LIST [(mparam $e_expr EXPR)] [] :
    (if  $e_expr : :
        (SysPrint! "AssertTrue failed: ")
        (SysPrint! (stringify $e_expr))
        (SysPrint! "\n")
        (trap)
        ))

@doc ""
(macro @pub AssertFalse! STMT_LIST [(mparam $e_expr EXPR)] [] :
    (if  $e_expr :
        (SysPrint! "AssertFalse failed: ")
        (SysPrint! (stringify $e_expr))
        (SysPrint! "\n")
        (trap)
        : ))

@doc ""
(macro @pub AssertUnreachable! STMT_LIST [] [] :
    (SysPrint! "AssertUnreachable\n")
    (trap)
)

)
