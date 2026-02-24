; Ansi Escape Sequences for Terminal Emulation
;
; * https://www.xfree86.org/current/ctlseqs.html")
; * https://gist.github.com/fnky/458719343aabd01cfb17a3a4f7296797
;
module:

pub global CLEAR_ALL span(u8) = "\x1b[2J"

pub global SET_MODE_BOLD span(u8) = "\x1b[1m"

pub global SET_MODE_DIM span(u8) = "\x1b[2m"

pub global SET_MODE_ITALIC span(u8) = "\x1b[3m"

pub global SET_MODE_UNDERLINE span(u8) = "\x1b[4m"

pub global SET_MODE_BLINKING span(u8) = "\x1b[5m"

pub global SET_MODE_INVERSE span(u8) = "\x1b[6m"

pub global SET_MODE_HIDDEN span(u8) = "\x1b[7m"

pub global SET_MODE_STRIKE_THROUGH span(u8) = "\x1b[8m"

; also clears color settings
pub global RESET_MODE_ALL span(u8) = "\x1b[0m"

pub global RESET_MODE_BOLD_OR_DIM span(u8) = "\x1b[22m"

pub global RESET_MODE_ITALIC span(u8) = "\x1b[23m"

pub global RESET_MODE_UNDERLINE span(u8) = "\x1b[24m"

pub global RESET_MODE_BLINKING span(u8) = "\x1b[25m"

pub global RESET_MODE_INVERSE span(u8) = "\x1b[26m"

pub global RESET_MODE_HIDDEN span(u8) = "\x1b[27m"

pub global RESET_MODE_STRIKE_THROUGH span(u8) = "\x1b[28m"

pub global CURSOR_HIDE span(u8) = "\x1b[?25l"

pub global CURSOR_SHOW span(u8) = "\x1b[?25h"

; same escape sequence with "f"
pub macro POS# EXPR_LIST ($x EXPR, $y EXPR) []:
    "\x1b["
    $x
    ";"
    $y
    "H"

pub global QUERY_POS span(u8) = "\x1b[6n"

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
