-- test helpers macros
--
-- This intentionally does not import the fmt module to keep
-- the footprint/dependencies small.
-- (We may change our mind on this.)
--
module:

import os

macro SysPrint# STMT_LIST($msg EXPR)[$msg_eval]:
    mlet $msg_eval span(u8) = $msg
    do os::write(unwrap(os::Stdout), front($msg_eval), len($msg_eval))

pub macro Success# STMT()[]:
    SysPrint#("OK\n")

-- The two scalar arguments must be the same
--
-- Both must have derivable types as we use `auto`
pub macro AssertEq# STMT_LIST($e_expr EXPR, $a_expr EXPR)[$e_val, $a_val]:
    mlet $e_val = $e_expr
    mlet $a_val = $a_expr
    if $e_val != $a_val:
        SysPrint#("AssertEq failed: ")
        SysPrint#(stringify($e_expr))
        SysPrint#(" VS ")
        SysPrint#(stringify($a_expr))
        SysPrint#("\n")
        trap

-- The two scalar arguments must be the same
--
-- Both must have derivable types as we use `auto`
pub macro AssertNe# STMT_LIST($e_expr EXPR, $a_expr EXPR)[$e_val, $a_val]:
    mlet $e_val = $e_expr
    mlet $a_val = $a_expr
    if $e_val == $a_val:
        SysPrint#("AssertNe failed: ")
        SysPrint#(stringify($e_expr))
        SysPrint#(" VS ")
        SysPrint#(stringify($a_expr))
        SysPrint#("\n")
        trap

-- First argument must have the type denoted by the second
pub macro AssertIs# STMT_LIST($expr EXPR, $type TYPE)[]:
    if is($expr, $type):
    else:
        SysPrint#("AssertIs failed: ")
        SysPrint#(stringify(type_of($expr)))
        SysPrint#(" VS ")
        SysPrint#(stringify($type))
        SysPrint#("\n")
        trap

-- The two arguments must type derivable
pub macro AssertSliceEq# STMT_LIST($e_expr EXPR, $a_expr EXPR)[
        $e_val, $a_val, $i]:
    mlet $e_val = $e_expr
    mlet $a_val = $a_expr
    AssertEq#(len($e_val), len($a_val))
    for $i = 0, len($a_val), 1:
        AssertEq#(pinc(front($e_val), $i)^, pinc(front($a_val), $i)^)

-- The first two arguments must derivable types as we use `auto`
pub macro AssertApproxEq# STMT_LIST($e_expr EXPR, $a_expr EXPR, $epsilon EXPR)[
        $e_val, $a_val]:
    mlet $e_val = $e_expr
    mlet $a_val = $a_expr
    if abs($e_val - $a_val) >= $epsilon:
        SysPrint#("AssertApproxEq failed: ")
        SysPrint#(stringify($e_expr))
        SysPrint#(" VS ")
        SysPrint#(stringify($a_expr))
        SysPrint#("\n")
        trap

pub macro AssertEqR64# STMT_LIST($e_expr EXPR, $a_expr EXPR)[$e_val, $a_val]:
    mlet $e_val r64 = $e_expr
    mlet $a_val r64 = $a_expr
    if bitwise_as($e_val, u64) != bitwise_as($a_val, u64):
        SysPrint#("AssertEq failed: ")
        SysPrint#(stringify($e_expr))
        SysPrint#(" VS ")
        SysPrint#(stringify($a_expr))
        SysPrint#("\n")
        trap

pub macro AssertNeR64# STMT_LIST($e_expr EXPR, $a_expr EXPR)[$e_val, $a_val]:
    mlet $e_val r64 = $e_expr
    mlet $a_val r64 = $a_expr
    if bitwise_as($e_val, u64) == bitwise_as($a_val, u64):
        SysPrint#("AssertEq failed: ")
        SysPrint#(stringify($e_expr))
        SysPrint#(" VS ")
        SysPrint#(stringify($a_expr))
        SysPrint#("\n")
        trap

-- The first two arguments must type derivable
pub macro AssertSliceApproxEq# STMT_LIST($e_expr EXPR, $a_expr EXPR, $epsilon EXPR)[
        $e_val, $a_val, $i]:
    mlet $e_val = $e_expr
    mlet $a_val = $a_expr
    AssertEq#(len($e_val), len($a_val))
    for $i = 0, len($a_val), 1:
        AssertApproxEq#(
                pinc(front($e_val), $i)^, pinc(front($a_val), $i)^, $epsilon)

--
pub macro AssertTrue# STMT_LIST($e_expr EXPR)[]:
    if $e_expr:
    else:
        SysPrint#("AssertTrue failed: ")
        SysPrint#(stringify($e_expr))
        SysPrint#("\n")
        trap

--
pub macro AssertFalse# STMT_LIST($e_expr EXPR)[]:
    if $e_expr:
        SysPrint#("AssertFalse failed: ")
        SysPrint#(stringify($e_expr))
        SysPrint#("\n")
        trap

--
pub macro AssertUnreachable# STMT_LIST()[]:
    SysPrint#("AssertUnreachable\n")
    trap
