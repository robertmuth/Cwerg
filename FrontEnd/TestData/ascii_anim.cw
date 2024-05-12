@doc "Ascii Art Animation Module"
(module aanim [] :
(import ansi)

(import fmt)


@doc "arbitrary bounds so we can statically allocate maps"
(global MAX_DIM s32 1024)


@pub (global DEF_ATTR_LOOKUP auto "RcRyBgM")


@pub (defrec Window :
    (field width s32)
    (field height s32)
    (field char_map (array (* MAX_DIM MAX_DIM) u8))
    (field attr_map (array (* MAX_DIM MAX_DIM) u8))
    (field depth_map (array (* MAX_DIM MAX_DIM) u8)))


@pub (defrec Sprite :
    (field image_map (slice u8))
    (field color_map (slice u8)))


@pub (defrec Object :
    (field name (slice u8))
    (field sprites (slice Sprite))
    (field def_attr u8)
    (field def_depth u8)
    (field transparent_char u8)
    (field def_x_speed r32)
    (field def_y_speed r32))


@pub (defrec ObjectState :
    (field obj (ptr Object))
    (field start_time r32)
    (field x_pos r32)
    (field y_pos r32)
    (field depth u8)
    (field frame uint)
    (field x_speed r32)
    (field y_speed r32)
    (field attr_lookup (slice u8))
    (field def_attr u8)
    @doc "updated by draw"
    (field visible bool))


@pub (fun InitObjectState [(param s (ptr! ObjectState)) (param o (ptr Object))] void :
    (= (^. s obj) o)
    (= (^. s attr_lookup) DEF_ATTR_LOOKUP)
    (= (^. s depth) (^. o def_depth))
    (= (^. s frame) 0)
    (= (^. s def_attr) (^. o def_attr))
    (= (^. s x_speed) (^. o def_x_speed))
    (= (^. s y_speed) (^. o def_y_speed)))


@pub (fun SetBasics [
        (param s (ptr! ObjectState))
        (param start_time r32)
        (param x_pos r32)
        (param y_pos r32)] void :
    (= (^. s start_time) start_time)
    (= (^. s x_pos) x_pos)
    (= (^. s y_pos) y_pos))


(fun tolower [(param c u8)] u8 :
    (return (or c 0x20)))


(fun get_style [(param attr u8)] (slice u8) :
    (return (? (< attr 'a') (as ansi::SET_MODE_BOLD (slice u8)) (as ansi::RESET_MODE_BOLD_OR_DIM (slice u8)))))


(fun get_fg_color [(param attr u8)] (slice u8) :
    (let col u8 (tolower [attr]))
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
    (let col u8 (tolower [attr]))
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


@pub (fun draw [(param window (ptr! Window)) (param s (ptr! ObjectState))] void :
    (let width auto (^. window width))
    (let height auto (^. window height))
    (let obj auto (^. s obj))
    (let sprite auto (& (at (^. obj sprites) (^. s frame))))
    (let image_map auto (^. sprite image_map))
    (let color_map auto (^. sprite color_map))
    (let def_attr auto (^. s def_attr))
    (let depth auto (^. s depth))
    (let! x s32 (as (^. s x_pos) s32))
    (let! y s32 (as (^. s y_pos) s32))
    (let! left_side auto true)
    (let! have_color auto true)
    (let! cpos uint 0)
    (for ipos 0 (len image_map) 1 :
        @doc "determine attribute"
        (let! a u8 def_attr)
        (if have_color :
            (let cc u8 (at color_map cpos))
            (+= cpos 1)
            (cond :
                (case (== cc '\n') :
                    (= have_color false))
                (case (== cc ' ') :)
                (case (&& (>= cc '1') (<= cc '9')) :
                    (= a (at (^. s attr_lookup) (- cc '1'))))
                (case true :
                    (= a cc)))
         :)
        @doc "determine character"
        (let c u8 (at image_map ipos))
        (if (== c '\n') :
            (+= y 1)
            (= x (as (^. s x_pos) s32))
            (= left_side true)
            @doc "the end of the color row should have been reached already"
            (fmt::assert# (! have_color) ["color failure\n"])
            (if (< cpos (len color_map)) :
                (= have_color true)
             :)
            (continue)
         :)
        (if (!= c ' ') :
            (= left_side false)
         :)
        (if (&& (&& (< x width) (< y height)) (&& (>= x 0) (>= y 0))) :
            (= (^. s visible) true)
            (let index auto (+ (* y width) x))
            (if (!= 0_u8 (at (^. window depth_map) index)) :
                (if (&& (! left_side) (!= c (^. obj transparent_char))) :
                    (= (at (^. window char_map) index) c)
                    (= (at (^. window attr_map) index) a)
                 :)
             :)
         :)
        (+= x 1)))


@pub (fun window_draw [(param obj (ptr Window)) (param bg_col u8)] void :
    (fmt::print# (get_bg_color [bg_col]) ansi::CLEAR_ALL)
    (let w auto (^. obj width))
    (let h auto (^. obj height))
    @doc "@ is an invalid attrib"
    (let! last_attr u8 '@')
    (for x 0 w 1 :
        (let! last_x auto MAX_DIM)
        (for y 0 h 1 :
            (let index auto (+ (* y w) x))
            (let c auto (at (^. obj char_map) index))
            (let a auto (at (^. obj attr_map) index))
            (if (== c ' ') :
                (continue)
             :)
            (if (!= x (+ last_x 1)) :
                (fmt::print# (ansi::POS# (+ y 1) (+ x 1)))
             :)
            (= last_x x)
            (if (!= last_attr a) :
                (fmt::print# (get_fg_color [a]) (get_style [a]))
             :)
            (= last_attr a)
            (fmt::print# (wrap c fmt::rune)))))


@pub (fun window_fill [
        (param obj (ptr! Window))
        (param c u8)
        (param a u8)] void :
    (let size auto (* (^. obj width) (^. obj height)))
    (for i 0 size 1 :
        (= (at (^. obj char_map) i) c)
        (= (at (^. obj attr_map) i) a)
        (= (at (^. obj depth_map) i) 255)))
)

