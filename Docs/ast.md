## Abstract Syntax Tree (AST) Nodes used by Cwerg

WIP


## Node Overview (Core)
[DefFun&nbsp;(fun)](#deffun-fun) &ensp;
[DefGlobal&nbsp;(global)](#defglobal-global) &ensp;
[DefMod&nbsp;(module)](#defmod-module) &ensp;
[DefRec&nbsp;(defrec)](#defrec-defrec) &ensp;
[DefType&nbsp;(type)](#deftype-type) &ensp;
[DefVar&nbsp;(let)](#defvar-let) &ensp;
[Expr1](#expr1) &ensp;
[Expr2](#expr2) &ensp;
[ExprAddrOf&nbsp;(&)](#expraddrof-) &ensp;
[ExprAs&nbsp;(as)](#expras-as) &ensp;
[ExprAsNot&nbsp;(asnot)](#exprasnot-asnot) &ensp;
[ExprBitCast&nbsp;(bitcast)](#exprbitcast-bitcast) &ensp;
[ExprCall&nbsp;(call)](#exprcall-call) &ensp;
[ExprDeref&nbsp;(^)](#exprderef-) &ensp;
[ExprField&nbsp;(.)](#exprfield-.) &ensp;
[ExprIndex&nbsp;(at)](#exprindex-at) &ensp;
[ExprIs&nbsp;(is)](#expris-is) &ensp;
[ExprLen&nbsp;(len)](#exprlen-len) &ensp;
[ExprParen](#exprparen) &ensp;
[ExprStmt&nbsp;(expr)](#exprstmt-expr) &ensp;
[ExprTryAs&nbsp;(tryas)](#exprtryas-tryas) &ensp;
[ExprUnsafeCast&nbsp;(cast)](#exprunsafecast-cast) &ensp;
[FieldVal](#fieldval) &ensp;
[FunParam&nbsp;(param)](#funparam-param) &ensp;
[Id&nbsp;(id)](#id-id) &ensp;
[IndexVal](#indexval) &ensp;
[RecField&nbsp;(field)](#recfield-field) &ensp;
[StmtAssignment&nbsp;(=)](#stmtassignment-) &ensp;
[StmtBlock&nbsp;(block)](#stmtblock-block) &ensp;
[StmtBreak&nbsp;(break)](#stmtbreak-break) &ensp;
[StmtContinue&nbsp;(continue)](#stmtcontinue-continue) &ensp;
[StmtExpr&nbsp;(stmt)](#stmtexpr-stmt) &ensp;
[StmtIf&nbsp;(if)](#stmtif-if) &ensp;
[StmtReturn&nbsp;(return)](#stmtreturn-return) &ensp;
[StmtTrap&nbsp;(trap)](#stmttrap-trap) &ensp;
[TypeArray&nbsp;(array)](#typearray-array) &ensp;
[TypeAuto&nbsp;(auto)](#typeauto-auto) &ensp;
[TypeBase](#typebase) &ensp;
[TypeFun&nbsp;(sig)](#typefun-sig) &ensp;
[TypePtr&nbsp;(ptr)](#typeptr-ptr) &ensp;
[TypeSum&nbsp;(union)](#typesum-union) &ensp;
[ValArray&nbsp;(array_val)](#valarray-array_val) &ensp;
[ValAuto&nbsp;(auto_val)](#valauto-auto_val) &ensp;
[ValFalse&nbsp;(false)](#valfalse-false) &ensp;
[ValNum&nbsp;(num)](#valnum-num) &ensp;
[ValRec&nbsp;(rec)](#valrec-rec) &ensp;
[ValString](#valstring) &ensp;
[ValTrue&nbsp;(true)](#valtrue-true) &ensp;
[ValUndef&nbsp;(undef)](#valundef-undef) &ensp;
[ValVoid&nbsp;(void_val)](#valvoid-void_val) &ensp;

## Node Overview (Non-Core)
[Case&nbsp;(case)](#case-case) &ensp;
[Comment&nbsp;(#)](#comment-) &ensp;
[DefEnum&nbsp;(enum)](#defenum-enum) &ensp;
[DefMacro&nbsp;(macro)](#defmacro-macro) &ensp;
[EnumVal&nbsp;(entry)](#enumval-entry) &ensp;
[EphemeralList](#ephemerallist) &ensp;
[Expr3&nbsp;(?)](#expr3-) &ensp;
[ExprOffsetof&nbsp;(offsetof)](#exproffsetof-offsetof) &ensp;
[ExprSizeof&nbsp;(sizeof)](#exprsizeof-sizeof) &ensp;
[ExprSrcLoc&nbsp;(src_loc)](#exprsrcloc-src_loc) &ensp;
[ExprStringify&nbsp;(stringify)](#exprstringify-stringify) &ensp;
[Import&nbsp;(import)](#import-import) &ensp;
[MacroFor&nbsp;(macro_for)](#macrofor-macro_for) &ensp;
[MacroId&nbsp;(macro_id)](#macroid-macro_id) &ensp;
[MacroInvoke&nbsp;(macro_invoke)](#macroinvoke-macro_invoke) &ensp;
[MacroParam&nbsp;(macro_param)](#macroparam-macro_param) &ensp;
[MacroVar&nbsp;(macro_let)](#macrovar-macro_let) &ensp;
[ModParam](#modparam) &ensp;
[StmtCompoundAssignment](#stmtcompoundassignment) &ensp;
[StmtCond&nbsp;(cond)](#stmtcond-cond) &ensp;
[StmtDefer&nbsp;(defer)](#stmtdefer-defer) &ensp;
[StmtStaticAssert&nbsp;(static_assert)](#stmtstaticassert-static_assert) &ensp;
[TypeSlice&nbsp;(slice)](#typeslice-slice) &ensp;
[ValSlice&nbsp;(slice_val)](#valslice-slice_val) &ensp;

## Enum Overview
[Expr1 Kind](#expr1-kind) &ensp;
[Expr2 Kind](#expr2-kind) &ensp;
[StmtCompoundAssignment Kind](#stmtcompoundassignment-kind) &ensp;
[Base Types Kind](#base-types-kind) &ensp;
[ModParam Types Kind](#modparam-types-kind) &ensp;
[MacroParam Types Kind](#macroparam-types-kind) &ensp;

## Misc Node Details

### Comment (#)
Comment

    Comments are proper AST nodes and may only occur where explicitly allowed.
    They refer to the next sibling in the tree.
    

Fields:
* comment [STR]: comment

### Id (id)
Refers to a type, variable, constant, function, module by name.

    Ids may contain a path component indicating which modules they reference.
    

Fields:
* name [STR]: name of the object
* path [STR] (default ""): TBD

## Type Node Details

### DefEnum (enum)
Enum definition

Allowed at top level only

Fields:
* pub [FLAG]: has public visibility
* name [STR]: name of the object
* base_type_kind [KIND]: see Base Types below
* items [LIST]: enum items and/or comments

### DefRec (defrec)
Record definition

Allowed at top level only

Fields:
* pub [FLAG]: has public visibility
* name [STR]: name of the object
* fields [LIST]: record fields and/or comments

### EnumVal (entry)
 Enum element.

     `value: ValAuto` means previous value + 1

Fields:
* name [STR]: name of the object
* value_or_auto [NODE] (default ValAuto): enum constant or auto

### FunParam (param)
Function parameter

    

Fields:
* name [STR]: name of the object
* type [NODE]: type expression

### RecField (field)
Record field

    All fields must be explicitly initialized. Use `ValUndef` in performance
    sensitive situations.
    

Fields:
* name [STR]: name of the object
* type [NODE]: type expression
* initial_or_undef [NODE] (default ValUndef): initializer

### TypeArray (array)
An array of the given type and `size`

    

Fields:
* size [NODE]: compile-time constant size
* type [NODE]: type expression

### TypeAuto (auto)
Placeholder for an unspecified (auto derived) type

    My only occur where explicitly allowed.
    

Fields:

### TypeBase
Base type

    One of: void, bool, r32, r64, u8, u16, u32, u64, s8, s16, s32, s64
    

Fields:
* base_type_kind [KIND]: see Base Types below

### TypeFun (sig)
A function signature

    The `FunParam.name` field is ignored and should be `_`
    

Fields:
* params [LIST]: function parameters and/or comments
* result [NODE]: return type

### TypePtr (ptr)
Pointer type
    

Fields:
* mut [FLAG]: is mutable
* type [NODE]: type expression

### TypeSlice (slice)
A view/slice of an array with compile-time unknown dimensions

    Internally, this is tuple of `start` and `length`
    (mutable/non-mutable)
    

Fields:
* mut [FLAG]: is mutable
* type [NODE]: type expression

### TypeSum (union)
Sum types (tagged unions)

    Sums are "auto flattening", e.g.
    Sum(a, Sum(b,c), Sum(a, d)) = Sum(a, b, c, d)
    

Fields:
* types [LIST]: union types

## Statement Node Details

### Case (case)
Single case of a Cond statement

Fields:
* cond [NODE]: conditional expression must evaluate to a boolean
* body [LIST]: new scope: statement list and/or comments

### DefFun (fun)
Function definition

Allowed at top level only

Fields:
* init [FLAG]: run function at startup
* fini [FLAG]: run function at shutdown
* pub [FLAG]: has public visibility
* extern [FLAG]: is external function (empty body)
* polymorphic [FLAG]: function definition or call is polymorphic
* name [STR]: name of the object
* params [LIST]: function parameters and/or comments
* result [NODE]: return type
* body [LIST]: new scope: statement list and/or comments

### DefGlobal (global)
Variable definition

    Allocates space in static memory and initializes it with `initial_or_undef`.
    `mut` makes the allocated space read/write otherwise it is readonly.
    

Allowed at top level only

Fields:
* pub [FLAG]: has public visibility
* mut [FLAG]: is mutable
* name [STR]: name of the object
* type_or_auto [NODE]: type expression
* initial_or_undef [NODE] (default ValUndef): initializer

### DefMacro (macro)
Define a macro


    A macro consists of parameters whose name starts with a '$'
    and a body. Macros that evaluate to expressions will typically
    have a single node body
    

Allowed at top level only

Fields:
* pub [FLAG]: has public visibility
* name [STR]: name of the object
* params_macro [LIST]: macro parameters
* gen_ids [STR_LIST]: name placeholder ids to be generated at macro instantiation time
* body_macro [LIST]: new scope: macro statments/expression

### DefMod (module)
Module Definition

    The module is a template if `params` is non-empty

Fields:
* name [STR]: name of the object
* params_mod [LIST]: module template parameters
* body_mod [LIST]: toplevel module definitions and/or comments

### DefType (type)
Type definition

    

Allowed at top level only

Fields:
* pub [FLAG]: has public visibility
* wrapped [FLAG]: is wrapped type (forces type equivalence by name)
* name [STR]: name of the object
* type [NODE]: type expression

### DefVar (let)
Variable definition

    Allocates space on stack and initializes it with `initial_or_undef`.
    `mut` makes the allocated space read/write otherwise it is readonly.

    

Fields:
* mut [FLAG]: is mutable
* name [STR]: name of the object
* type_or_auto [NODE]: type expression
* initial_or_undef [NODE] (default ValUndef): initializer

### Import (import)
Import another Module

Fields:
* name [STR]: name of the object
* alias [STR] (default ""): name of imported module to be used instead of given name

### ModParam
Module Parameters

Fields:
* name [STR]: name of the object
* mod_param_kind [KIND]: see ModParam Kind below

### StmtAssignment (=)
Assignment statement

Fields:
* lhs [NODE]: l-value expression
* expr_rhs [NODE]: rhs of assignment

### StmtBlock (block)
Block statement.

    if `label` is non-empty, nested break/continue statements can target this `block`.
    

Fields:
* label [STR]: block  name (if not empty)
* body [LIST]: new scope: statement list and/or comments

### StmtBreak (break)
Break statement

    use "" if the target is the nearest for/while/block 

Fields:
* target [STR] (default ""): name of enclosing while/for/block to brach to (empty means nearest)

### StmtCompoundAssignment
Compound assignment statement

Fields:
* assignment_kind [KIND]: see StmtCompoundAssignment Kind below
* lhs [NODE]: l-value expression
* expr_rhs [NODE]: rhs of assignment

### StmtCond (cond)
Multicase if-elif-else statement

Fields:
* cases [LIST]: list of case statements

### StmtContinue (continue)
Continue statement

    use "" if the target is the nearest for/while/block 

Fields:
* target [STR] (default ""): name of enclosing while/for/block to brach to (empty means nearest)

### StmtDefer (defer)
Defer statement

    Note: defer body's containing return statments have
    non-straightforward semantics.
    

Fields:
* body [LIST]: new scope: statement list and/or comments

### StmtExpr (stmt)
Expression statement

    If expression does not have type void, `discard` must be `true`
    

Fields:
* discard [FLAG]: ignore non-void expression
* expr [NODE]: expression

### StmtIf (if)
If statement

Fields:
* cond [NODE]: conditional expression must evaluate to a boolean
* body_t [LIST]: new scope: statement list and/or comments for true branch
* body_f [LIST]: new scope: statement list and/or comments for false branch

### StmtReturn (return)
Return statement

    Returns from the first enclosing ExprStmt node or the enclosing DefFun node.
    Uses void_val if the DefFun's return type is void
    

Fields:
* expr_ret [NODE] (default ValVoid): result expression (ValVoid means no result)

### StmtStaticAssert (static_assert)
Static assert statement (must evaluate to true at compile-time

Allowed at top level only

Fields:
* cond [NODE]: conditional expression must evaluate to a boolean
* message [STR] (default ""): message for assert failures

### StmtTrap (trap)
Trap statement

Fields:

## Value Node Details

### FieldVal
Part of rec literal

    e.g. `.imag = 5`
    If field is empty use `first field` or `next field`.
    

Fields:
* value [NODE]: 
* init_field [STR] (default ""): initializer field or empty (empty means next field)

### IndexVal
Part of an array literal

    e.g. `.1 = 5`
    If index is empty use `0` or `previous index + 1`.
    

Fields:
* value_or_undef [NODE]: 
* init_index [NODE] (default ValAuto): initializer index or empty (empty mean next index)

### ValArray (array_val)
An array literal

    `[10]int{.1 = 5, .2 = 6, 77}`
    

Fields:
* expr_size [NODE]: expression determining the size or auto
* type [NODE]: type expression
* inits_array [LIST] (default list): array initializers and/or comments

### ValAuto (auto_val)
Placeholder for an unspecified (auto derived) value

    Used for: array dimensions, enum values, chap and range
    

Fields:

### ValFalse (false)
Bool constant `false`

Fields:

### ValNum (num)
Numeric constant (signed int, unsigned int, real

    Underscores in `number` are ignored. `number` can be explicitly typed via
    suffices like `_u64`, `_s16`, `_r32`.
    

Fields:
* number [STR]: a number

### ValRec (rec)
A record literal

    `E.g.: complex{.imag = 5, .real = 1}`
    

Fields:
* type [NODE]: type expression
* inits_rec [LIST]: record initializers and/or comments

### ValSlice (slice_val)
A slice value comprised of a pointer and length

    type and mutability is defined by the pointer
    

Fields:
* pointer [NODE]: pointer component of slice
* expr_size [NODE]: expression determining the size or auto

### ValString
An array value encoded as a string

    type is `[strlen(string)]u8`. `string` may be escaped/raw
    

Fields:
* raw [FLAG]: ignore escape sequences in string
* string [STR]: string literal

### ValTrue (true)
Bool constant `true`

Fields:

### ValUndef (undef)
Special constant to indiciate *no default value*
    

Fields:

### ValVoid (void_val)
Only value inhabiting the `TypeVoid` type

    It can be used to model *null* in nullable pointers via a sum type.
     

Fields:

## Expression Node Details

### Expr1
Unary expression.

Fields:
* unary_expr_kind [KIND]: see Expr1 Kind below
* expr [NODE]: expression

### Expr2
Binary expression.

Fields:
* binary_expr_kind [KIND]: see Expr2 Kind below
* expr1 [NODE]: left operand expression
* expr2 [NODE]: righ operand expression

### Expr3 (?)
Tertiary expression (like C's `? :`)
    

Fields:
* cond [NODE]: conditional expression must evaluate to a boolean
* expr_t [NODE]: expression (will only be evaluated if cond == true)
* expr_f [NODE]: expression (will only be evaluated if cond == false)

### ExprAddrOf (&)
Create a pointer to object represented by `expr`

    Pointer can optionally point to a mutable object if the
    pointee is mutable.
    

Fields:
* mut [FLAG]: is mutable
* lhs [NODE]: l-value expression

### ExprAs (as)
Safe Cast (Conversion)

    Allowed:
    enum <-> undelying enum type
    wrapped type <-> undelying enum type
    u8-u64, s8-s64 <-> u8-u64, s8-s64
    u8-u64, s8-s64 -> r32-r64  (note: one way only)

    Possibly
    slice -> ptr
    ptr to rec -> ptr to first element of rec
    

Fields:
* expr [NODE]: expression
* type [NODE]: type expression

### ExprAsNot (asnot)
Cast of Union to diff of the union and the given type

    

Fields:
* expr [NODE]: expression
* type [NODE]: type expression

### ExprBitCast (bitcast)
Bit cast.

    Type must have same size as type of item

    s32,u32,f32 <-> s32,u32,f32
    s64,u64, f64 <-> s64,u64, f64
    sint, uint <-> ptr
    

Fields:
* expr [NODE]: expression
* type [NODE]: type expression

### ExprCall (call)
Function call expression.
    

Fields:
* polymorphic [FLAG]: function definition or call is polymorphic
* callee [NODE]: expression evaluating to the function to be called
* args [LIST]: function call arguments

### ExprDeref (^)
Dereference a pointer represented by `expr`

Fields:
* expr [NODE]: expression

### ExprField (.)
Access field in expression representing a record.
    

Fields:
* container [NODE]: array and slice
* field [STR]: record field

### ExprIndex (at)
Checked indexed access of array or slice
    

Fields:
* container [NODE]: array and slice
* expr_index [NODE]: expression determining the index to be accessed

### ExprIs (is)
Test actual expression type within a Sum Type

    

Fields:
* expr [NODE]: expression
* type [NODE]: type expression

### ExprLen (len)
Length of array or slice

Fields:
* container [NODE]: array and slice

### ExprOffsetof (offsetof)
Byte offset of field in record types

    Type is `uint`

Fields:
* type [NODE]: type expression
* field [STR]: record field

### ExprParen
Used for preserving parenthesis in the source
    

Fields:
* expr [NODE]: expression

### ExprSizeof (sizeof)
Byte size of type

    Type is `uint`

Fields:
* type [NODE]: type expression

### ExprSrcLoc (src_loc)
Source Location encoded as u32

Fields:

### ExprStmt (expr)
Expr with Statements

    The body statements must be terminated by a StmtReturn
    

Fields:
* body [LIST]: new scope: statement list and/or comments

### ExprStringify (stringify)
Human readable representation of the expression

    This is useful to implement for assert like features
    

Fields:
* expr [NODE]: expression

### ExprTryAs (tryas)
Narrow a `expr` which is of Sum to `type`

    If the is not possible return `default_or_undef` if that is not undef
    or trap otherwise.

    

Fields:
* expr [NODE]: expression
* type [NODE]: type expression
* default_or_undef [NODE]: value if type narrowing fail or trap if undef

### ExprUnsafeCast (cast)
Unsafe Cast

    Allowed:
    ptr a <-> ptr b

    

Fields:
* expr [NODE]: expression
* type [NODE]: type expression

## Macro Node Details

### EphemeralList
Only exist temporarily after a replacement strep

    will removed (flattened) in the next cleanup step
    

Fields:
* args [LIST]: function call arguments

### MacroFor (macro_for)
Macro for-loop like statement

    NYI
    

Fields:
* name [STR]: name of the object
* name_list [STR]: name of the object list
* body_for [LIST]: statement list for macro_loop

### MacroId (macro_id)
Placeholder for a parameter

    This node will be expanded with the actual argument
    

Fields:
* name [STR]: name of the object

### MacroInvoke (macro_invoke)
Macro Invocation

Fields:
* name [STR]: name of the object
* args [LIST]: function call arguments

### MacroParam (macro_param)
Macro Parameter

Fields:
* name [STR]: name of the object
* macro_param_kind [KIND]: see MacroParam Kind below

### MacroVar (macro_let)
Macro Variable definition whose name stems from a macro parameter or macro_gen_id"

    `name` must start with a `$`.

    

Fields:
* mut [FLAG]: is mutable
* name [STR]: name of the object
* type_or_auto [NODE]: type expression
* initial_or_undef [NODE] (default ValUndef): initializer
## Enum Details

### Expr1 Kind

|Kind|Abbrev|
|----|------|
|NOT       |!|
|MINUS     |~|
|NEG       |neg|

### Expr2 Kind

|Kind|Abbrev|
|----|------|
|ADD       |+|
|SUB       |-|
|DIV       |/|
|MUL       |*|
|REM       |%|
|MIN       |min|
|MAX       |max|
|AND       |and|
|OR        |or|
|XOR       |xor|
|EQ        |==|
|NE        |!=|
|LT        |<|
|LE        |<=|
|GT        |>|
|GE        |>=|
|ANDSC     |&&|
|ORSC      ||||
|SHR       |>>|
|SHL       |<<|
|INCP      |incp|
|DECP      |decp|
|PDELTA    |pdelta|

### StmtCompoundAssignment Kind

|Kind|Abbrev|
|----|------|
|ADD       |+=|
|SUB       |-=|
|DIV       |/=|
|MUL       |*=|
|REM       |%=|
|INCP      |incp=|
|DECP      |decp=|
|AND       |and=|
|OR        |or=|
|XOR       |xor=|
|SHR       |>>=|
|SHL       |<<=|

### Base Types Kind

|Kind|
|----|
|SINT      |
|S8        |
|S16       |
|S32       |
|S64       |
|UINT      |
|U8        |
|U16       |
|U32       |
|U64       |
|R32       |
|R64       |
|VOID      |
|NORET     |
|BOOL      |

### ModParam Types Kind

|Kind|
|----|
|CONST     |
|MOD       |
|TYPE      |

### MacroParam Types Kind

|Kind|
|----|
|ID        |
|STMT_LIST |
|EXPR      |
|FIELD     |
|TYPE      |
