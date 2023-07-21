@doc "Word Count Example"
(module main [] :

(enum @pub Mode U32 :
    (entry r 1)
    (entry w 2)
    (entry rw 3))


@doc "This is an incomplete dummy"
(defrec @pub File :
    (field handle s32))


(type @pub FP (ptr @mut File))


(type @pub @wrapped errorOpen void)


(type @pub @wrapped errorClose void)


(type @pub @wrapped errorRead void)


(type @pub errorIO (union [
        errorOpen
        errorClose
        errorRead]))


(fun @pub @extern fopen [(param fname (slice u8)) (param mode Mode)] (union [FP errorOpen]) :)


(fun @pub @extern fread [(param fp FP) (param buffer (slice @mut u8))] (union [u64 errorRead]) :)


(fun @pub @extern fclose [(param fp FP)] (union [void errorClose]) :)


(fun @pub @extern is_white_space [(param c u8)] bool :)


(defrec TextStats :
    (field num_lines u64)
    (field num_words u64)
    (field num_chars u64))


(fun @pub WordCount [(param fname (slice u8))] (union [TextStats errorIO]) :
    (let @mut stats auto (rec_val TextStats [
            (field_val 0)
            (field_val 0)
            (field_val 0)]))
    (let @mut in_word auto false)
    (try fp FP (call fopen [fname Mode::r]) err :
        (return err))
    (let @mut buf (array 128 u8) undef)
    (while true :
        (try n u64 (call fread [fp buf]) err :
            (stmt (call fclose [fp]))
            (return err))
        (+= (. stats num_chars) n)
        (for i u64 0 n 1 :
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
    (try _ void (call fclose [fp]) err :
        (return err))
    (return stats))

)


