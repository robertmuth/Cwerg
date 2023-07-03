(module $builtin [] :
(# "Macro Examples")
(# "This gets passed to the actual formatters which decide how to interpret the options.")
(defrec pub SysFormatOptions :
    (# "min width")
    (field witdh u8)
    (field precission u8)
    (field padding u8)
    (field style u8)
    (field show_sign bool)
    (field left_justify bool))


(fun pub extern SysErrorPrint [(param buffer (slice u8))] void :)


(fun pub extern SysPrint [(param buffer (slice u8))] void :)


(# "macro for c-style -> operator")
(macro pub -> EXPR [(mparam $pointer EXPR) (mparam $field FIELD)] [] :
    (. (^ (macro_id $pointer)) $field))


(# "macro for number range for-loop")
(macro pub for STMT_LIST [
        (mparam $index ID)
        (mparam $type TYPE)
        (mparam $start EXPR)
        (mparam $end EXPR)
        (mparam $step EXPR)
        (mparam $body STMT_LIST)] [$end_eval $step_eval $it] :
    (macro_let $end_eval (macro_id $type) (macro_id $end))
    (macro_let $step_eval (macro_id $type) (macro_id $step))
    (macro_let mut $it (macro_id $type) (macro_id $start))
    (block _ :
        (if (>= (macro_id $it) (macro_id $end_eval)) :
            break
            :)
        (macro_let $index auto (macro_id $it))
        (= (macro_id $it) (+ (macro_id $it) (macro_id $step_eval)))
        (macro_id $body)
        continue))


(# "macro for while-loop")
(macro pub while STMT [(mparam $cond EXPR) (mparam $body STMT_LIST)] [] :
    (block _ :
        (if (macro_id $cond) :
            :
            break)
        (macro_id $body)
        continue))


(macro pub try STMT_LIST [
        (mparam $name ID)
        (mparam $type EXPR)
        (mparam $expr EXPR)
        (mparam $catch_name ID)
        (mparam $catch_body STMT_LIST)] [$eval] :
    (macro_let $eval auto (macro_id $expr))
    (if (is (macro_id $eval) (macro_id $type)) :
        :
        (macro_let $catch_name auto (asnot (macro_id $eval) (macro_id $type)))
        (macro_id $catch_body)
        (trap))
    (macro_let $name (macro_id $type) (tryas (macro_id $eval) (macro_id $type) undef)))


(fun pub extern IsLogActive [(param level u8) (param loc u32)] void :)


(# "generic copy of data from slice/array to slice")
(macro copy_slice STMT_LIST [
        (mparam $item_type TYPE)
        (mparam $src EXPR)
        (mparam $dst EXPR)
        (mparam $len EXPR)] [$psrc $pdst $n $i] :
    (macro_let $psrc auto (as (macro_id $src) (ptr (macro_id $item_type))))
    (macro_let $pdst auto (as (macro_id $dst) (ptr mut (macro_id $item_type))))
    (macro_let $n uint (min (macro_id $len) (len (macro_id $dst))))
    (for (macro_id $i) uint 0 (macro_id $n) 1 [(= (^ (incp (macro_id $pdst) (macro_id $i) undef)) (^ (incp (macro_id $psrc) (macro_id $i) undef)))]))


(fun pub memcpy [
        (param dst (ptr mut u8))
        (param src (ptr u8))
        (param size uint)] uint :
    (for i uint 0 size 1 :
        (= (^ (incp dst i undef)) 
        (^ (incp src i undef))))
    (return size))


(fun polymorphic SysRender [
        (param v bool)
        (param buffer (slice mut u8))
        (param options (ptr mut SysFormatOptions))] uint :
    (let s auto (? v (as "true" (slice u8)) (as "false" (slice u8))))
    (let n uint (min (len buffer) (len s)))
    (return (call memcpy [
            (as buffer (ptr mut u8))
            (as s (ptr u8))
            n])))


(macro unsigned_to_str STMT_LIST [
        (mparam $val EXPR)
        (mparam $base EXPR)
        (mparam $max_width EXPR)
        (mparam $out ID)] [$v $tmp $pos] :
    (# "unsigned to str with give base")
    (macro_let mut $v auto (macro_id $val))
    (macro_let mut $tmp auto (array_val (macro_id $max_width) u8 []))
    (macro_let mut $pos uint (macro_id $max_width))
    (block _ :
        (-= (macro_id $pos) 1)
        (let c auto (% (macro_id $v) (macro_id $base)))
        (let mut c8 auto (as c u8))
        (+= c8 (? (<= c8 9) '0' (- 'a' 10)))
        (= (at (macro_id $tmp) (macro_id $pos)) c8)
        (/= (macro_id $v) (macro_id $base))
        (if (!= (macro_id $v) 0) :
            continue
            :))
    (let n uint (min (- (macro_id $max_width) (macro_id $pos)) (len (macro_id $out))))
    (return (call memcpy [
            (as (macro_id $out) (ptr mut u8))
            (incp (as (macro_id $tmp) (ptr u8)) (macro_id $pos) undef)
            n])))


(fun polymorphic SysRender [
        (param v u8)
        (param out (slice mut u8))
        (param options (ptr mut SysFormatOptions))] uint :
    (unsigned_to_str v 10 32_uint out))


(fun polymorphic SysRender [
        (param v u16)
        (param out (slice mut u8))
        (param options (ptr mut SysFormatOptions))] uint :
    (unsigned_to_str v 10 32_uint out))


(fun polymorphic SysRender [
        (param v u32)
        (param out (slice mut u8))
        (param options (ptr mut SysFormatOptions))] uint :
    (unsigned_to_str v 10 32_uint out))


(fun polymorphic SysRender [
        (param v u64)
        (param out (slice mut u8))
        (param options (ptr mut SysFormatOptions))] uint :
    (unsigned_to_str v 10 32_uint out))


(fun polymorphic SysRender [
        (param v (slice u8))
        (param buffer (slice mut u8))
        (param options (ptr mut SysFormatOptions))] uint :
    (let n uint (min (len buffer) (len v)))
    (return (call memcpy [
            (as buffer (ptr mut u8))
            (as v (ptr u8))
            n])))


(macro print_common STMT_LIST [(mparam $curr ID) (mparam $parts STMT_LIST)] [$buffer $options $buffer_orig] :
    (macro_let mut $buffer auto (array_val 1024 u8 []))
    (macro_let mut $curr (slice mut u8) (macro_id $buffer))
    (macro_let mut ref $options auto (rec_val SysFormatOptions []))
    (macro_for $i $parts :
        (= (macro_id $curr) (incp (macro_id $curr) (call polymorphic SysRender [
                (macro_id $i)
                (macro_id $curr)
                (& mut (macro_id $options))]) undef)))
    (macro_let $buffer_orig (slice u8) (macro_id $buffer))
    (stmt (call SysPrint [(pdelta (macro_id $buffer_orig) (macro_id $curr))])))


(macro pub print STMT_LIST [(mparam $parts STMT_LIST)] [$curr] :
    (print_common (macro_id $curr) [(macro_id $parts)])
    (stmt (call SysPrint [(macro_id $curr)])))


(macro swap STMT_LIST [(mparam $a EXPR) (mparam $b EXPR)] [$t] :
    (macro_let $t auto (macro_id $a))
    (= (macro_id $a) (macro_id $b))
    (= (macro_id $b) (macro_id $t)))


(macro pub log STMT [(mparam $level EXPR) (mparam $parts STMT_LIST)] [$curr] :
    (if (call IsLogActive [(macro_id $level) (src_loc)]) :
        (print_common (macro_id $curr) [(macro_id $parts)])
        (stmt (call SysErrorPrint [(macro_id $curr)]))
        :))


(macro pub assert STMT [(mparam $cond EXPR) (mparam $parts STMT_LIST)] [$curr] :
    (if (macro_id $cond) :
        :
        (print_common (macro_id $curr) [(macro_id $parts)])
        (stmt (call SysErrorPrint [(macro_id $curr)]))
        (trap)))

)


