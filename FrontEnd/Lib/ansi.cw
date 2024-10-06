-- Ansi Escape Sequences for Terminal Emulation
-- 
-- * https://www.xfree86.org/current/ctlseqs.html")
-- * https://gist.github.com/fnky/458719343aabd01cfb17a3a4f7296797
-- 
module:

pub global CLEAR_ALL = "\x1b[2J"

pub global SET_MODE_BOLD = "\x1b[1m"

pub global SET_MODE_DIM = "\x1b[2m"

pub global SET_MODE_ITALIC = "\x1b[3m"

pub global SET_MODE_UNDERLINE = "\x1b[4m"

pub global SET_MODE_BLINKING = "\x1b[5m"

pub global SET_MODE_INVERSE = "\x1b[6m"

pub global SET_MODE_HIDDEN = "\x1b[7m"

pub global SET_MODE_STRIKE_THROUGH = "\x1b[8m"

-- also clears color settings
pub global RESET_MODE_ALL = "\x1b[0m"

pub global RESET_MODE_BOLD_OR_DIM = "\x1b[22m"

pub global RESET_MODE_ITALIC = "\x1b[23m"

pub global RESET_MODE_UNDERLINE = "\x1b[24m"

pub global RESET_MODE_BLINKING = "\x1b[25m"

pub global RESET_MODE_INVERSE = "\x1b[26m"

pub global RESET_MODE_HIDDEN = "\x1b[27m"

pub global RESET_MODE_STRIKE_THROUGH = "\x1b[28m"

pub global CURSOR_HIDE = "\x1b[?25l"

pub global CURSOR_SHOW = "\x1b[?25h"

macro POS# EXPR_LIST($x EXPR, $y EXPR)[]:
    "\x1b[" 
    $x 
    ";" 
    $y 
    "f" 

-- Foreground Color
pub global FG_COLOR_BLACK = "\x1b[38;2;0;0;0m"

pub global FG_COLOR_RED = "\x1b[38;2;205;0;0m"

pub global FG_COLOR_GREEN = "\x1b[38;2;0;205;0m"

pub global FG_COLOR_YELLOW = "\x1b[38;2;205;205;0m"

pub global FG_COLOR_BLUE = "\x1b[38;2;0;0;238m"

pub global FG_COLOR_MAGENTA = "\x1b[38;2;205;0;205m"

pub global FG_COLOR_CYAN = "\x1b[38;2;0;205;205m"

pub global FG_COLOR_WHITE = "\x1b[38;2;229;229;229m"

macro FG_COLOR# EXPR_LIST($r EXPR, $g EXPR, $b EXPR)[]:
    "\x1b[38;2;" 
    $r 
    ";" 
    $g 
    ";" 
    $b 
    "m" 

-- Background Color
pub global BG_COLOR_BLACK = "\x1b[48;2;0;0;0m"

pub global BG_COLOR_RED = "\x1b[48;2;205;0;0m"

pub global BG_COLOR_GREEN = "\x1b[48;2;0;205;0m"

pub global BG_COLOR_YELLOW = "\x1b[48;2;205;205;0m"

pub global BG_COLOR_BLUE = "\x1b[48;2;0;0;238m"

pub global BG_COLOR_MAGENTA = "\x1b[48;2;205;0;205m"

pub global BG_COLOR_CYAN = "\x1b[48;2;0;205;205m"

pub global BG_COLOR_WHITE = "\x1b[48;2;229;229;229m"

macro BG_COLOR# EXPR_LIST($r EXPR, $g EXPR, $b EXPR)[]:
    "\x1b[48;2;" 
    $r 
    ";" 
    $g 
    ";" 
    $b 
    "m" 
