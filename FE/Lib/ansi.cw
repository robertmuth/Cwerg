; Ansi Escape Sequences for Terminal Emulation
;
; * https://www.xfree86.org/current/ctlseqs.html")
; * https://gist.github.com/fnky/458719343aabd01cfb17a3a4f7296797
;
module:

pub global CLEAR_ALL span(u8) = "\x1b[2J"

;
pub global CURSOR_HIDE span(u8) = "\x1b[?25l"

pub global CURSOR_SHOW span(u8) = "\x1b[?25h"



; SGR (Select Graphic Rendition) sequences look like:
; SGR_START attr1 ; attr2 ; ... ; attrN SGR_END but without any whitespace

pub global SGR_START span(u8) = "\x1b["
pub global SGR_END span(u8) = "m"

pub global SGR_RESET_ALL = "0"

pub global SGR_BOLD = "1"
pub global SGR_DIM = "2"
pub global SGR_ITALIC = "3"
pub global SGR_UNDERLINE = "4"
pub global SGR_BLINKING = "5"
pub global SGR_INVERSE = "6"
pub global SGR_HIDDEN = "7"
pub global SGR_STRIKE_THROUGH = "8"

pub global SGR_RESET_BOLD_AND_DIM = "22"
pub global SGR_RESET_ITALIC = "23"
pub global SGR_RESET_UNDERLINE = "24"
pub global SGR_RESET_BLINKING = "25"
pub global SGR_RESET_INVERSE = "26"
pub global SGR_RESET_HIDDEN = "27"
pub global SGR_RESET_STRIKE_THROUGH = "28"

pub global SGR_FG_BLACK = "30"
pub global SGR_FG_RED = "31"
pub global SGR_FG_GREEN = "32"
pub global SGR_FG_YELLOW = "33"
pub global SGR_FG_BLUE = "34"
pub global SGR_FG_MAGENTA = "35"
pub global SGR_FG_CYAN = "36"
pub global SGR_FG_WHITE = "37"
pub global SGR_FG_EXTENDED = "38"
pub global SGR_FG_DEFAULT = "39"
pub global SGR_FG_BRIGHT_BLACK = "90"
pub global SGR_FG_BRIGHT_RED = "91"
pub global SGR_FG_BRIGHT_GREEN = "92"
pub global SGR_FG_BRIGHT_YELLOW = "93"
pub global SGR_FG_BRIGHT_BLUE = "94"
pub global SGR_FG_BRIGHT_MAGENTA = "95"
pub global SGR_FG_BRIGHT_CYAN = "96"
pub global SGR_FG_BRIGHT_WHITE = "97"

pub global SGR_BG_BLACK = "40"
pub global SGR_BG_RED = "41"
pub global SGR_BG_GREEN = "42"
pub global SGR_BG_YELLOW = "43"
pub global SGR_BG_BLUE = "44"
pub global SGR_BG_MAGENTA = "45"
pub global SGR_BG_CYAN = "46"
pub global SGR_BG_WHITE = "47"
pub global SGR_BG_EXTENDED = "48"
pub global SGR_BG_DEFAULT = "49"
pub global SGR_BG_BRIGHT_BLACK = "100"
pub global SGR_BG_BRIGHT_RED = "101"
pub global SGR_BG_BRIGHT_GREEN = "102"
pub global SGR_BG_BRIGHT_YELLOW = "1003"
pub global SGR_BG_BRIGHT_BLUE = "1004"
pub global SGR_BG_BRIGHT_MAGENTA = "105"
pub global SGR_BG_BRIGHT_CYAN = "106"
pub global SGR_BG_BRIGHT_WHITE = "107"




; same escape sequence with "f"
pub macro POS# EXPR_LIST ($x EXPR, $y EXPR) []:
    "\x1b["
    $x
    ";"
    $y
    "H"


; OBSOLETEish STUFF Below
pub global SET_MODE_BOLD span(u8) = "\x1b[1m"
pub global RESET_MODE_BOLD_OR_DIM span(u8) = "\x1b[22m"

; Foreground Color
pub global FG_COLOR_BLACK span(u8) = "\x1b[38;2;0;0;0m"
pub global FG_COLOR_RED span(u8) = "\x1b[38;2;205;0;0m"
pub global FG_COLOR_GREEN span(u8) = "\x1b[38;2;0;205;0m"
pub global FG_COLOR_YELLOW span(u8) = "\x1b[38;2;205;205;0m"
pub global FG_COLOR_BLUE span(u8) = "\x1b[38;2;0;0;238m"
pub global FG_COLOR_MAGENTA span(u8) = "\x1b[38;2;205;0;205m"
pub global FG_COLOR_CYAN span(u8) = "\x1b[38;2;0;205;205m"
pub global FG_COLOR_WHITE span(u8) = "\x1b[38;2;229;229;229m"

macro FG_COLOR# EXPR_LIST ($r EXPR, $g EXPR, $b EXPR) []:
    "\x1b[38;2;"
    $r
    ";"
    $g
    ";"
    $b
    "m"

; Background Color
pub global BG_COLOR_BLACK span(u8) = "\x1b[48;2;0;0;0m"
pub global BG_COLOR_RED span(u8) = "\x1b[48;2;205;0;0m"
pub global BG_COLOR_GREEN span(u8) = "\x1b[48;2;0;205;0m"
pub global BG_COLOR_YELLOW span(u8) = "\x1b[48;2;205;205;0m"
pub global BG_COLOR_BLUE span(u8) = "\x1b[48;2;0;0;238m"
pub global BG_COLOR_MAGENTA span(u8) = "\x1b[48;2;205;0;205m"
pub global BG_COLOR_CYAN span(u8) = "\x1b[48;2;0;205;205m"
pub global BG_COLOR_WHITE span(u8) = "\x1b[48;2;229;229;229m"
macro BG_COLOR# EXPR_LIST ($r EXPR, $g EXPR, $b EXPR) []:
    "\x1b[48;2;"
    $r
    ";"
    $g
    ";"
    $b
    "m"

; Light
; ┌┬┐
; ├┼┤
; └┴┘
; ─│
;
pub global BOX_COMPONENTS_LIGHT = {[11]u32:
    0x250c, 0x252c, 0x2510,
    0x251c, 0x253c, 0x2524,
    0x2514, 0x2534, 0x2518,
    0x2500, 0x2502}

; Heavy
; ┌┬┐
; ├┼┤
; └┴┘
; ━┃

pub global BOX_COMPONENTS_HEAVY = {[11]u32:
    0x250f, 0x2533, 0x2513,
    0x2523, 0x254b, 0x252b,
    0x2517, 0x253b, 0x251b,
    0x2501, 0x2503}

; Double
; ╔═╦═╗
; ╠═╬═╣
; ╚═╩═╝
;  ═║

pub global BOX_COMPONENTS_DOUBLE = {[11]u32:
    0x2554, 0x2566, 0x2557,
    0x2560, 0x256c, 0x2563,
    0x255a, 0x2569, 0x255d,
    0x2550, 0x2551}
