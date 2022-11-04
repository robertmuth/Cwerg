(mod main [] [
    (# "Word Count example")

    (# "File StdLib bindings")
    (enum pub Mode U32 [
        (entry r 1)
        (entry w 2)
        (entry rw 3)])

    (rec pub File [
        (# "This is an incomplete dummy")
        (field handle s32)
    ])

    (type pub FP (ptr mut File))
 
    (type pub wrapped errorOpen void)
    (type pub wrapped errorClose void)
    (type pub wrapped errorRead void)
    (type pub errorIO (union [errorOpen errorClose errorRead]))
 

    (fun pub extern fopen [(param fname (slice u8)) (param mode Mode)] (union [FP errorOpen]) [])
    (fun pub extern fread [(param fp FP) (param buffer (slice mut u8))] (union [u64 errorRead]) [])
    (fun pub extern fclose [(param fp FP)] (union [void errorClose]) [])
    (fun pub extern is_white_space [(param c u8)] bool [])

    (rec TextStats [
        (# "This is an incomplete dummy")
        (field num_lines u64 0)
        (field num_words u64 0)
        (field num_chars u64 0)
   ])

  (fun pub WordCount  [(param fname (slice u8))]  (union [TextStats errorIO]) [
    (let mut stats (ValRec TextStats []))
    (let in_word false)
    (try fp FP (call fopen [fname Mode/r]) (catch err [(return err)]))
    (let mut buf auto (ValArray u8 128 [(IndexVal undef)]))
    (while true [
        (try n u64 (call fread [fp buf]) (catch err [(return err)]))
        (+= (. stats num_chars) n)
        (for i u64 (range n) [
             (let c auto (at buf i))
             (cond [
                 (case (== c '\n') [
                    (+= (. stats num_lines) 1)]) 
                 (case (call is_white_space [c]) [
                    (= in_word false)])
                 (case (! in_word) [
                    (= in_word true) 
                    (+= (. stats num_words) 1)])
             ])
             (if (!= n (len buf)) [(break)] [])
        ])
    ])
    (return stats)
  ])
])