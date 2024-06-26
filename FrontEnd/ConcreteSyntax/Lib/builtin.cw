@builtin module:

-- macro for while-loop
@pub macro while STMT($cond EXPR, $body STMT_LIST)[]:
    block _:
        if $cond:
        else:
            break
        $body 

        continue

-- macro for number range for-loop,
-- 
-- The type of the loop variable is determined by $end
@pub macro for STMT_LIST($index ID, $start EXPR, $end EXPR, $step EXPR, $body STMT_LIST)[
        $end_eval, $step_eval, $it]:
    mlet $end_eval typeof($end) = $end
    mlet $step_eval typeof($end) = $step
    mlet! $it typeof($end) = $start
    block _:
        if $it >= $end_eval:
            break
        mlet $index = $it
        set $it = $it + $step_eval
        $body 

        continue

@pub macro trylet STMT_LIST(
        $name ID, $type EXPR, $expr EXPR, $catch_name ID, $catch_body STMT_LIST)[
        $eval]:
    mlet $eval = $expr
    if is($eval, $type):
    else:
        mlet $catch_name = @unchecked narrowto(
                $eval, uniondelta(typeof($eval), $type))
        $catch_body 

        trap
    mlet $name $type = @unchecked narrowto($eval, $type)

@pub macro trylet! STMT_LIST(
        $name ID, $type EXPR, $expr EXPR, $catch_name ID, $catch_body STMT_LIST)[
        $eval]:
    mlet $eval = $expr
    if !is($eval, $type):
        mlet $catch_name = @unchecked narrowto(
                $eval, uniondelta(typeof($eval), $type))
        $catch_body 

        trap
    mlet! $name $type = @unchecked narrowto($eval, $type)

@pub macro tryset STMT_LIST(
        $name ID, $expr EXPR, $catch_name ID, $catch_body STMT_LIST)[$eval]:
    mlet $eval = $expr
    if !is($eval, typeof($name)):
        mlet $catch_name = @unchecked narrowto(
                $eval, uniondelta(typeof($eval), typeof($type)))
        $catch_body 

        trap
    mlet $name $type = narrowto($eval, $type)

macro swap# STMT_LIST($a EXPR, $b EXPR)[$t]:
    mlet $t = $a
    set $a = $b
    set $b = $t

-- macro for c-style -> operator
@pub macro ^. EXPR($pointer EXPR, $field FIELD)[]:
    ($pointer^).$field 
