{{builtin}} module:

; macro for while-loop
pub {{builtin}} macro while STMT ($cond EXPR, $body STMT_LIST) []:
    block _:
        if !$cond:
            break
        $body
        continue

; macro for number range for-loop,
;
; The type of the loop variable is determined by $end
pub {{builtin}} macro for STMT_LIST ($index ID, $start EXPR, $end EXPR,
                                     $step EXPR, $body STMT_LIST)
  [$end_eval, $step_eval, $it]:
    let $end_eval type_of($end) = $end
    let $step_eval type_of($end) = $step
    let! $it type_of($end) = $start
    block _:
        if $step_eval >= 0:
            if $it >= $end_eval:
                break
        else:
            if $it <= $end_eval:
                break
        let $index = $it
        set $it = $it + $step_eval
        $body
        continue

pub {{builtin}} macro trylet STMT_LIST ($name ID, $type EXPR, $expr EXPR,
                                        $catch_name ID, $catch_body STMT_LIST)
  [$eval]:
    let $eval = $expr
    if !is($eval, $type):
        let $catch_name = narrow_as!($eval, union_delta(type_of($eval), $type))
        $catch_body
        trap
    let $name $type = narrow_as!($eval, $type)

pub {{builtin}} macro trylet! STMT_LIST ($name ID, $type EXPR, $expr EXPR,
                                         $catch_name ID, $catch_body STMT_LIST)
  [$eval]:
    let $eval = $expr
    if !is($eval, $type):
        let $catch_name = narrow_as!($eval, union_delta(type_of($eval), $type))
        $catch_body
        trap
    let! $name $type = narrow_as!($eval, $type)

pub {{builtin}} macro tryset STMT_LIST ($lhs EXPR, $expr EXPR, $catch_name ID,
                                        $catch_body STMT_LIST) [$eval]:
    let $eval = $expr
    if !is($eval, type_of($lhs)):
        let $catch_name = narrow_as!($eval,
                            union_delta(type_of($eval), type_of($lhs)))
        $catch_body
        trap
    set $lhs = narrow_as($eval, type_of($lhs))

macro swap# STMT_LIST ($a EXPR, $b EXPR) [$t]:
    let $t = $a
    set $a = $b
    set $b = $t

; works with arrays and slices. For arrays we make sure we do not copy them.
pub {{builtin}} macro span_inc EXPR ($slice EXPR, $size EXPR)
  [$orig_size, $orig_len, $orig_slice]:
    expr:
        let $orig_slice = $slice
        let $orig_len = len($orig_slice)
        let $orig_size uint = $size
        if $orig_size > $orig_len:
            trap
        return make_span(ptr_inc({{preserve_mut}} front($orig_slice), $orig_size
                           ), $orig_len - $orig_size)

pub {{builtin}} macro span_diff EXPR ($a EXPR, $b EXPR) []:
    ptr_diff(front($a), front($b))

; works with arrays and slices. For arrays we make sure we do not copy them.
pub macro span_truncate_or_die# EXPR ($slice EXPR, $size EXPR)
  [$orig_size, $orig_len, $orig_slice]:
    expr:
        let $orig_slice = as($slice, span!(type_of(front($slice)^)))
        let $orig_len = len($orig_slice)
        let $orig_size uint = $size
        if $orig_size > $orig_len:
            trap
        return make_span(front!($orig_slice), $orig_size)

; works with arrays and slices. For arrays we make sure we do not copy them.
pub macro span_append_or_die# EXPR ($slice EXPR, $out EXPR) [$e_slice, $e_out]:
    expr:
        let $e_slice span(type_of(front($slice)^)) = $slice
        let! $e_out span!(type_of(front($out)^)) = $out
        if len($e_slice) > len($e_out):
            trap
        for i = 0, len($e_slice), 1:
            set $e_out[i] = $e_slice[i]
        return len($e_slice)

pub {{extern}} {{cdecl}} fun print_ln(s ^u8, size uint) void:

; simple assert for those libs that cannot import fmt
pub macro assert# STMT ($cond EXPR, $text EXPR) [$e_cond, $e_text]:
    if !$cond:
        let $e_cond span(u8) = stringify($cond)
        let $e_text span(u8) = $text
        do print_ln(front($e_cond), len($e_cond))
        do print_ln(front($e_text), len($e_text))
        trap
