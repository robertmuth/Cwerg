@doc """
* https://github.com/cmatsuoka/asciiquarium
* https://robobunny.com/projects/asciiquarium/
* Artwork by Joan Stark: http://www.geocities.com/SoHo/7373/ (see archive.org copy)"""
(module artwork [] :
(import ./ascii_anim aanim)



@doc """Color codes and xterm rgb values:
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
"""
@pub (global RandomColor auto "RcRyBgM")


(global CastleSprites auto (array_val 1 aanim::Sprite [(index_val (rec_val aanim::Sprite [(field_val r"""
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
""") (field_val r"""
                 RR

               yyy
              y   y
             y     y
            y       y



               yyy
              yy yy
             y y y y
             yyyyyyy
""")]))]))


@pub (global Castle auto (rec_val aanim::Object [
        (field_val "castle")
        (field_val CastleSprites)
        (field_val 'B')
        (field_val 22 def_depth)]))


(global SwanLSprites auto (array_val 1 aanim::Sprite [(index_val (rec_val aanim::Sprite [(field_val r"""
 ___
/,_ \    _,
|/ )/   / |
  //  _/  |
 / ( /   _)
/   `   _/)
\  ~=-   /
""") (field_val r"""

 g
yy
""")]))]))


@pub (global SwanL auto (rec_val aanim::Object [
        (field_val "swan_l")
        (field_val SwanLSprites)
        (field_val 'W')
        (field_val 3 def_depth)
        (field_val -1.0_r32 def_x_speed)]))


(global SwanRSprites auto (array_val 1 aanim::Sprite [(index_val (rec_val aanim::Sprite [(field_val r"""
        ___
 ,_    / _,\
 | \   \( \|
 |  \_  \\\
 (_   \_) \
 (\_   `   \
  \   -=~  /
""") (field_val r"""

          g
          yy
""")]))]))


@pub (global SwanR auto (rec_val aanim::Object [
        (field_val "swan_r")
        (field_val SwanRSprites)
        (field_val 'W')
        (field_val 3 def_depth)
        (field_val -1.0_r32 def_x_speed)]))


(global DucksRSprites auto (array_val 3 aanim::Sprite [
        (index_val (rec_val aanim::Sprite [(field_val r"""
      _??????????_??????????_
,____(')=??,____(')=??,____(')<
 \~~= ')????\~~= ')????\~~= ')
""") (field_val r"""
      g          g          g
wwwwwgcgy  wwwwwgcgy  wwwwwgcgy
 wwww Ww    wwww Ww    wwww Ww
""")]))
        (index_val (rec_val aanim::Sprite [(field_val r"""
      _??????????_??????????_
,____(')=??,____(')<??,____(')=
 \~~= ')????\~~= ')????\~~= ')
""") (field_val r"""
      g          g          g
wwwwwgcgy  wwwwwgcgy  wwwwwgcgy
 wwww Ww    wwww Ww    wwww Ww
""")]))
        (index_val (rec_val aanim::Sprite [(field_val r"""
      _??????????_??????????_
,____(')<??,____(')=??,____(')=
 \~~= ')????\~~= ')????\~~= ')
""") (field_val r"""
      g          g          g
wwwwwgcgy  wwwwwgcgy  wwwwwgcgy
 wwww Ww    wwww Ww    wwww Ww
""")]))]))


@pub (global DuckR auto (rec_val aanim::Object [
        (field_val "duck_r1")
        (field_val DucksRSprites)
        (field_val 'W')
        (field_val 3 def_depth)
        (field_val '?' transparent_char)
        (field_val 1.0_r32 def_x_speed)]))


(global DolphinRSprites auto (array_val 2 aanim::Sprite [(index_val (rec_val aanim::Sprite [(field_val r"""
        ,
      __)\_
(\_.-'    a`-.
(/~~````(/~^^`
""") (field_val r"""


          W
""")])) (index_val (rec_val aanim::Sprite [(field_val r"""
        ,
(\__  __)\_
(/~.''    a`-.
    ````\)~^^`
""") (field_val r"""


          W
""")]))]))


@pub (global DolphinR auto (rec_val aanim::Object [
        (field_val "dolphin_r")
        (field_val DolphinRSprites)
        (field_val 'b')
        (field_val 3 def_depth)
        (field_val 1.0_r32 def_x_speed)]))


(global DolphinLSprites auto (array_val 2 aanim::Sprite [(index_val (rec_val aanim::Sprite [(field_val r"""
     ,
   _/(__
.-'a    `-._/)
'^^~\)''''~~\)
""") (field_val r"""


   W
""")])) (index_val (rec_val aanim::Sprite [(field_val r"""
     ,
   _/(__  __/)
.-'a    ``.~\)
'^^~(/''''
""") (field_val r"""


   W
""")]))]))


@pub (global DolphinL auto (rec_val aanim::Object [
        (field_val "dolphin_r")
        (field_val DolphinLSprites)
        (field_val 'b')
        (field_val 3 def_depth)
        (field_val -1.0_r32 def_x_speed)]))


(global BigFishRSprites auto (array_val 1 aanim::Sprite [(index_val (rec_val aanim::Sprite [(field_val r"""
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
""") (field_val r"""
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
""")]))]))


@pub (global BigFishR auto (rec_val aanim::Object [
        (field_val "bigfish_r")
        (field_val BigFishRSprites)
        (field_val 'Y')
        (field_val 2 def_depth)
        (field_val 3.0_r32 def_x_speed)]))


(global BigFishLSprites auto (array_val 1 aanim::Sprite [(index_val (rec_val aanim::Sprite [(field_val r"""
                           ______
          __.....-----'''''  .-""'
       .-'       .      .  .'
     .'       .     .     :
    : _          .    .   :     ,
 _.' (@)                  :   .' :
(__.       .-'=     .     `..' .'
 "-.     :  ~  =        .     ;
   `. _.'  `-.=  .    .   .'`. `.
     `.   .               :   `. :
       `-.   .     .    .  `.   `
          `.=`.``----....____`.
            `.`.             ""
              '`"``
""") (field_val r"""
                           111111
          11111111111111111  11111
       111       2      2  11
     11       2     2     1
    1 1          2    2   1     1
 111 1W1                  1   11 1
1111       1111     2     1111 11
 111     1  1  1        2     1
   11 111  1111  2    2   1111 11
     11   2               1   11 1
       111   2     2    2  11   1
          111111111111111111111
            1111             11
              11111
""")]))]))


@pub (global BigFishL auto (rec_val aanim::Object [
        (field_val "bigfish_l")
        (field_val BigFishLSprites)
        (field_val 'Y')
        (field_val 2 def_depth)
        (field_val 3.0_r32 def_x_speed)]))


(global MonsterRSprites auto (array_val 4 aanim::Sprite [
        (index_val (rec_val aanim::Sprite [(field_val r"""
                                                          ____
            __??????????????????????????????????????????/   o  \
          /    \????????_?????????????????????_???????/     ____ >
  _??????|  __  |?????/   \????????_????????/   \????|     |
 | \?????|  ||  |????|     |?????/   \?????|     |???|     |
""") (field_val r"""

                                                            W



""")]))
        (index_val (rec_val aanim::Sprite [(field_val r"""
                                                          ____
                                             __?????????/   o  \
             _?????????????????????_???????/    \?????/     ____ >
   _???????/   \????????_????????/   \????|  __  |???|     |
  | \?????|     |?????/   \?????|     |???|  ||  |???|     |
""") (field_val r"""

                                                            W



""")]))
        (index_val (rec_val aanim::Sprite [(field_val r"""
                                                          ____
                                  __????????????????????/   o  \
 _??????????????????????_???????/    \????????_???????/     ____ >
| \??????????_????????/   \????|  __  |?????/   \????|     |
 \ \???????/   \?????|     |???|  ||  |????|     |???|     |
""") (field_val r"""

                                                            W



""")]))
        (index_val (rec_val aanim::Sprite [(field_val r"""
                                                          ____
                       __???????????????????????????????/   o  \
  _??????????_???????/    \????????_??????????????????/     ____ >
 | \???????/   \????|  __  |?????/   \????????_??????|     |
  \ \?????|     |???|  ||  |????|     |?????/   \????|     |
""") (field_val r"""

                                                            W



""")]))]))


@pub (global MonsterR auto (rec_val aanim::Object [
        (field_val "monster_r")
        (field_val MonsterRSprites)
        (field_val 'G')
        (field_val 5 def_depth)
        (field_val '?' transparent_char)
        (field_val 2.0_r32 def_x_speed)]))


(global ShipRSprites auto (array_val 1 aanim::Sprite [(index_val (rec_val aanim::Sprite [(field_val r"""
     |    |    |
    )_)  )_)  )_)
   )___))___))___)\
  )____)____)_____)\\\
_____|____|____|____\\\\\__
\                   /
""") (field_val r"""
     y    y    y

                  w
                   ww
yyyyyyyyyyyyyyyyyyyywwwyy
y                   y
""")]))]))


@pub (global ShipR auto (rec_val aanim::Object [
        (field_val "ship_r")
        (field_val ShipRSprites)
        (field_val 'W')
        (field_val 7 def_depth)
        (field_val 1.0_r32 def_x_speed)]))


(global SharkRSprites auto (array_val 1 aanim::Sprite [(index_val (rec_val aanim::Sprite [(field_val r"""
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
""") (field_val r"""





                                           cR

                                          cWWWWWWWW


""")]))]))


@pub (global SharkR auto (rec_val aanim::Object [
        (field_val "ship_r")
        (field_val SharkRSprites)
        (field_val 'C')
        (field_val 2 def_depth)
        (field_val '?' transparent_char)
        (field_val 2.0_r32 def_x_speed)]))


(global Fish1RSprites auto (array_val 1 aanim::Sprite [(index_val (rec_val aanim::Sprite [(field_val r"""
       \
     ...\..,
\  /'       \
 >=     (  ' >
/  \      / /
    `"'"'/''
""") (field_val r"""
       2
     1112111
6  11       1
 66     7  4 5
6  1      3 1
    11111311
""")]))]))


@pub (global Fish1R auto (rec_val aanim::Object [
        (field_val "fish1_r")
        (field_val Fish1RSprites)
        (field_val 'C')
        (field_val 2 def_depth)]))


@pub (fun UpdateState [
        (param s (ptr! aanim::ObjectState))
        (param t r32)
        (param dt r32)] void :
    (= (-> s x_pos) (+ (-> s x_pos) (* (-> s x_speed) dt)))
    (= (-> s y_pos) (+ (-> s y_pos) (* (-> s y_speed) dt)))
    (+= (-> s frame) 1)
    (if (>= (-> s frame) (len (-> (-> s obj) sprites))) :
        (= (-> s frame) 0)
        :))

)
