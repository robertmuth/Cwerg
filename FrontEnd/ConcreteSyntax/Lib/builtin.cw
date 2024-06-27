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
    mlet $end_eval type_of($end) = $end
    mlet $step_eval type_of($end) = $step
    mlet! $it type_of($end) = $start
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
        mlet $catch_name = @unchecked narrow_as(
                $eval, union_delta(type_of($eval), $type))
        $catch_body 

        trap
    mlet $name $type = @unchecked narrow_as($eval, $type)

@pub macro trylet! STMT_LIST(
        $name ID, $type EXPR, $expr EXPR, $catch_name ID, $catch_body STMT_LIST)[
        $eval]:
    mlet $eval = $expr
    if !is($eval, $type):
        mlet $catch_name = @unchecked narrow_as(
                $eval, union_delta(type_of($eval), $type))
        $catch_body 

        trap
    mlet! $name $type = @unchecked narrow_as($eval, $type)

@pub macro tryset STMT_LIST(
        $name ID, $expr EXPR, $catch_name ID, $catch_body STMT_LIST)[$eval]:
    mlet $eval = $expr
    if !is($eval, type_of($name)):
        mlet $catch_name = @unchecked narrow_as(
                $eval, union_delta(type_of($eval), type_of($type)))
        $catch_body 

        trap
    mlet $name $type = narrow_as($eval, $type)

macro swap# STMT_LIST($a EXPR, $b EXPR)[$t]:
    mlet $t = $a
    set $a = $b
    set $b = $t

-- macro for c-style -> operator
@pub macro ^. EXPR($pointer EXPR, $field FIELD)[]:
    ($pointer^).$field 
