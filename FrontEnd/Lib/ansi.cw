@doc """Ansi Escape Sequences for Terminal Emulation

* https://www.xfree86.org/current/ctlseqs.html")
* https://gist.github.com/fnky/458719343aabd01cfb17a3a4f7296797
"""
(module ansi [] :

@pub (global CLEAR_ALL auto "\x1b[2J")


@pub (global SET_MODE_BOLD auto "\x1b[1m")


@pub (global SET_MODE_DIM auto "\x1b[2m")


@pub (global SET_MODE_ITALIC auto "\x1b[3m")


@pub (global SET_MODE_UNDERLINE auto "\x1b[4m")


@pub (global SET_MODE_BLINKING auto "\x1b[5m")


@pub (global SET_MODE_INVERSE auto "\x1b[6m")


@pub (global SET_MODE_HIDDEN auto "\x1b[7m")


@pub (global SET_MODE_STRIKE_THROUGH auto "\x1b[8m")


@doc "also clears color settings"
@pub (global RESET_MODE_ALL auto "\x1b[0m")


@pub (global RESET_MODE_BOLD_OR_DIM auto "\x1b[22m")


@pub (global RESET_MODE_ITALIC auto "\x1b[23m")


@pub (global RESET_MODE_UNDERLINE auto "\x1b[24m")


@pub (global RESET_MODE_BLINKING auto "\x1b[25m")


@pub (global RESET_MODE_INVERSE auto "\x1b[26m")


@pub (global RESET_MODE_HIDDEN auto "\x1b[27m")


@pub (global RESET_MODE_STRIKE_THROUGH auto "\x1b[28m")


@pub (global CURSOR_HIDE auto "\x1b[?25l")


@pub (global CURSOR_SHOW auto "\x1b[?25h")


(macro POS# EXPR_LIST [(mparam $x EXPR) (mparam $y EXPR)] [] :
    "\x1b["
    $x
    ";"
    $y
    "f")


@doc "FG"
@pub (global FG_COLOR_BLACK auto "\x1b[38;2;0;0;0m")


@pub (global FG_COLOR_RED auto "\x1b[38;2;205;0;0m")


@pub (global FG_COLOR_GREEN auto "\x1b[38;2;0;205;0m")


@pub (global FG_COLOR_YELLOW auto "\x1b[38;2;205;205;0m")


@pub (global FG_COLOR_BLUE auto "\x1b[38;2;0;0;238m")


@pub (global FG_COLOR_MAGENTA auto "\x1b[38;2;205;0;205m")


@pub (global FG_COLOR_CYAN auto "\x1b[38;2;0;205;205m")


@pub (global FG_COLOR_WHITE auto "\x1b[38;2;229;229;229m")


(macro FG_COLOR# EXPR_LIST [
        (mparam $r EXPR)
        (mparam $g EXPR)
        (mparam $b EXPR)] [] :
    "\x1b[38;2;"
    $r
    ";"
    $g
    ";"
    $b
    "m")


@doc "BG"
@pub (global BG_COLOR_BLACK auto "\x1b[48;2;0;0;0m")


@pub (global BG_COLOR_RED auto "\x1b[48;2;205;0;0m")


@pub (global BG_COLOR_GREEN auto "\x1b[48;2;0;205;0m")


@pub (global BG_COLOR_YELLOW auto "\x1b[48;2;205;205;0m")


@pub (global BG_COLOR_BLUE auto "\x1b[48;2;0;0;238m")


@pub (global BG_COLOR_MAGENTA auto "\x1b[48;2;205;0;205m")


@pub (global BG_COLOR_CYAN auto "\x1b[48;2;0;205;205m")


@pub (global BG_COLOR_WHITE auto "\x1b[48;2;229;229;229m")


(macro BG_COLOR# EXPR_LIST [
        (mparam $r EXPR)
        (mparam $g EXPR)
        (mparam $b EXPR)] [] :
    "\x1b[48;2;"
    $r
    ";"
    $g
    ";"
    $b
    "m")
)
