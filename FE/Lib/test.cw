-- test helpers macros
--
-- This intentionally does not import the fmt module to keep
-- the footprint/dependencies small.
-- (We may change our mind on this.)
--
module:

import os
import cmp

macro SysPrint# STMT_LIST($msg EXPR)[$msg_eval]:
    mlet $msg_eval span(u8) = $msg
    do os::write(unwrap(os::Stdout), front($msg_eval), len($msg_eval))

pub macro Success# STMT()[]:
    SysPrint#("OK\n")

macro AssertCommon# STMT_LIST($name EXPR, $e_expr EXPR, $a_expr EXPR)[
        $e_val, $a_val]:
    SysPrint#($name)
    SysPrint#(" failed in ")
    SysPrint#(srcloc($e_expr))
    SysPrint#(": ")
    SysPrint#(stringify($e_expr))
    SysPrint#(" VS ")
    SysPrint#(stringify($a_expr))
    SysPrint#(" at ")
    SysPrint#(srcloc($e_expr))
    SysPrint#("\n")
    trap

-- The two scalar arguments must be the same
--
-- Both must have derivable types as we use `auto`
pub macro AssertGenericEq# STMT_LIST($e_expr EXPR, $a_expr EXPR)[$e_val, $a_val]:
    mlet $e_val = $e_expr
    mlet $a_val = $a_expr
    if !cmp::eq($e_val, $a_val):
        AssertCommon#("AssertEq", $e_expr, $a_expr)

pub macro AssertEq# STMT_LIST($e_expr EXPR, $a_expr EXPR)[$e_val, $a_val]:
    mlet $e_val = $e_expr
    mlet $a_val = $a_expr
    if $e_val != $a_val:
        AssertCommon#("AssertEq", $e_expr, $a_expr)

-- The two scalar arguments must be the same
--
-- Both must have derivable types as we use `auto`
pub macro AssertGenericNe# STMT_LIST($e_expr EXPR, $a_expr EXPR)[$e_val, $a_val]:
    mlet $e_val = $e_expr
    mlet $a_val = $a_expr
    if cmp::eq($e_val, $a_val):
        AssertCommon#("AssertNe", $e_expr, $a_expr)

pub macro AssertNe# STMT_LIST($e_expr EXPR, $a_expr EXPR)[$e_val, $a_val]:
    mlet $e_val = $e_expr
    mlet $a_val = $a_expr
    if $e_val == $a_val:
        AssertCommon#("AssertNe", $e_expr, $a_expr)

-- First argument must have the type denoted by the second
pub macro AssertIs# STMT_LIST($expr EXPR, $type TYPE)[]:
    if is($expr, $type):
    else:
        AssertCommon#("AssertIs", $expr, $type)

-- The two arguments must type derivable
pub macro AssertSliceEq# STMT_LIST($e_expr EXPR, $a_expr EXPR)[
        $e_val, $a_val, $i]:
    mlet $e_val = $e_expr
    mlet $a_val = $a_expr
    AssertEq#(len($e_val), len($a_val))
    for $i = 0, len($a_val), 1:
        AssertEq#(ptr_inc(front($e_val), $i)^, ptr_inc(front($a_val), $i)^)

pub macro AssertGenericSliceEq# STMT_LIST($e_expr EXPR, $a_expr EXPR)[
        $e_val, $a_val, $i]:
    mlet $e_val = $e_expr
    mlet $a_val = $a_expr
    AssertEq#(len($e_val), len($a_val))
    for $i = 0, len($a_val), 1:
        AssertGenericEq#(ptr_inc(front($e_val), $i)^, ptr_inc(front($a_val), $i)^)

pub macro AssertEqR64# STMT_LIST($e_expr EXPR, $a_expr EXPR)[$e_val, $a_val]:
    mlet $e_val r64 = $e_expr
    mlet $a_val r64 = $a_expr
    if bitwise_as($e_val, u64) != bitwise_as($a_val, u64):
        AssertCommon#("AssertEqR64", $e_expr, $a_expr)

pub macro AssertNeR64# STMT_LIST($e_expr EXPR, $a_expr EXPR)[$e_val, $a_val]:
    mlet $e_val r64 = $e_expr
    mlet $a_val r64 = $a_expr
    if bitwise_as($e_val, u64) == bitwise_as($a_val, u64):
        AssertCommon#("AssertNeR64", $e_expr, $a_expr)

--
pub macro AssertTrue# STMT_LIST($e_expr EXPR)[]:
    if $e_expr:
    else:
        SysPrint#("AssertTrue failed: ")
        SysPrint#(stringify($e_expr))
        SysPrint#(" at ")
        SysPrint#(srcloc($e_expr))
        SysPrint#("\n")
        trap

--
pub macro AssertFalse# STMT_LIST($e_expr EXPR)[]:
    if $e_expr:
        SysPrint#("AssertFalse failed: ")
        SysPrint#(stringify($e_expr))
        SysPrint#(" at ")
        SysPrint#(srcloc($e_expr))
        SysPrint#("\n")
        trap

--
pub macro AssertUnreachable# STMT_LIST()[]:
    SysPrint#("AssertUnreachable\n")
    trap
