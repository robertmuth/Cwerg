(module ansi [] :
(# """Ansi Escape Sequences for Terminal Emulation 

* https://www.xfree86.org/current/ctlseqs.html")
* https://gist.github.com/fnky/458719343aabd01cfb17a3a4f7296797
""")

(global pub CLEAR_ALL auto "\x1b[2J")

(global pub SET_MODE_BOLD auto "\x1b[1m")
(global pub SET_MODE_DIM auto "\x1b[2m")
(global pub SET_MODE_ITALIC auto "\x1b[3m")
(global pub SET_MODE_UNDERLINE auto "\x1b[4m")
(global pub SET_MODE_BLINKING auto "\x1b[5m")
(global pub SET_MODE_INVERSE auto "\x1b[6m")
(global pub SET_MODE_HIDDEN auto "\x1b[7m")
(global pub SET_MODE_STRIKE_THROUGH auto "\x1b[8m")

(# "also clears color settings")
(global pub RESET_MODE_ALL auto "\x1b[0m")
(global pub RESET_MODE_BOLD_OR_DIM auto "\x1b[22m")
(global pub RESET_MODE_ITALIC auto "\x1b[23m")
(global pub RESET_MODE_UNDERLINE auto "\x1b[24m")
(global pub RESET_MODE_BLINKING auto "\x1b[25m")
(global pub RESET_MODE_INVERSE auto "\x1b[26m")
(global pub RESET_MODE_HIDDEN auto "\x1b[27m")
(global pub RESET_MODE_STRIKE_THROUGH auto "\x1b[28m")

(global pub CURSOR_SHOW auto "\x1b[?25l")
(global pub CURSOR_HIDE auto "\x1b[?25h")


(macro POS EXPR_LIST [(mparam $x EXPR)  (mparam $y EXPR)] [] :
   "\x1b[" $x  ";"  $y  "f" )

(macro FG_COLOR EXPR_LIST [(mparam $r EXPR) (mparam $g EXPR) (mparam $b EXPR)] [] :
   "\x1b[38;2;"  $r ";"  $g ";" $b  "m" 
)

(macro BG_COLOR EXPR_LIST [(mparam $r EXPR) (mparam $g EXPR) (mparam $b EXPR)] [] :
   "\x1b[48;2;" $r ";" $g ";" $b  "m" 
)

)

(module artwork [] :
(import ansi)



(# """
* https://github.com/cmatsuoka/asciiquarium
* https://robobunny.com/projects/asciiquarium/
* Artwork by Joan Stark: http://www.geocities.com/SoHo/7373/ (see archive.org copy)
""")


(# """
Color codes and xterm rgb values:
k  black    0,0,0
r  red      205,0, 0
g  green    0,205,0
y  yellow   205,205,0
b  blue     0,0,238
m  magenta  205,0,205
c  cyan     0,205,205
w  white    229,229,229
t  translucent
""")


(global MAX_DIM u32 1000)

(defrec pub Object :
    (field name (slice u8))
    (field image_map (slice u8))
    (field color_map (slice u8))
    (field def_color u8)
    (field def_x s32)
    (field def_y s32)
    (field def_z s32)

)

(global pub Castle auto (rec_val Object [
    (field_val "castle")
    (field_val r"""
                 T~~
                 |
                /^\
               /   \
   _   _   _  /     \  _   _   _
  [ ]_[ ]_[ ]/ _   _ \[ ]_[ ]_[ ]
  |_=__-_ =_|_[ ]_[ ]_|_=-___-__|
   | _- =  | =_ = _    |= _=   |
   |= -[]  |- = _ =    |_-=_[] |
   | =_    |= - ___    | =_ =  |
   |=  []- |-  /| |\   |=_ =[] |
   |- =_   | =| | | |  |- = -  |
   |_______|__|_|_|_|__|_______|
""")
    (field_val r"""
                  RR
  
                yyy
               y   y
              y     y
             y       y
  
  
  
                yyy
               yy yy
              y y y y
              yyyyyyy
""")
    (field_val 'B')
    (field_val -32)
    (field_val -13)
    (field_val 22)
]))

(fun pub draw [(param obj (ptr Object)) 
               (param xx u32) 
               (param yy u32) 
               (param bg_col u8)] void :
    (let image_map auto (. (^ obj) image_map))
    (let color_map auto (. (^ obj) color_map))
    (let mut x u32 xx)
    (let mut y u32 yy)
    (let are_inside_obj auto false)
    (let have_color auto true)


    (for ipos uint 0 (len image_map) 1 :
        (let i u8 (at image_map ipos))
        (if (== i '\n') :
            (+= y 1)
            (= x xx)
            continue
        :)
        (print [(ansi::POS y x) (as i rune)])
        (+= x 1)
    )
)

)


(module main [] :
(import ansi)
(import artwork)

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

    (let ref req TimeSpec (rec_val TimeSpec [(field_val 1) (field_val 0)]))
    (let mut ref rem TimeSpec undef)

    (for i uint 1 6 1 :
        (print [ansi::CLEAR_ALL 
                (ansi::POS i i) 
                (ansi::FG_COLOR 0_uint 0_uint 255_uint) 
                "asciiquarium aa" 
                (ansi::POS 20_uint 10_uint) 
                (ansi::FG_COLOR 255_uint 0_uint 0_uint) 
                w "x" h "\n" 
                ])
        (stmt (call artwork::draw [(& artwork::Castle) 1 1 'k']))
        (stmt (call nanosleep [(& req) (& mut rem)]))
    )
    (return 0))

)