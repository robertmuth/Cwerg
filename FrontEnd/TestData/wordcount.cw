@doc "Word Count Example"
(module [] :
(import os)

(import fmt)


(fun is_white_space [(param c u8)] bool :
    (return (|| (|| (|| (== c ' ') (== c '\n')) (== c '\t')) (== c '\r'))))


@doc "word, line and character count statistics"
(defrec TextStats :
    (field num_lines uint)
    (field num_words uint)
    (field num_chars uint))


@doc "Returns either a TextStat or an Error"
(fun WordCount [(param fd os::FD)] (union [TextStats os::Error]) :
    @doc "note limited type inference in next two stmts"
    (let! stats auto (rec_val TextStats []))
    (let! in_word auto false)
    @doc "do not initialize buf with zeros"
    (let! buf (array 1024 u8) undef)
    (while true :
        @doc "if FileRead returns an uint, assign it to n else return it"
        (trylet n uint (os::FileRead [fd buf]) err :
            (return err))
        (if (== n 0) :
            (break)
         :)
        (+= (. stats num_chars) n)
        @doc "index variable has the same type as n."
        (for i 0 n 1 :
            (let c auto (at buf i))
            (cond :
                (case (== c '\n') :
                    (+= (. stats num_lines) 1))
                (case (is_white_space [c]) :
                    (= in_word false))
                (case (! in_word) :
                    (= in_word true)
                    (+= (. stats num_words) 1))))
        (if (!= n (len buf)) :
            (break)
         :))
    (return stats))


(fun main [(param argc s32) (param argv (ptr (ptr u8)))] s32 :
    (trylet stats TextStats (WordCount [os::Stdin]) err :
        (return 1))
    @doc """print# is a stmt macro for printing arbitrary values.
(It is possible to define formatters for custom types.)"""
    (fmt::print# (. stats num_lines) " " (. stats num_words) " " (. stats num_chars) "\n")
    (return 0))
)
