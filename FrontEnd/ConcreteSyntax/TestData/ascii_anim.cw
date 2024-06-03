-- Ascii Art Animation Module
module aanim:

import ansi

import fmt

-- arbitrary bounds so we can statically allocate maps
global MAX_DIM s32 = 1024

@pub global DEF_ATTR_LOOKUP = "RcRyBgM"

@pub rec Window:
    width s32
    height s32
    char_map [MAX_DIM * MAX_DIM]u8
    attr_map [MAX_DIM * MAX_DIM]u8
    depth_map [MAX_DIM * MAX_DIM]u8

@pub rec Sprite:
    image_map slice(u8)
    color_map slice(u8)

@pub rec Object:
    name slice(u8)
    sprites slice(Sprite)
    def_attr u8
    def_depth u8
    transparent_char u8
    def_x_speed r32
    def_y_speed r32

@pub rec ObjectState:
    obj ^Object
    start_time r32
    x_pos r32
    y_pos r32
    depth u8
    frame uint
    x_speed r32
    y_speed r32
    attr_lookup slice(u8)
    def_attr u8
    -- updated by draw
    visible bool

@pub fun InitObjectState(s ^!ObjectState, o ^Object) void:
    set s^.obj = o
    set s^.attr_lookup = DEF_ATTR_LOOKUP
    set s^.depth = o^.def_depth
    set s^.frame = 0
    set s^.def_attr = o^.def_attr
    set s^.x_speed = o^.def_x_speed
    set s^.y_speed = o^.def_y_speed

@pub fun SetBasics(s ^!ObjectState, start_time r32, x_pos r32, y_pos r32) void:
    set s^.start_time = start_time
    set s^.x_pos = x_pos
    set s^.y_pos = y_pos

fun tolower(c u8) u8:
    return c or 0x20

fun get_style(attr u8) slice(u8):
    return attr < 'a' ? as(ansi::SET_MODE_BOLD, slice(u8)) : as(
            ansi::RESET_MODE_BOLD_OR_DIM, slice(u8))

fun get_fg_color(attr u8) slice(u8):
    let col u8 = tolower(attr)
    cond:
        case col == 'k':
            return ansi::FG_COLOR_BLACK
        case col == 'r':
            return ansi::FG_COLOR_RED
        case col == 'g':
            return ansi::FG_COLOR_GREEN
        case col == 'y':
            return ansi::FG_COLOR_YELLOW
        case col == 'b':
            return ansi::FG_COLOR_BLUE
        case col == 'm':
            return ansi::FG_COLOR_MAGENTA
        case col == 'c':
            return ansi::FG_COLOR_CYAN
        case col == 'w':
            return ansi::FG_COLOR_WHITE
        case true:
            return ""

fun get_bg_color(attr u8) slice(u8):
    let col u8 = tolower(attr)
    cond:
        case col == 'k':
            return ansi::BG_COLOR_BLACK
        case col == 'r':
            return ansi::BG_COLOR_RED
        case col == 'g':
            return ansi::BG_COLOR_GREEN
        case col == 'y':
            return ansi::BG_COLOR_YELLOW
        case col == 'b':
            return ansi::BG_COLOR_BLUE
        case col == 'm':
            return ansi::BG_COLOR_MAGENTA
        case col == 'c':
            return ansi::BG_COLOR_CYAN
        case col == 'w':
            return ansi::BG_COLOR_WHITE
        case true:
            return ""

@pub fun draw(window ^!Window, s ^!ObjectState) void:
    let width = window^.width
    let height = window^.height
    let obj = s^.obj
    let sprite = &obj^.sprites[s^.frame]
    let image_map = sprite^.image_map
    let color_map = sprite^.color_map
    let def_attr = s^.def_attr
    let depth = s^.depth
    let! x s32 = as(s^.x_pos, s32)
    let! y s32 = as(s^.y_pos, s32)
    let! left_side = true
    let! have_color = true
    let! cpos uint = 0
    for ipos = 0, len(image_map), 1:
        -- determine attribute
        let! a u8 = def_attr
        if have_color:
            let cc u8 = color_map[cpos]
            set cpos += 1
            cond:
                case cc == '\n':
                    set have_color = false
                case cc == ' ':
                case cc >= '1' && cc <= '9':
                    set a = s^.attr_lookup[cc - '1']
                case true:
                    set a = cc
        -- determine character
        let c u8 = image_map[ipos]
        if c == '\n':
            set y += 1
            set x = as(s^.x_pos, s32)
            set left_side = true
            -- the end of the color row should have been reached already
            fmt::assert#(!have_color,{"color failure\n"})
            if cpos < len(color_map):
                set have_color = true
            continue
        if c != ' ':
            set left_side = false
        if x < width && y < height && (x >= 0 && y >= 0):
            set s^.visible = true
            let index = y * width + x
            if 0_u8 != window^.depth_map[index]:
                if !left_side && c != obj^.transparent_char:
                    set window^.char_map[index] = c
                    set window^.attr_map[index] = a
        set x += 1

@pub fun window_draw(obj ^Window, bg_col u8) void:
    fmt::print#(get_bg_color(bg_col), ansi::CLEAR_ALL)
    let w = obj^.width
    let h = obj^.height
    -- @ is an invalid attrib
    let! last_attr u8 = '@'
    for x = 0, w, 1:
        let! last_x = MAX_DIM
        for y = 0, h, 1:
            let index = y * w + x
            let c = obj^.char_map[index]
            let a = obj^.attr_map[index]
            if c == ' ':
                continue
            if x != last_x + 1:
                fmt::print#(ansi::POS#(y + 1, x + 1))
            set last_x = x
            if last_attr != a:
                fmt::print#(get_fg_color(a), get_style(a))
            set last_attr = a
            fmt::print#(wrapas(c, fmt::rune))

@pub fun window_fill(obj ^!Window, c u8, a u8) void:
    let size = obj^.width * obj^.height
    for i = 0, size, 1:
        set obj^.char_map[i] = c
        set obj^.attr_map[i] = a
        set obj^.depth_map[i] = 255
