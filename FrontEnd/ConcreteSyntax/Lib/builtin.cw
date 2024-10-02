@builtin module:

-- macro for while-loop
pub macro while STMT($cond EXPR, $body STMT_LIST)[]:
    block _:
        if $cond:
        else:
            break
        $body 

        continue

-- macro for number range for-loop,
-- 
-- The type of the loop variable is determined by $end
pub macro for STMT_LIST($index ID, $start EXPR, $end EXPR, $step EXPR, $body STMT_LIST)[
        $end_eval, $step_eval, $it]:
    mlet $end_eval type_of($end) = $end
    mlet $step_eval type_of($end) = $step
    mlet! $it type_of($end) = $start
    block _:
        if $step_eval >= 0:
            if $it >= $end_eval:
                break
        else:
            if $it <= $end_eval:
                break
        mlet $index = $it
        set $it = $it + $step_eval
        $body 

        continue

pub macro trylet STMT_LIST(
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

pub macro trylet! STMT_LIST(
        $name ID, $type EXPR, $expr EXPR, $catch_name ID, $catch_body STMT_LIST)[
        $eval]:
    mlet $eval = $expr
    if !is($eval, $type):
        mlet $catch_name = @unchecked narrow_as(
                $eval, union_delta(type_of($eval), $type))
        $catch_body 

        trap
    mlet! $name $type = @unchecked narrow_as($eval, $type)

pub macro tryset STMT_LIST(
        $lhs EXPR, $expr EXPR, $catch_name ID, $catch_body STMT_LIST)[$eval]:
    mlet $eval = $expr
    if !is($eval, type_of($lhs)):
        mlet $catch_name = @unchecked narrow_as(
                $eval, union_delta(type_of($eval), type_of($lhs)))
        $catch_body 

        trap
    set $lhs = narrow_as($eval, type_of($lhs))

macro swap# STMT_LIST($a EXPR, $b EXPR)[$t]:
    mlet $t = $a
    set $a = $b
    set $b = $t

-- works with arrays and slices. For arrays we make sure we do not copy them.
pub macro span_inc_or_die# EXPR($slice EXPR, $size EXPR)[
        $orig_size, $orig_len, $orig_slice]:
    expr:
        mlet $orig_slice = as($slice, span!(type_of(front($slice)^)))
        mlet $orig_len = len($orig_slice)
        mlet $orig_size uint = $size
        if $orig_size > $orig_len:
            trap
        return span(pinc(front!($orig_slice), $orig_size), $orig_len - $orig_size)


-- works with arrays and slices. For arrays we make sure we do not copy them.
pub macro span_truncate_or_die# EXPR($slice EXPR, $size EXPR)[
        $orig_size, $orig_len, $orig_slice]:
    expr:
        mlet $orig_slice = as($slice, span!(type_of(front($slice)^)))
        mlet $orig_len = len($orig_slice)
        mlet $orig_size uint = $size
        if $orig_size > $orig_len:
            trap
        return span(front!($orig_slice), $orig_size)


-- works with arrays and slices. For arrays we make sure we do not copy them.
pub macro span_append_or_die# EXPR($slice EXPR, $out EXPR)[$e_slice, $e_out]:
    expr:
        mlet $e_slice = as($slice, span(type_of(front($slice)^)))
        mlet $e_out = as($out, span!(type_of(front($out)^)))
        if len($e_slice) > len($e_out):
            trap
        for i = 0, len($e_slice), 1:
            set $e_out[i] = $e_slice[i]
        return len($e_slice)


-- macro for c-style -> operator
pub macro ^. EXPR($pointer EXPR, $field FIELD)[]:
    ($pointer^).$field 

pub @extern @cdecl fun print_ln(s ^u8, size uint) void:

-- simple assert for those libs that cannot import fmt
pub macro assert# STMT($cond EXPR, $text EXPR)[$e_cond, $e_text]:
    if $cond:
    else:
        mlet $e_cond span(u8) = stringify($cond)
        mlet $e_text span(u8) = $text
        do print_ln(front($e_cond), len($e_cond))
        do print_ln(front($e_text), len($e_text))
        trap
