@doc """Macro Examples
This gets passed to the actual formatters which decide how to interpret the options."""
(module $builtin [] :

(defrec @pub SysFormatOptions :
    @doc "min width"
    (field witdh u8)
    (field precission u8)
    (field padding u8)
    (field style u8)
    (field show_sign bool)
    (field left_justify bool))


(fun @pub @extern SysErrorPrint [(param buffer (slice u8))] void :)


(fun @pub @extern SysPrint [(param buffer (slice u8))] void :)

@doc "macro for c-style -> operator"
(macro @pub -> EXPR [(mparam $pointer EXPR) (mparam $field FIELD)] [] :
    (. (^ $pointer) $field))


@doc "macro for number range for-loop"
(macro @pub for STMT_LIST [
        (mparam $index ID)
        (mparam $type TYPE)
        (mparam $start EXPR)
        (mparam $end EXPR)
        (mparam $step EXPR)
        (mparam $body STMT_LIST)] [$end_eval $step_eval $it] :
    (macro_let $end_eval $type $end)
    (macro_let $step_eval $type $step)
    (macro_let @mut $it $type $start)
    (block _ :
        (if (>= $it $end_eval) :
            (break)
            :)
        (macro_let $index auto $it)
        (= $it (+ $it $step_eval))
        $body
        (continue)))


@doc "macro for while-loop"
(macro @pub while STMT [(mparam $cond EXPR) (mparam $body STMT_LIST)] [] :
    (block _ :
        (if $cond :
            :
            (break))
        $body
        (continue)))


(macro @pub try STMT_LIST [
        (mparam $name ID)
        (mparam $type EXPR)
        (mparam $expr EXPR)
        (mparam $catch_name ID)
        (mparam $catch_body STMT_LIST)] [$eval] :
    (macro_let $eval auto $expr)
    (if (is $eval $type) :
        :
        (macro_let $catch_name auto (asnot $eval $type))
        $catch_body
        (trap))
    (macro_let $name $type (sumas $eval $type)))


(fun @pub @extern IsLogActive [(param level u8) (param loc u32)] void :)


@doc "generic copy of data from slice/array to slice"
(macro copy_slice STMT_LIST [
        (mparam $item_type TYPE)
        (mparam $src EXPR)
        (mparam $dst EXPR)
        (mparam $len EXPR)] [$psrc $pdst $n $i] :
    (macro_let $psrc auto (as $src (ptr $item_type)))
    (macro_let $pdst auto (as $dst (ptr @mut $item_type)))
    (macro_let $n uint (min $len (len $dst)))
    (for $i uint 0 $n 1 [(= (^ (incp $pdst $i)) (^ (incp $psrc $i)))]))


(fun @pub memcpy [
        (param dst (ptr @mut u8))
        (param src (ptr u8))
        (param size uint)] uint :
    (for i uint 0 size 1 :
        (= (^ (incp dst i)) (^ (incp src i))))
    (return size))


(fun @polymorphic SysRender [
        (param v bool)
        (param buffer (slice @mut u8))
        (param options (ptr @mut SysFormatOptions))] uint :
    (let s auto (? v (as "true" (slice u8)) (as "false" (slice u8))))
    (let n uint (min (len buffer) (len s)))
    (return (call memcpy [
            (as buffer (ptr @mut u8))
            (as s (ptr u8))
            n])))


(macro unsigned_to_str STMT_LIST [
        (mparam $val EXPR)
        (mparam $base EXPR)
        (mparam $max_width EXPR)
        (mparam $out ID)] [$v $tmp $pos] :
    @doc "unsigned to str with give base"
    (macro_let @mut $v auto $val)
    (macro_let @mut $tmp auto (array_val $max_width u8))
    (macro_let @mut $pos uint $max_width)
    (block _ :
        (-= $pos 1)
        (let c auto (% $v $base))
        (let @mut c8 auto (as c u8))
        (+= c8 (? (<= c8 9) '0' (- 'a' 10)))
        (= (at $tmp $pos) c8)
        (/= $v $base)
        (if (!= $v 0) :
            (continue)
            :))
    (let n uint (min (- $max_width $pos) (len $out)))
    (return (call memcpy [
            (as $out (ptr @mut u8))
            (incp (as $tmp (ptr u8)) $pos)
            n])))


(fun @polymorphic SysRender [
        (param v u8)
        (param out (slice @mut u8))
        (param options (ptr @mut SysFormatOptions))] uint :
    (unsigned_to_str v 10 32_uint out))


(fun @polymorphic SysRender [
        (param v u16)
        (param out (slice @mut u8))
        (param options (ptr @mut SysFormatOptions))] uint :
    (unsigned_to_str v 10 32_uint out))


(fun @polymorphic SysRender [
        (param v u32)
        (param out (slice @mut u8))
        (param options (ptr @mut SysFormatOptions))] uint :
    (unsigned_to_str v 10 32_uint out))


(fun @polymorphic SysRender [
        (param v u64)
        (param out (slice @mut u8))
        (param options (ptr @mut SysFormatOptions))] uint :
    (unsigned_to_str v 10 32_uint out))


(fun @polymorphic SysRender [
        (param v (slice u8))
        (param buffer (slice @mut u8))
        (param options (ptr @mut SysFormatOptions))] uint :
    (let n uint (min (len buffer) (len v)))
    (return (call memcpy [
            (as buffer (ptr @mut u8))
            (as v (ptr u8))
            n])))


(macro print_common STMT_LIST [(mparam $curr ID) (mparam $parts STMT_LIST)] [$buffer $options $buffer_orig] :
    (macro_let @mut $buffer auto (array_val 1024 u8))
    (macro_let @mut $curr (slice @mut u8) $buffer)
    (macro_let @mut @ref $options auto (rec_val SysFormatOptions []))
    (macro_for $i $parts :
        (= $curr (incp $curr (call @polymorphic SysRender [
                $i
                $curr
                (& @mut $options)]))))
    (macro_let $buffer_orig (slice u8) $buffer)
    (stmt (call SysPrint [(pdelta $buffer_orig $curr)])))


(macro @pub print STMT_LIST [(mparam $parts STMT_LIST)] [$curr] :
    (print_common $curr [$parts])
    (stmt (call SysPrint [$curr])))


(macro swap STMT_LIST [(mparam $a EXPR) (mparam $b EXPR)] [$t] :
    (macro_let $t auto $a)
    (= $a $b)
    (= $b $t))


(macro @pub log STMT [(mparam $level EXPR) (mparam $parts STMT_LIST)] [$curr] :
    (if (call IsLogActive [$level (src_loc)]) :
        (print_common $curr [$parts])
        (stmt (call SysErrorPrint [$curr]))
        :))


(macro @pub assert STMT [(mparam $cond EXPR) (mparam $parts STMT_LIST)] [$curr] :
    (if $cond :
        :
        (print_common $curr [$parts])
        (stmt (call SysErrorPrint [$curr]))
        (trap)))

)


