@builtin (module [] :

@doc "macro for while-loop"
@pub (macro while STMT [(mparam $cond EXPR) (mparam $body STMT_LIST)] [] :
    (block _ :
        (if $cond :
         :
            (break))
        $body
        (continue)))


@doc """macro for number range for-loop,

The type of the loop variable is determined by $end"""
@pub (macro for STMT_LIST [
        (mparam $index ID)
        (mparam $start EXPR)
        (mparam $end EXPR)
        (mparam $step EXPR)
        (mparam $body STMT_LIST)] [$end_eval $step_eval $it] :
    (mlet $end_eval (type_of $end) $end)
    (mlet $step_eval (type_of $end) $step)
    (mlet! $it (type_of $end) $start)
    (block _ :
        (if (>= $it $end_eval) :
            (break)
         :)
        (mlet $index auto $it)
        (= $it (+ $it $step_eval))
        $body
        (continue)))


@pub (macro trylet STMT_LIST [
        (mparam $name ID)
        (mparam $type EXPR)
        (mparam $expr EXPR)
        (mparam $catch_name ID)
        (mparam $catch_body STMT_LIST)] [$eval] :
    (mlet $eval auto $expr)
    (if (is $eval $type) :
     :
        (mlet $catch_name auto (@unchecked narrow_as $eval (union_delta (type_of $eval) $type)))
        $catch_body
        (trap))
    (mlet $name $type (@unchecked narrow_as $eval $type)))


@pub (macro trylet! STMT_LIST [
        (mparam $name ID)
        (mparam $type EXPR)
        (mparam $expr EXPR)
        (mparam $catch_name ID)
        (mparam $catch_body STMT_LIST)] [$eval] :
    (mlet $eval auto $expr)
    (if (! (is $eval $type)) :
        (mlet $catch_name auto (@unchecked narrow_as $eval (union_delta (type_of $eval) $type)))
        $catch_body
        (trap)
    :)
    (mlet! $name $type (@unchecked narrow_as $eval $type)))

@pub (macro tryset STMT_LIST [
        (mparam $lhs EXPR)
        (mparam $expr EXPR)
        (mparam $catch_name ID)
        (mparam $catch_body STMT_LIST)] [$eval] :
    (mlet $eval auto $expr)
    (if (! (is $eval (type_of $lhs))) :
        (mlet $catch_name auto (@unchecked narrow_as $eval (union_delta (type_of $eval) (type_of $lhs))))
        $catch_body
        (trap)
    :)
    (= $lhs (narrow_as $eval (type_of $lhs))))

(macro swap# STMT_LIST [(mparam $a EXPR) (mparam $b EXPR)] [$t] :
    (mlet $t auto $a)
    (= $a $b)
    (= $b $t))


@doc "macro for c-style -> operator"
@pub (macro ^. EXPR [(mparam $pointer EXPR) (mparam $field FIELD)] [] :
    (. (paren (^ $pointer)) $field))
)
