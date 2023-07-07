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

(# "FG")
(global pub FG_COLOR_BLACK auto "\x1b[38;2;0;0;0m")
(global pub FG_COLOR_RED auto "\x1b[38;2;205;0;0m")
(global pub FG_COLOR_GREEN auto "\x1b[38;2;0;205;0m")
(global pub FG_COLOR_YELLOW auto "\x1b[38;2;205;205;0m")
(global pub FG_COLOR_BLUE auto "\x1b[38;2;0;0;238m")
(global pub FG_COLOR_MAGENTA auto "\x1b[38;2;205;0;205m")
(global pub FG_COLOR_CYAN auto "\x1b[38;2;0;205;205m")
(global pub FG_COLOR_WHITE auto "\x1b[38;2;229;229;229m")

(macro FG_COLOR EXPR_LIST [(mparam $r EXPR) (mparam $g EXPR) (mparam $b EXPR)] [] :
   "\x1b[38;2;"  $r ";"  $g ";" $b  "m" 
)

(# "BG")
(global pub BG_COLOR_BLACK auto "\x1b[48;2;0;0;0m")
(global pub BG_COLOR_RED auto "\x1b[48;2;205;0;0m")
(global pub BG_COLOR_GREEN auto "\x1b[48;2;0;205;0m")
(global pub BG_COLOR_YELLOW auto "\x1b[48;2;205;205;0m")
(global pub BG_COLOR_BLUE auto "\x1b[48;2;0;0;238m")
(global pub BG_COLOR_MAGENTA auto "\x1b[48;2;205;0;205m")
(global pub BG_COLOR_CYAN auto "\x1b[48;2;0;205;205m")
(global pub BG_COLOR_WHITE auto "\x1b[48;2;229;229;229m")

(macro BG_COLOR EXPR_LIST [(mparam $r EXPR) (mparam $g EXPR) (mparam $b EXPR)] [] :
   "\x1b[48;2;" $r ";" $g ";" $b  "m" 
)

)

(module aanim [] :
(# "Ascii Art Animation Module")
(import ansi)


(global MAX_DIM u32 1024)

(defrec pub Window :
    (field w u32)
    (field h u32)
    (field char_map (array (* MAX_DIM MAX_DIM) u8))
    (field attr_map (array (* MAX_DIM MAX_DIM) u8)))


(defrec pub Object :
    (field name (slice u8))
    (field image_map (slice u8))
    (field color_map (slice u8))
    (field def_color u8)
    (field def_z s32)
)

(fun tolower [(param c u8)] u8 :
    (return (or c 0x20))
)

(fun get_style [(param attr u8)] (slice u8) :
    (return (? (< attr 'a') 
        (as ansi::SET_MODE_BOLD (slice u8)) 
        (as ansi::RESET_MODE_BOLD_OR_DIM (slice u8)))))

(fun get_fg_color [(param attr u8)] (slice u8) :
   (let col u8 (call tolower [attr]))
   (cond :
    (case (== col 'k') : (return ansi::FG_COLOR_BLACK))
    (case (== col 'r') : (return ansi::FG_COLOR_RED))
    (case (== col 'g') : (return ansi::FG_COLOR_GREEN))
    (case (== col 'y') : (return ansi::FG_COLOR_YELLOW))
    (case (== col 'b') : (return ansi::FG_COLOR_BLUE))
    (case (== col 'm') : (return ansi::FG_COLOR_MAGENTA))
    (case (== col 'c') : (return ansi::FG_COLOR_CYAN))
    (case (== col 'w') : (return ansi::FG_COLOR_WHITE))
    (case true : (return ""))
   )
)

(fun get_bg_color [(param attr u8)] (slice u8) :
   (let col u8 (call tolower [attr]))
   (cond :
    (case (== col 'k') : (return ansi::BG_COLOR_BLACK))
    (case (== col 'r') : (return ansi::BG_COLOR_RED))
    (case (== col 'g') : (return ansi::BG_COLOR_GREEN))
    (case (== col 'y') : (return ansi::BG_COLOR_YELLOW))
    (case (== col 'b') : (return ansi::BG_COLOR_BLUE))
    (case (== col 'm') : (return ansi::BG_COLOR_MAGENTA))
    (case (== col 'c') : (return ansi::BG_COLOR_CYAN))
    (case (== col 'w') : (return ansi::BG_COLOR_WHITE))
    (case true : (return ""))
   )
)

(fun pub draw [(param obj (ptr Object)) 
               (param xx u32) 
               (param yy u32) 
               (param def_col u8)
               (param colors (slice u8))] void :
    (let image_map auto (. (^ obj) image_map))
    (let color_map auto (. (^ obj) color_map))
    (let mut x u32 xx)
    (let mut y u32 yy)
    (let mut left_side auto true)
    (let mut have_color auto true)

    (let mut cpos uint 0)
    (for ipos uint 0 (len image_map) 1 :
        (# "determine color and style")
        (let mut c u8 def_col)
        (if have_color :
            (let cc u8 (at color_map cpos))
            (+= cpos 1)
            (cond :
               (case (== cc '\n') : (= have_color false))
               (case (== cc ' ') :)
               (case (&& (>= cc '1') (<= cc '9')) : (= c (at colors (- cc '1'))))
               (case true : (= c cc))
            )
        :)

        (# "determine shape")
        (let i u8 (at image_map ipos))
        (if (== i '\n') :
            (+= y 1)
            (= x xx)
            (= left_side true)
            (# "the end of the color row should have been reached already")
            (assert (! have_color) ["color failure\n"])
            (if (< cpos (len color_map)) : 
                (= have_color true)
            :)
            continue
        :)

        (if (!= i ' ') :
            (= left_side false) 
        :)
        (if (! left_side) :
            (print [(call get_fg_color [c]) (ansi::POS y x) (as i rune)])
        :)

        (+= x 1)
    )
)


(fun pub window_draw [(param obj (ptr Window)) (param bg_col u8)] void :
    (print [(call get_bg_color [bg_col]) ansi::CLEAR_ALL])
    (let w auto (. (^ obj) w))
    (let h auto (. (^ obj) h))

    (# "@ is an invalid attrib")
    (let mut last_attr u8 '@')
    (for x u32 0 w 1 :
        (let mut last_x auto MAX_DIM)
        (for y u32 0 h 1 :
          (let index auto (+ (* y w) x))
          (let c auto (at (. (^ obj) char_map) index))
          (let a auto (at (. (^ obj) attr_map) index))
          (if (== c ' ') : 
            continue
          :)
          (if (!= x (+ last_x 1)) :
            (print [(ansi::POS (+ y 1) (+ x 1))])
          :)
          (= last_x x)
          (if (!= last_attr a) :
            (print [(call get_fg_color [a]) (call get_style [a])])
          :)
          (= last_attr a)
        (print [(as c rune)])
        )
    )
)

(fun pub window_fill [(param obj (ptr mut Window)) (param c u8) (param a u8)] void :
    (let size u32 (* (. (^ obj) w) (. (^ obj) h)))
    (for i u32 0 size 1 :
        (= (at  (. (^ obj) char_map) i) c)
        (= (at  (. (^ obj) attr_map) i) a)
    )
)

)


(module artwork [] :
(import aanim)


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


Fish body parts:
1: body
2: dorsal fin
3: flippers
4: eye
5: mouth
6: tailfin
7: gills
""")




(global pub RandomColor auto "RcRyBgM")


(global pub Castle auto (rec_val aanim::Object [
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
    (field_val 22)
]))


(global pub SwanL auto (rec_val aanim::Object [
    (field_val "swan_l")
    (field_val r"""
 ___
/,_ \    _,
|/ )/   / |
  //  _/  |
 / ( /   _)
/   `   _/)
\  ~=-   /
""")
    (field_val r"""

 g
yy
""")
    (field_val 'W')
    (field_val 3)
]))


(global pub SwanR auto (rec_val aanim::Object [
    (field_val "swan_r")
    (field_val r"""
        ___
 ,_    / _,\
 | \   \( \|
 |  \_  \\\
 (_   \_) \
 (\_   `   \
  \   -=~  /
""")
    (field_val r"""

          g
          yy
""")
    (field_val 'W')
    (field_val 3)
]))


(global pub DuckR1 auto (rec_val aanim::Object [
    (field_val "duck_r1")
    (field_val r"""
      _??????????_??????????_  
,____(')=??,____(')=??,____(')<
 \~~= ')????\~~= ')????\~~= ') 
""")
    (field_val r"""
      g          g          g
wwwwwgcgy  wwwwwgcgy  wwwwwgcgy
 wwww Ww    wwww Ww    wwww Ww
""")
    (field_val 'W')
    (field_val 3)
]))

(global pub DuckR2 auto (rec_val aanim::Object [
    (field_val "duck_r2")
    (field_val r"""
      _??????????_??????????_  
,____(')=??,____(')<??,____(')=
 \~~= ')????\~~= ')????\~~= ') 
""")
    (field_val r"""
      g          g          g
wwwwwgcgy  wwwwwgcgy  wwwwwgcgy
 wwww Ww    wwww Ww    wwww Ww
""")
    (field_val 'W')
    (field_val 3)
]))

(global pub DuckR3 auto (rec_val aanim::Object [
    (field_val "duck_r3")
    (field_val r"""
      _??????????_??????????_  
,____(')<??,____(')=??,____(')=
 \~~= ')????\~~= ')????\~~= ') 
""")
    (field_val r"""
      g          g          g
wwwwwgcgy  wwwwwgcgy  wwwwwgcgy
 wwww Ww    wwww Ww    wwww Ww
""")
    (field_val 'W')
    (field_val 3)
]))

(global pub DophinR1 auto (rec_val aanim::Object [
    (field_val "dolphin_r1")
    (field_val r"""
        ,
      __)\_
(\_.-'    a`-.
(/~~````(/~^^`
""")
    (field_val r"""


          W
""")
    (field_val 'b')
    (field_val 3)
]))

(global pub DophinR2 auto (rec_val aanim::Object [
    (field_val "dolphin_r2")
    (field_val r"""
        ,
(\__  __)\_
(/~.''    a`-.
    ````\)~^^`
""")
    (field_val r"""


          W
""")
    (field_val 'b')
    (field_val 3)
]))

(global pub DophinL1 auto (rec_val aanim::Object [
    (field_val "dolphin_l1")
    (field_val r"""
     ,
   _/(__
.-'a    `-._/)
'^^~\)''''~~\)
""")
    (field_val r"""


   W
""")
    (field_val 'b')
    (field_val 3)
]))

(global pub DophinL2 auto (rec_val aanim::Object [
    (field_val "dolphin_l2")
    (field_val r"""
     ,
   _/(__  __/)
.-'a    ``.~\)
'^^~(/''''
""")
    (field_val r"""


   W
""")
    (field_val 'b')
    (field_val 3)
]))



(global pub BigFishR auto (rec_val aanim::Object [
    (field_val "dolphin_l2")
    (field_val r"""
 ______
`""-.  `````-----.....__
     `.  .      .       `-.
       :     .     .       `.
 ,     :   .    .          _ :
: `.   :                  (@) `._
 `. `..'     .     =`-.       .__)
   ;     .        =  ~  :     .-"
 .' .'`.   .    .  =.-'  `._ .'
: .'   :               .   .'
 '   .'  .    .     .   .-'
   .'____....----''.'=.'
   ""             .'.'
               ''"'`
""")
    (field_val r"""
 111111
11111  11111111111111111
     11  2      2       111
       1     2     2       11
 1     1   2    2          1 1
1 11   1                  1W1 111
 11 1111     2     1111       1111
   1     2        1  1  1     111
 11 1111   2    2  1111  111 11
1 11   1               2   11
 1   11  2    2     2   111
   111111111111111111111
   11             1111
               11111
""")
    (field_val 'Y')
    (field_val 2)
]))



)


(module main [] :
(import artwork)
(import aanim)
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

    (let ref req TimeSpec (rec_val TimeSpec [(field_val 1) (field_val 0)]))

    (let mut ref rem TimeSpec undef)

    (let ref window auto (rec_val aanim::Window [
        (field_val w)
        (field_val h)
    ])
    )

    (stmt (call aanim::window_fill [(& mut window) '#' 'y']))
    (stmt (call aanim::window_draw [(& window) 'b' ]))
    
    (return 0)

    (print [ansi::BG_COLOR_GREEN ansi::CLEAR_ALL])
    (stmt (call aanim::draw [(& artwork::BigFishR) 1 1 'b' artwork::RandomColor]))

    (for i uint 3 10 1 :
      (print [ansi::CLEAR_ALL])
        (# """
        (print [
                (ansi::POS i i) 
                (ansi::FG_COLOR 0_uint 0_uint 255_uint) 
                "################################asciiquarium#######" 
                (ansi::POS 20_uint 10_uint) 
                (ansi::FG_COLOR 255_uint 0_uint 0_uint) 
                w "x" h "\n" 
                ])
                """)
        (stmt (call aanim::draw [(& artwork::Castle) 1 1 'b' artwork::RandomColor]))
        (stmt (call nanosleep [(& req) (& mut rem)]))
    )
    (return 0))

)