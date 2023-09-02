@doc "Word Count Example"
(module main [] :
(import os)


(fun @pub @extern is_white_space [(param c u8)] bool :)

(macro @pub try STMT_LIST [
        (mparam $name ID)
        (mparam $type EXPR)
        (mparam $expr EXPR)
        (mparam $catch_name ID)
        (mparam $catch_body STMT_LIST)] [$eval] :
    (macro_let $eval auto $expr)
    (if (is $eval $type) :
        :
        (macro_let $catch_name auto (sumas @unchecked $eval (sumdelta (typeof $eval) $type)))
        $catch_body
        (trap))
    (macro_let $name $type (sumas @unchecked $eval $type)))


@doc "macro for while-loop"
(macro @pub while STMT [(mparam $cond EXPR) (mparam $body STMT_LIST)] [] :
    (block _ :
        (if $cond :
            :
            (break))
        $body
        (continue)))


@doc "macro for number range for-loop"
(macro @pub for STMT_LIST [
        (mparam $index ID)
        (mparam $start EXPR)
        (mparam $end EXPR)
        (mparam $step EXPR)
        (mparam $body STMT_LIST)] [$end_eval $step_eval $it] :
    (macro_let $end_eval (typeof $end) $end)
    (macro_let $step_eval (typeof $end) $step)
    (macro_let @mut $it (typeof $end) $start)
    (block _ :
        (if (>= $it $end_eval) :
            (break)
            :)
        (macro_let $index auto $it)
        (= $it (+ $it $step_eval))
        $body
        (continue)))

(defrec TextStats :
    (field num_lines uint)
    (field num_words uint)
    (field num_chars uint))


(fun WordCount [(param fd os::FD)] (union [TextStats os::Error]) :
    (let @mut stats auto (rec_val TextStats []))
    (let @mut in_word auto false)
    (let @mut buf (array 1024 u8) undef)
    (while true :
        (try n uint (call os::FileRead [fd buf]) err :
            (return err))
        (if (==  n 0) : break : )
        (+= (. stats num_chars) n)
        (for i 0 n 1 :
            (let c auto (at buf i))
            (cond :
                (case (== c '\n') :
                    (+= (. stats num_lines) 1))
                (case (call is_white_space [c]) :
                    (= in_word false))
                (case (! in_word) :
                    (= in_word true)
                    (+= (. stats num_words) 1)))
            (if (!= n (len buf)) :
                (break)
                :)))
    (return stats))

(fun @cdecl main [(param argc s32) (param argv (ptr (ptr u8)))] s32 :
    (try stats TextStats (call WordCount [os::Stdin]) err :
        (return 1)
    )
    (return 0))

)


