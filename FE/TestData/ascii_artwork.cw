;
; * https://github.com/cmatsuoka/asciiquarium
; * https://robobunny.com/projects/asciiquarium/
; * Artwork by Joan Stark: http://www.geocities.com/SoHo/7373/ (see archive.org copy)
module:

import aanim = "./ascii_anim"

; Color codes and xterm rgb values:
; k  black    0,0,0
; r  red      205,0, 0
; g  green    0,205,0
; y  yellow   205,205,0
; b  blue     0,0,238
; m  magenta  205,0,205
; c  cyan     0,205,205
; w  white    229,229,229
; t  translucent
;
;
; Fish body parts:
; 1: body
; 2: dorsal fin
; 3: flippers
; 4: eye
; 5: mouth
; 6: tailfin
; 7: gills
;
pub global RandomColor = "RcRyBgM"

ref global CastleSprites = {[1]aanim\Sprite:
                        {:
                         r"""
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
"""
                         ,
                         r"""
                 RR

               yyy
              y   y
             y     y
            y       y



               yyy
              yy yy
             y y y y
             yyyyyyy
"""
                         }}

ref pub global Castle = {aanim\Object: "castle", CastleSprites, 'B', def_depth = 22
                     }

global SwanLSprites = {[1]aanim\Sprite:
                       {:
                        r"""
 ___
/,_ \    _,
|/ )/   / |
  //  _/  |
 / ( /   _)
/   `   _/)
\  ~=-   /
"""
                        , r"""

 g
yy
"""}}

ref pub global SwanL = {aanim\Object: "swan_l", SwanLSprites, 'W', def_depth = 3,
                    def_x_speed = -1.0_r32}

global SwanRSprites = {[1]aanim\Sprite:
                       {:
                        r"""
        ___
 ,_    / _,\
 | \   \( \|
 |  \_  \\\
 (_   \_) \
 (\_   `   \
  \   -=~  /
"""
                        , r"""

          g
          yy
"""}}

ref pub global SwanR = {aanim\Object: "swan_r", SwanRSprites, 'W', def_depth = 3,
                    def_x_speed = -1.0_r32}

global DucksRSprites = {[3]aanim\Sprite:
                        {:
                         r"""
      _??????????_??????????_
,____(')=??,____(')=??,____(')<
 \~~= ')????\~~= ')????\~~= ')
"""
                         ,
                         r"""
      g          g          g
wwwwwgcgy  wwwwwgcgy  wwwwwgcgy
 wwww Ww    wwww Ww    wwww Ww
"""
                         },
                        {:
                         r"""
      _??????????_??????????_
,____(')=??,____(')<??,____(')=
 \~~= ')????\~~= ')????\~~= ')
"""
                         ,
                         r"""
      g          g          g
wwwwwgcgy  wwwwwgcgy  wwwwwgcgy
 wwww Ww    wwww Ww    wwww Ww
"""
                         },
                        {:
                         r"""
      _??????????_??????????_
,____(')<??,____(')=??,____(')=
 \~~= ')????\~~= ')????\~~= ')
"""
                         ,
                         r"""
      g          g          g
wwwwwgcgy  wwwwwgcgy  wwwwwgcgy
 wwww Ww    wwww Ww    wwww Ww
"""
                         }}

ref pub global DuckR = {aanim\Object: "duck_r1", DucksRSprites, 'W', def_depth = 3,
                    transparent_char = '?', def_x_speed = 1.0_r32}

global DolphinRSprites = {[2]aanim\Sprite:
                          {:
                           r"""
        ,
      __)\_
(\_.-'    a`-.
(/~~````(/~^^`
"""
                           , r"""


          W
"""},
                          {:
                           r"""
        ,
(\__  __)\_
(/~.''    a`-.
    ````\)~^^`
"""
                           , r"""


          W
"""}}

ref pub global DolphinR = {aanim\Object: "dolphin_r", DolphinRSprites, 'b',
                       def_depth = 3, def_x_speed = 1.0_r32}

global DolphinLSprites = {[2]aanim\Sprite:
                          {:
                           r"""
     ,
   _/(__
.-'a    `-._/)
'^^~\)''''~~\)
"""
                           , r"""


   W
"""},
                          {:
                           r"""
     ,
   _/(__  __/)
.-'a    ``.~\)
'^^~(/''''
"""
                           , r"""


   W
"""}}

ref pub global DolphinL = {aanim\Object: "dolphin_r", DolphinLSprites, 'b',
                       def_depth = 3, def_x_speed = -1.0_r32}

global BigFishRSprites = {[1]aanim\Sprite:
                          {:
                           r"""
 ______
`""-.  `````-----.....__
     `.  .      .       `-.
       :     .     .       `.
 ,     :   .    .          _ :
: `.   :                  (@) `._
 `. `..'     .     =`-.       .__)
   &&     .        =  ~  :     .-"
 .' .'`.   .    .  =.-'  `._ .'
: .'   :               .   .'
 '   .'  .    .     .   .-'
   .'____....----''.'=.'
   ""             .'.'
               ''"'`
"""
                           ,
                           r"""
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
"""
                           }}

ref pub global BigFishR = {aanim\Object: "bigfish_r", BigFishRSprites, 'Y',
                       def_depth = 2, def_x_speed = 3.0_r32}

global BigFishLSprites = {[1]aanim\Sprite:
                          {:
                           r"""
                           ______
          __.....-----'''''  .-""'
       .-'       .      .  .'
     .'       .     .     :
    : _          .    .   :     ,
 _.' (@)                  :   .' :
(__.       .-'=     .     `..' .'
 "-.     :  ~  =        .     &&
   `. _.'  `-.=  .    .   .'`. `.
     `.   .               :   `. :
       `-.   .     .    .  `.   `
          `.=`.``----....____`.
            `.`.             ""
              '`"``
"""
                           ,
                           r"""
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
"""
                           }}

ref pub global BigFishL = {aanim\Object: "bigfish_l", BigFishLSprites, 'Y',
                       def_depth = 2, def_x_speed = 3.0_r32}

global MonsterRSprites = {[4]aanim\Sprite:
                          {:
                           r"""
                                                          ____
            __??????????????????????????????????????????/   o  \
          /    \????????_?????????????????????_???????/     ____ >
  _??????|  __  |?????/   \????????_????????/   \????|     |
 | \?????|  ||  |????|     |?????/   \?????|     |???|     |
"""
                           ,
                           r"""

                                                            W



"""
                           },
                          {:
                           r"""
                                                          ____
                                             __?????????/   o  \
             _?????????????????????_???????/    \?????/     ____ >
   _???????/   \????????_????????/   \????|  __  |???|     |
  | \?????|     |?????/   \?????|     |???|  ||  |???|     |
"""
                           ,
                           r"""

                                                            W



"""
                           },
                          {:
                           r"""
                                                          ____
                                  __????????????????????/   o  \
 _??????????????????????_???????/    \????????_???????/     ____ >
| \??????????_????????/   \????|  __  |?????/   \????|     |
 \ \???????/   \?????|     |???|  ||  |????|     |???|     |
"""
                           ,
                           r"""

                                                            W



"""
                           },
                          {:
                           r"""
                                                          ____
                       __???????????????????????????????/   o  \
  _??????????_???????/    \????????_??????????????????/     ____ >
 | \???????/   \????|  __  |?????/   \????????_??????|     |
  \ \?????|     |???|  ||  |????|     |?????/   \????|     |
"""
                           ,
                           r"""

                                                            W



"""
                           }}

ref pub global MonsterR = {aanim\Object: "monster_r", MonsterRSprites, 'G',
                       def_depth = 5, transparent_char = '?',
                       def_x_speed = 2.0_r32}

global ShipRSprites = {[1]aanim\Sprite:
                       {:
                        r"""
     |    |    |
    )_)  )_)  )_)
   )___))___))___)\
  )____)____)_____)\\\
_____|____|____|____\\\\\__
\                   /
"""
                        ,
                        r"""
     y    y    y

                  w
                   ww
yyyyyyyyyyyyyyyyyyyywwwyy
y                   y
"""
                        }}

ref pub global ShipR = {aanim\Object: "ship_r", ShipRSprites, 'W', def_depth = 7,
                    def_x_speed = 1.0_r32}

global SharkRSprites = {[1]aanim\Sprite:
                        {:
                         r"""
                              __
                             ( `\
  ,??????????????????????????)   `\
&&' `.????????????????????????(     `\__
 &&   `.?????????????__..---''          `~~~~-._
  `.   `.____...--''                       (b  `--._
    >                     _.-'      .((      ._     )
  .`.-`--...__         .-'     -.___.....-(|/|/|/|/'
 &&.'?????????`. ...----`.___.',,,_______......---'
 '???????????'-'
"""
                         ,
                         r"""





                                           cR

                                          cWWWWWWWW


"""
                         }}

ref pub global SharkR = {aanim\Object: "ship_r", SharkRSprites, 'C', def_depth = 2,
                     transparent_char = '?', def_x_speed = 2.0_r32}

global Fish1RSprites = {[1]aanim\Sprite:
                        {:
                         r"""
       \
     ...\..,
\  /'       \
 >=     (  ' >
/  \      / /
    `"'"'/''
"""
                         ,
                         r"""
       2
     1112111
6  11       1
 66     7  4 5
6  1      3 1
    11111311
"""
                         }}

ref pub global Fish1R = {aanim\Object: "fish1_r", Fish1RSprites, 'C', def_depth = 2
                     }

pub fun UpdateState(s ^!aanim\ObjectState, t r32, dt r32) void:
    set s^.x_pos = s^.x_pos + s^.x_speed * dt
    set s^.y_pos = s^.y_pos + s^.y_speed * dt
    set s^.frame += 1
    if s^.frame >= len(s^.obj^.sprites):
        set s^.frame = 0
