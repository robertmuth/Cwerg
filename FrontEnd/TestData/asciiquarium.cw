(module artwork [] :



)

(module ansi [] :
(# "https://www.xfree86.org/current/ctlseqs.html")
(# "https://gist.github.com/fnky/458719343aabd01cfb17a3a4f7296797")

(global pub MAX_ESC_SEQ_LEN uint 64)

(global pub CLEAR_ALL auto "\x1b[2J")


(global pub SET_MODE_BOLD auto "\x1b[1m")
(global pub SET_MODE_DIM auto "\x1b[2m")
(global pub SET_MODE_ITALIC auto "\x1b[3m")
(global pub SET_MODE_UNDERLINE auto "\x1b[4m")
(global pub SET_MODE_BLINKING auto "\x1b[5m")
(global pub SET_MODE_INVERSE auto "\x1b[6m")
(global pub SET_MODE_HIDDEN auto "\x1b[7m")
(global pub SET_MODE_STRIKE_THROUGH auto "\x1b[8m")

(global pub RESET_MODE_ALL auto "\x1b[0m")
(global pub RESET_MODE_BOLD_OR_DIM auto "\x1b[22m")
(global pub RESET_MODE_ITALIC auto "\x1b[23m")
(global pub RESET_MODE_UNDERLINE auto "\x1b[24m")
(global pub RESET_MODE_BLINKING auto "\x1b[25m")
(global pub RESET_MODE_INVERSE auto "\x1b[26m")
(global pub RESET_MODE_HIDDEN auto "\x1b[27m")
(global pub RESET_MODE_STRIKE_THROUGH auto "\x1b[28m")

(global pub CUSROR_HOME auto "\x1b[H")
(global pub CURSOR_SHOW auto "\x1b[?25l")
(global pub CURSOR_HIDE auto "\x1b[?25h")



(macro POS EXPR_LIST [(mparam $x EXPR)  (mparam $y EXPR)] [] :
   "\x1b[" 
   $x 
   ";" 
   $y 
   "f" 
)

(macro FG_COLOR EXPR_LIST [(mparam $r EXPR) (mparam $g EXPR) (mparam $b EXPR)] [] :
   "\x1b[38;2;"  $r ";"  $g ";" $b  "m" 
)

(macro BG_COLOR EXPR_LIST [(mparam $r EXPR) (mparam $g EXPR) (mparam $b EXPR)] [] :
   "\x1b[48;2;" $r ";" $g ";" $b  "m" 
)

)

(module main [] :
(import ansi)

(# "main module with program entry point `main`")
(fun main [(param argc s32) (param argv (ptr (ptr u8)))] s32 :
    (if (< argc 3) :
         (print ["Not enough arguments, need width and height\n"])
         (return 0)
    :)
    (let arg_w (slice u8) (call strz_to_slice [(^ (incp argv 1))]))
    (let arg_h (slice u8) (call strz_to_slice [(^ (incp argv 2))]))

    (let w u32 (call str_to_u32 [arg_w]))
    (let h u32 (call str_to_u32 [arg_h]))

    (print [ansi::CLEAR_ALL 
            (ansi::POS 10_uint 10_uint) 
            (ansi::FG_COLOR 0_uint 0_uint 255_uint) 
            "asciiquarium aa" 
            (ansi::POS 20_uint 10_uint) 
            (ansi::FG_COLOR 255_uint 0_uint 0_uint) 
            w "x" h "\n" 
            ])
    (return 0))

)