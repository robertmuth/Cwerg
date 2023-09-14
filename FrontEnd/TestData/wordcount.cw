@doc "Word Count Example"
(module main [] :
(import os)
(import fmt)


(fun is_white_space [(param c u8)] bool :
    (return (|| (|| (== c ' ') (== c '\n'))
                (|| (== c '\t') (== c '\r'))))
)

(defrec TextStats :
    (field num_lines uint)
    (field num_words uint)
    (field num_chars uint))


(fun WordCount [(param fd os::FD)] (union [TextStats os::Error]) :
    (let @mut stats auto (rec_val TextStats []))
    (let @mut in_word auto false)
    (let @mut buf (array 1024 u8) undef)
    (while true :
        (try n uint (os::FileRead [fd buf]) err :
            (return err))
        (if (==  n 0) : break : )
        (+= (. stats num_chars) n)
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

(fun @cdecl main [(param argc s32) (param argv (ptr (ptr u8)))] s32 :
    (try stats TextStats (WordCount [os::Stdin]) err :
        (return 1)
    )
    (fmt::print! [(. stats num_lines) " " (. stats num_words) " " (. stats num_chars) "\n"])
    (return 0))

)
