

(module aanim [] :
(# "Ascii Art Animation Module")
(import ansi)

(# "arbitrary bound so we can statically allocate maps")
(global MAX_DIM s32 1024)

(global pub DEF_ATTR_LOOKUP auto "RcRyBgM")

(defrec pub Window :
    (field width s32)
    (field height s32)
    (field char_map (array (* MAX_DIM MAX_DIM) u8))
    (field attr_map (array (* MAX_DIM MAX_DIM) u8))
    (field depth_map (array (* MAX_DIM MAX_DIM) u8)))

(defrec pub Sprite :
    (field image_map (slice u8))
    (field color_map (slice u8)))

(defrec pub Object :
    (field name (slice u8))
    (field sprites (slice Sprite))
    (field def_attr u8)
    (field def_depth u8)
    (field transparent_char u8)
    (field def_x_speed r32)
    (field def_y_speed r32))


(defrec pub ObjectState :
    (field obj (ptr Object))
    (field start_time r32)
    (field x_pos r32)
    (field y_pos r32)
    (field depth u8)
    (field frame u8)
    (field x_speed r32)
    (field y_speed r32)
    (field attr_lookup (slice u8))
    (field def_attr u8)
    (# "updated by draw")
    (field visible bool))


(fun pub InitObjectState [
        (param s (ptr mut ObjectState))
        (param o (ptr Object))] void :
    (= (-> s obj) o)
    (= (-> s attr_lookup) DEF_ATTR_LOOKUP)
    (= (-> s depth) (-> o def_depth))
    (= (-> s frame) 0)
    (= (-> s def_attr) (-> o def_attr))
    (= (-> s x_speed) (-> o def_x_speed))
    (= (-> s y_speed) (-> o def_y_speed)))

(fun pub SetBasics [
        (param s (ptr mut ObjectState)) 
        (param start_time r32) (param x_pos r32) (param y_pos r32)] void :
        (= (-> s start_time) start_time)
        (= (-> s x_pos) x_pos)
        (= (-> s y_pos) y_pos))



(fun tolower [(param c u8)] u8 :
    (return (or c 0x20)))


(fun get_style [(param attr u8)] (slice u8) :
    (return (? (< attr 'a') (as ansi::SET_MODE_BOLD (slice u8)) (as ansi::RESET_MODE_BOLD_OR_DIM (slice u8)))))


(fun get_fg_color [(param attr u8)] (slice u8) :
    (let col u8 (call tolower [attr]))
    (cond :
        (case (== col 'k') :
            (return ansi::FG_COLOR_BLACK))
        (case (== col 'r') :
            (return ansi::FG_COLOR_RED))
        (case (== col 'g') :
            (return ansi::FG_COLOR_GREEN))
        (case (== col 'y') :
            (return ansi::FG_COLOR_YELLOW))
        (case (== col 'b') :
            (return ansi::FG_COLOR_BLUE))
        (case (== col 'm') :
            (return ansi::FG_COLOR_MAGENTA))
        (case (== col 'c') :
            (return ansi::FG_COLOR_CYAN))
        (case (== col 'w') :
            (return ansi::FG_COLOR_WHITE))
        (case true :
            (return ""))))


(fun get_bg_color [(param attr u8)] (slice u8) :
    (let col u8 (call tolower [attr]))
    (cond :
        (case (== col 'k') :
            (return ansi::BG_COLOR_BLACK))
        (case (== col 'r') :
            (return ansi::BG_COLOR_RED))
        (case (== col 'g') :
            (return ansi::BG_COLOR_GREEN))
        (case (== col 'y') :
            (return ansi::BG_COLOR_YELLOW))
        (case (== col 'b') :
            (return ansi::BG_COLOR_BLUE))
        (case (== col 'm') :
            (return ansi::BG_COLOR_MAGENTA))
        (case (== col 'c') :
            (return ansi::BG_COLOR_CYAN))
        (case (== col 'w') :
            (return ansi::BG_COLOR_WHITE))
        (case true :
            (return ""))))


(fun pub draw [
        (param window (ptr mut Window))
        (param s (ptr mut ObjectState))] void :
    (let width auto (-> window width))
    (let height auto (-> window height))
    (let obj auto (-> s obj))
    (let sprite auto (& (at (-> obj sprites) (-> s frame))))
    (let image_map auto (-> sprite image_map))
    (let color_map auto (-> sprite color_map))
    (let def_attr auto (-> s def_attr))
    (let depth auto (-> s depth))

    (let mut x s32 (as (-> s x_pos) s32))
    (let mut y s32 (as (-> s y_pos) s32))
    (let mut left_side auto true)
    (let mut have_color auto true)
    (let mut cpos uint 0)
    (for ipos uint 0 (len image_map) 1 :
        (# "determine attribute")
        (let mut a u8 def_attr)
        (if have_color :
            (let cc u8 (at color_map cpos))
            (+= cpos 1)
            (cond :
                (case (== cc '\n') :
                    (= have_color false))
                (case (== cc ' ') :)
                (case (&& (>= cc '1') (<= cc '9')) :
                    (= a (at (-> s  attr_lookup) (- cc '1'))))
                (case true :
                    (= a cc)))
            :)
        (# "determine character")
        (let c u8 (at image_map ipos))
        (if (== c '\n') :
            (+= y 1)
            (= x  (as (-> s x_pos) s32))
            (= left_side true)
            (# "the end of the color row should have been reached already")
            (assert (! have_color) ["color failure\n"])
            (if (< cpos (len color_map)) :
                (= have_color true)
                :)
            (continue)
            :)
        (if (!= c ' ') :
            (= left_side false)
            :)
        (let index auto (+ (* y width) x))
        (if (!= 0_u8 (at (-> window depth_map) index)) :
            (if (&& (! left_side) (!= c (-> obj transparent_char))) :
                (if (&& (< x width) (< y height)) :
                    (let i auto (+ (* y width) x))
                    (= (at (-> window char_map) index) c)
                    (= (at (-> window attr_map) index) a)
                    :)
                :)
            :)
        (+= x 1)))

(fun pub window_draw [(param obj (ptr Window)) (param bg_col u8)] void :
    (print [(call get_bg_color [bg_col]) ansi::CLEAR_ALL])
    (let w auto (-> obj width))
    (let h auto (-> obj height))
    (# "@ is an invalid attrib")
    (let mut last_attr u8 '@')
    (for x s32 0 w 1 :
        (let mut last_x auto MAX_DIM)
        (for y s32 0 h 1 :
            (let index auto (+ (* y w) x))
            (let c auto (at (-> obj char_map) index))
            (let a auto (at (-> obj attr_map) index))
            (if (== c ' ') :
                (continue)
                :)
            (if (!= x (+ last_x 1)) :
                (print [(ansi::POS (+ y 1) (+ x 1))])
                :)
            (= last_x x)
            (if (!= last_attr a) :
                (print [(call get_fg_color [a]) (call get_style [a])])
                :)
            (= last_attr a)
            (print [(as c rune)]))))


(fun pub window_fill [
        (param obj (ptr mut Window))
        (param c u8)
        (param a u8)] void :
    (let size auto (* (-> obj width) (-> obj height)))
    (for i s32 0 size 1 :
        (= (at (-> obj char_map) i) c)
        (= (at (-> obj attr_map) i) a)
        (= (at (-> obj depth_map) i) 255)))


(# "eom"))


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



(global CastleSprites auto (array_val 1 aanim::Sprite [
    (index_val
        (rec_val aanim::Sprite [
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
""")]))
]))

(global pub Castle auto (rec_val aanim::Object [
        (field_val "castle")
        (field_val CastleSprites)
        (field_val 'B')
        (field_val 22 def_depth)
        ]))

(global SwanLSprites auto (array_val 1 aanim::Sprite [
    (index_val
        (rec_val aanim::Sprite [
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
""")]))
]))     




(global pub SwanL auto (rec_val aanim::Object [
        (field_val "swan_l")
        (field_val SwanLSprites)
        (field_val 'W')
        (field_val 3 def_depth)
        (field_val -1.0_r32 def_x_speed)]))

(global SwanRSprites auto (array_val 1 aanim::Sprite [
    (index_val
        (rec_val aanim::Sprite [
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
""")]))
]))     

(global pub SwanR auto (rec_val aanim::Object [
        (field_val "swan_r")
        (field_val SwanRSprites)
        (field_val 'W')
        (field_val 3 def_depth)
        (field_val -1.0_r32 def_x_speed)]))

(global DucksRSprites auto (array_val 3 aanim::Sprite [
    (index_val
        (rec_val aanim::Sprite [
             (field_val r"""
      _??????????_??????????_  
,____(')=??,____(')=??,____(')<
 \~~= ')????\~~= ')????\~~= ') 
""")
            (field_val r"""
      g          g          g
wwwwwgcgy  wwwwwgcgy  wwwwwgcgy
 wwww Ww    wwww Ww    wwww Ww
""")]))
    (index_val
        (rec_val aanim::Sprite [
             (field_val r"""
      _??????????_??????????_  
,____(')=??,____(')<??,____(')=
 \~~= ')????\~~= ')????\~~= ') 
""")
        (field_val r"""
      g          g          g
wwwwwgcgy  wwwwwgcgy  wwwwwgcgy
 wwww Ww    wwww Ww    wwww Ww
""")]))
    (index_val
        (rec_val aanim::Sprite [
             (field_val r"""
      _??????????_??????????_  
,____(')<??,____(')=??,____(')=
 \~~= ')????\~~= ')????\~~= ') 
""")
        (field_val r"""
      g          g          g
wwwwwgcgy  wwwwwgcgy  wwwwwgcgy
 wwww Ww    wwww Ww    wwww Ww
""")]))
]))    

(global pub DuckR auto (rec_val aanim::Object [
        (field_val "duck_r1")
        (field_val DucksRSprites)
        (field_val 'W')
        (field_val 3 def_depth)
        (field_val '?' transparent_char)
        (field_val 1.0_r32 def_x_speed)]))



(global DolphinRSprites auto (array_val 2 aanim::Sprite [
    (index_val
        (rec_val aanim::Sprite [
             (field_val r"""
        ,
      __)\_
(\_.-'    a`-.
(/~~````(/~^^`
""")
        (field_val r"""


          W
""")]))
    (index_val
        (rec_val aanim::Sprite [
             (field_val r"""
        ,
(\__  __)\_
(/~.''    a`-.
    ````\)~^^`
""")
        (field_val r"""


          W
""")]))
]))   

(global pub DolphinR auto (rec_val aanim::Object [
        (field_val "dolphin_r")
        (field_val DolphinRSprites)
        (field_val 'b')
        (field_val 3 def_depth)
        (field_val 1.0_r32 def_x_speed)]))


(global DolphinLSprites auto (array_val 2 aanim::Sprite [
    (index_val
        (rec_val aanim::Sprite [
             (field_val r"""
     ,
   _/(__
.-'a    `-._/)
'^^~\)''''~~\)
""")
        (field_val r"""


   W
""")]))
    (index_val
        (rec_val aanim::Sprite [
             (field_val r"""
     ,
   _/(__  __/)
.-'a    ``.~\)
'^^~(/''''
""")
        (field_val r"""


   W
""")]))
]))  


(global pub DolphinL auto (rec_val aanim::Object [
        (field_val "dolphin_r")
        (field_val DolphinLSprites)
        (field_val 'b')
        (field_val 3 def_depth)
        (field_val -1.0_r32 def_x_speed)]))


(global BigFishRSprites auto (array_val 1 aanim::Sprite [
    (index_val
        (rec_val aanim::Sprite [
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
""")]))
]))  

(global pub BigFishR auto (rec_val aanim::Object [
        (field_val "bigfish_r")
        (field_val BigFishRSprites)
        (field_val 'Y')
        (field_val 2 def_depth)
        (field_val 3.0_r32 def_x_speed)]))


(global MonsterRSprites auto (array_val 4 aanim::Sprite [
    (index_val
        (rec_val aanim::Sprite [
            (field_val r"""
                                                          ____
            __??????????????????????????????????????????/   o  \
          /    \????????_?????????????????????_???????/     ____ >
  _??????|  __  |?????/   \????????_????????/   \????|     |
 | \?????|  ||  |????|     |?????/   \?????|     |???|     |
""")
            (field_val r"""

                                                            W



""")]))
   (index_val
        (rec_val aanim::Sprite [
            (field_val r"""
                                                          ____
                                             __?????????/   o  \
             _?????????????????????_???????/    \?????/     ____ >
   _???????/   \????????_????????/   \????|  __  |???|     |
  | \?????|     |?????/   \?????|     |???|  ||  |???|     |
""")
            (field_val r"""

                                                            W



""")]))
   (index_val
        (rec_val aanim::Sprite [
            (field_val r"""
                                                          ____     
                                  __????????????????????/   o  \
 _??????????????????????_???????/    \????????_???????/     ____ >
| \??????????_????????/   \????|  __  |?????/   \????|     |
 \ \???????/   \?????|     |???|  ||  |????|     |???|     |
""")
            (field_val r"""

                                                            W



""")]))
   (index_val
        (rec_val aanim::Sprite [
            (field_val r"""
                                                          ____
                       __???????????????????????????????/   o  \
  _??????????_???????/    \????????_??????????????????/     ____ >
 | \???????/   \????|  __  |?????/   \????????_??????|     |
  \ \?????|     |???|  ||  |????|     |?????/   \????|     |
""")
            (field_val r"""

                                                            W



""")]))
]))  


(global pub MonsterR auto (rec_val aanim::Object [
        (field_val "monster_r")
        (field_val MonsterRSprites)
        (field_val 'G')
        (field_val 5 def_depth)
        (field_val '?' transparent_char)
        (field_val 2.0_r32 def_x_speed)]))


(global ShipRSprites auto (array_val 1 aanim::Sprite [
    (index_val
        (rec_val aanim::Sprite [
            (field_val r"""
     |    |    |
    )_)  )_)  )_)
   )___))___))___)\
  )____)____)_____)\\\
_____|____|____|____\\\\\__
\                   /
""")
            (field_val r"""
     y    y    y

                  w
                   ww
yyyyyyyyyyyyyyyyyyyywwwyy
y                   y
""")]))
]))  


(global pub ShipR auto (rec_val aanim::Object [
        (field_val "ship_r")
        (field_val ShipRSprites)
        (field_val 'W')
        (field_val 7 def_depth)
        (field_val 1.0_r32 def_x_speed)]))


(global SharkRSprites auto (array_val 1 aanim::Sprite [
    (index_val
        (rec_val aanim::Sprite [
            (field_val r"""
                              __
                             ( `\
  ,??????????????????????????)   `\
;' `.????????????????????????(     `\__
 ;   `.?????????????__..---''          `~~~~-._
  `.   `.____...--''                       (b  `--._
    >                     _.-'      .((      ._     )
  .`.-`--...__         .-'     -.___.....-(|/|/|/|/'
 ;.'?????????`. ...----`.___.',,,_______......---'
 '???????????'-'
""")
            (field_val r"""





                                           cR
 
                                          cWWWWWWWW


""")]))
]))  


(global pub SharkR auto (rec_val aanim::Object [
        (field_val "ship_r")
        (field_val SharkRSprites)
        (field_val 'C')
        (field_val 2 def_depth)
        (field_val '?' transparent_char)
        (field_val 2.0_r32 def_x_speed)]))


(global Fish1RSprites auto (array_val 1 aanim::Sprite [
    (index_val
        (rec_val aanim::Sprite [
            (field_val r"""
       \
     ...\..,
\  /'       \
 >=     (  ' >
/  \      / /
    `"'"'/''
""")
            (field_val r"""
       2
     1112111
6  11       1
 66     7  4 5
6  1      3 1
    11111311
""")]))
]))  


(global pub Fish1R auto (rec_val aanim::Object [
        (field_val "fish1_r")
        (field_val Fish1RSprites)
        (field_val 'C')
        (field_val 2 def_depth)]))      
        
        
(fun pub UpdateState [(param s (ptr mut aanim::ObjectState)) (param t r32) (param dt r32)] void :
    (= (-> s x_pos) (+ (-> s x_pos) (* (-> s x_speed) dt)))
    (= (-> s y_pos) (+ (-> s y_pos) (* (-> s y_speed) dt)))
)

(# "eom"))


(module main [] :
(import artwork)

(import aanim)

(import ansi)

(global mut all_objects auto (array_val 100 aanim::ObjectState))


(# "main module with program entry point `main`")
(fun main [(param argc s32) (param argv (ptr (ptr u8)))] s32 :
    (if (< argc 3) :
        (print ["Not enough arguments, need width and height\n"])
        (return 0)
        :)
    (let arg_w (slice u8) (call strz_to_slice [(^ (incp argv 1))]))
    (let arg_h (slice u8) (call strz_to_slice [(^ (incp argv 2))]))
    (let width s32 (as (call str_to_u32 [arg_w]) s32))
    (let height s32 (as (call str_to_u32 [arg_h]) s32))
    (# "100ms per frame" )
    (let ref req TimeSpec (rec_val TimeSpec [(field_val 0) (field_val 100000000)]))
    (let mut ref rem TimeSpec undef)


    (let ref window auto (rec_val aanim::Window [(field_val width) (field_val height)]))
    (let mut curr auto (front mut all_objects))
    (# "")
    (stmt (call aanim::InitObjectState [curr (& artwork::DuckR)]))
    (stmt (call aanim::SetBasics [curr 0.0  0 5]))
    (= curr (incp curr 1))
    (# "")
    (stmt (call aanim::InitObjectState [curr (& artwork::Castle)]))
    (stmt (call aanim::SetBasics [curr 0.0 (- (as width r32) 32) (- (as height r32) 13)]))
    (= curr (incp curr 1))
    (# "")
    (stmt (call aanim::InitObjectState [curr (& artwork::BigFishR)]))
    (stmt (call aanim::SetBasics [curr 0.0 10 10]))
    (= curr (incp curr 1))
    (# "")
    (stmt (call aanim::InitObjectState [curr (& artwork::SwanL)]))
    (stmt (call aanim::SetBasics [curr 0.0 50 1]))
    (= curr (incp curr 1))
    (# "")
    (stmt (call aanim::InitObjectState [curr (& artwork::DolphinL)]))
    (stmt (call aanim::SetBasics [curr 0.0 30 8]))
    (= curr (incp curr 1))
    (# "")
    (stmt (call aanim::InitObjectState [curr (& artwork::MonsterR)]))
    (stmt (call aanim::SetBasics [curr 0.0 30 2]))
    (= curr (incp curr 1))
    (# "")
    (stmt (call aanim::InitObjectState [curr (& artwork::SharkR)]))
    (stmt (call aanim::SetBasics [curr 0.0 30 30]))
    (= curr (incp curr 1))
    (# "")
    (stmt (call aanim::InitObjectState [curr (& artwork::ShipR)]))
    (stmt (call aanim::SetBasics [curr 0.0 50 0]))
    (= curr (incp curr 1))
    (# "")
    (stmt (call aanim::InitObjectState [curr (& artwork::Fish1R)]))
    (stmt (call aanim::SetBasics [curr 0.0 40 40]))
    (= curr (incp curr 1))
    (# "")

     (print [ansi::CURSOR_HIDE])
     (let mut last_t r32 0.0)
     (for t r32 0.0 5.0 0.1 :

        (stmt (call aanim::window_fill [
                (& mut window)
                ' '
                ' ']))
    
        (= curr (front mut all_objects))
        (for i uint 0 9 1 :
            (stmt (call aanim::draw [(& mut window) (incp curr i)]))
        )
        (# "")
        (stmt (call aanim::window_draw [(& window) 'k']))

        (for i uint 0 9 1 :
            (stmt (call artwork::UpdateState [(incp curr i) t (- t last_t)]))
        )
        
        (stmt (call nanosleep [(& req) (& mut rem)]))
        (= last_t t)
    )
    (print [ansi::CURSOR_SHOW])

    (return 0))




(# "eom"))


