## Abstract Syntax Tree (AST) Nodes used by Cwerg



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
[ExprFront&nbsp;(front)](#exprfront-front) &ensp;
[ExprIs&nbsp;(is)](#expris-is) &ensp;
[ExprPointer](#exprpointer) &ensp;
[ExprStmt&nbsp;(expr)](#exprstmt-expr) &ensp;
[ExprTryAs&nbsp;(tryas)](#exprtryas-tryas) &ensp;
[ExprUnsafeCast&nbsp;(cast)](#exprunsafecast-cast) &ensp;
[FieldVal&nbsp;(field_val)](#fieldval-field_val) &ensp;
[FunParam&nbsp;(param)](#funparam-param) &ensp;
[Id&nbsp;(id)](#id-id) &ensp;
[IndexVal&nbsp;(index_val)](#indexval-index_val) &ensp;
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
[ValRec&nbsp;(rec_val)](#valrec-rec_val) &ensp;
[ValString](#valstring) &ensp;
[ValTrue&nbsp;(true)](#valtrue-true) &ensp;
[ValUndef&nbsp;(undef)](#valundef-undef) &ensp;
[ValVoid&nbsp;(void_val)](#valvoid-void_val) &ensp;

## Node Overview (Non-Core)
[Case&nbsp;(case)](#case-case) &ensp;
[DefEnum&nbsp;(enum)](#defenum-enum) &ensp;
[DefMacro&nbsp;(macro)](#defmacro-macro) &ensp;
[EnumVal&nbsp;(entry)](#enumval-entry) &ensp;
[EphemeralList](#ephemerallist) &ensp;
[Expr3&nbsp;(?)](#expr3-) &ensp;
[ExprIndex&nbsp;(at)](#exprindex-at) &ensp;
[ExprLen&nbsp;(len)](#exprlen-len) &ensp;
[ExprOffsetof&nbsp;(offsetof)](#exproffsetof-offsetof) &ensp;
[ExprParen](#exprparen) &ensp;
[ExprSizeof&nbsp;(sizeof)](#exprsizeof-sizeof) &ensp;
[ExprSrcLoc&nbsp;(src_loc)](#exprsrcloc-src_loc) &ensp;
[ExprStringify&nbsp;(stringify)](#exprstringify-stringify) &ensp;
[Import&nbsp;(import)](#import-import) &ensp;
[MacroFor&nbsp;(macro_for)](#macrofor-macro_for) &ensp;
[MacroId&nbsp;(macro_id)](#macroid-macro_id) &ensp;
[MacroInvoke&nbsp;(macro_invoke)](#macroinvoke-macro_invoke) &ensp;
[MacroParam&nbsp;(mparam)](#macroparam-mparam) &ensp;
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
[Base Type Kind](#base-type-kind) &ensp;
[ModParam Kind](#modparam-kind) &ensp;
[MacroParam Kind](#macroparam-kind) &ensp;

## Misc Node Details

### Id (id)
Refers to a type, variable, constant, function, module by name.

    Ids may contain a path component indicating which modules they reference.
    

Fields:
* name [STR]: name of the object


## Type Node Details

### DefEnum (enum)
Enum definition

Allowed at top level only

Fields:
* name [STR]: name of the object
* base_type_kind [KIND]: see [Base Type Kind](#base-type-kind) below
* items [LIST]: enum items and/or comments

Flags:
* pub: has public visibility
* doc: comment


### DefRec (defrec)
Record definition

Allowed at top level only

Fields:
* name [STR]: name of the object
* fields [LIST]: record fields and/or comments

Flags:
* pub: has public visibility
* doc: comment


### EnumVal (entry)
 Enum element.

     `value: ValAuto` means previous value + 1

Fields:
* name [STR]: name of the object
* value_or_auto [NODE] (default ValAuto): enum constant or auto

Flags:
* doc: comment


### FunParam (param)
Function parameter

    

Fields:
* name [STR]: name of the object
* type [NODE]: type expression

Flags:
* doc: comment


### RecField (field)
Record field

    All fields must be explicitly initialized. Use `ValUndef` in performance
    sensitive situations.
    

Fields:
* name [STR]: name of the object
* type [NODE]: type expression

Flags:
* doc: comment


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
* base_type_kind [KIND]: see [Base Type Kind](#base-type-kind) below


### TypeFun (sig)
A function signature

    The `FunParam.name` field is ignored and should be `_`
    

Fields:
* params [LIST]: function parameters and/or comments
* result [NODE]: return type


### TypePtr (ptr)
Pointer type
    

Fields:
* type [NODE]: type expression

Flags:
* mut: is mutable


### TypeSlice (slice)
A view/slice of an array with compile-time unknown dimensions

    Internally, this is tuple of `start` and `length`
    (mutable/non-mutable)
    

Fields:
* type [NODE]: type expression

Flags:
* mut: is mutable


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

Flags:
* doc: comment


### DefFun (fun)
Function definition


    `init` and `fini` indicate module initializer/finalizers

    `extern` indicates a prototype and hence the function body must be empty.
    

Allowed at top level only

Fields:
* name [STR]: name of the object
* params [LIST]: function parameters and/or comments
* result [NODE]: return type
* body [LIST]: new scope: statement list and/or comments

Flags:
* polymorphic: function definition or call is polymorphic
* init: run function at startup
* fini: run function at shutdown
* pub: has public visibility
* extern: is external function (empty body)
* doc: comment


### DefGlobal (global)
Variable definition at global scope (DefVar is used for local scope)

    Allocates space in static memory and initializes it with `initial_or_undef`.
    `mut` makes the allocated space read/write otherwise it is readonly.
    

Allowed at top level only

Fields:
* name [STR]: name of the object
* type_or_auto [NODE]: type expression
* initial_or_undef_or_auto [NODE] (default ValAuto): initializer

Flags:
* pub: has public visibility
* mut: is mutable
* doc: comment


### DefMacro (macro)
Define a macro

    A macro consists of
    * a name 
    * the type of AST node (list) it create
    * a parameter list. A parameter name must start with a '$'
    * a list of additional identifiers used by the macro (also starimg with '$') 
    * a body containing both regular and macro specific AST node serving as a template
    

Allowed at top level only

Fields:
* name [STR]: name of the object
* macro_result_kind [KIND]: type of the macro result node,  see [MacroParam Kind](#macroparam-kind) below
* params_macro [LIST]: macro parameters
* gen_ids [STR_LIST]: name placeholder ids to be generated at macro instantiation time
* body_macro [LIST]: new scope: macro statments/expression

Flags:
* pub: has public visibility
* doc: comment


### DefMod (module)
Module Definition

    The module is a template if `params` is non-empty

Fields:
* name [STR]: name of the object
* params_mod [LIST]: module template parameters
* body_mod [LIST]: toplevel module definitions and/or comments

Flags:
* doc: comment


### DefType (type)
Type definition

    A `wrapped` gives the underlying type a new name that is not type compatible.
    To convert between the two use an `as` cast expression.
    

Allowed at top level only

Fields:
* name [STR]: name of the object
* type [NODE]: type expression

Flags:
* pub: has public visibility
* wrapped: is wrapped type (forces type equivalence by name)
* doc: comment


### DefVar (let)
Variable definition at local scope (DefGlobal is used for global scope)

    Allocates space on stack (or in a register) and initializes it with `initial_or_undef_or_auto`.
    `mut` makes the allocated space read/write otherwise it is readonly.
    `ref` allows the address of the  variable to be taken and prevents register allocation.

    

Fields:
* name [STR]: name of the object
* type_or_auto [NODE]: type expression
* initial_or_undef_or_auto [NODE] (default ValAuto): initializer

Flags:
* mut: is mutable
* ref: address may be taken
* doc: comment


### Import (import)
Import another Module from `path` as `name`

Fields:
* name [STR]: name of the object
* alias [STR] (default ""): name of imported module to be used instead of given name

Flags:
* doc: comment


### ModParam
Module Parameters

Fields:
* name [STR]: name of the object
* mod_param_kind [KIND]: see [ModParam Kind](#modparam-kind) below

Flags:
* doc: comment


### StmtAssignment (=)
Assignment statement

Fields:
* lhs [NODE]: l-value expression
* expr_rhs [NODE]: rhs of assignment

Flags:
* doc: comment


### StmtBlock (block)
Block statement.

    if `label` is non-empty, nested break/continue statements can target this `block`.
    

Fields:
* label [STR]: block  name (if not empty)
* body [LIST]: new scope: statement list and/or comments

Flags:
* doc: comment


### StmtBreak (break)
Break statement

    use "" if the target is the nearest for/while/block 

Fields:
* target [STR] (default ""): name of enclosing while/for/block to brach to (empty means nearest)

Flags:
* doc: comment


### StmtCompoundAssignment
Compound assignment statement

Fields:
* assignment_kind [KIND]: see [StmtCompoundAssignment Kind](#stmtcompoundassignment-kind) below
* lhs [NODE]: l-value expression
* expr_rhs [NODE]: rhs of assignment

Flags:
* doc: comment


### StmtCond (cond)
Multicase if-elif-else statement

Fields:
* cases [LIST]: list of case statements

Flags:
* doc: comment


### StmtContinue (continue)
Continue statement

    use "" if the target is the nearest for/while/block 

Fields:
* target [STR] (default ""): name of enclosing while/for/block to brach to (empty means nearest)

Flags:
* doc: comment


### StmtDefer (defer)
Defer statement

    Note: defer body's containing return statments have
    non-straightforward semantics.
    

Fields:
* body [LIST]: new scope: statement list and/or comments

Flags:
* doc: comment


### StmtExpr (stmt)
Expression statement

    Turns an expression (typically a call) into a statement
    

Fields:
* expr [NODE]: expression

Flags:
* doc: comment


### StmtIf (if)
If statement

Fields:
* cond [NODE]: conditional expression must evaluate to a boolean
* body_t [LIST]: new scope: statement list and/or comments for true branch
* body_f [LIST]: new scope: statement list and/or comments for false branch

Flags:
* doc: comment


### StmtReturn (return)
Return statement

    Returns from the first enclosing ExprStmt node or the enclosing DefFun node.
    Uses void_val if the DefFun's return type is void
    

Fields:
* expr_ret [NODE] (default ValVoid): result expression (ValVoid means no result)

Flags:
* doc: comment


### StmtStaticAssert (static_assert)
Static assert statement (must evaluate to true at compile-time

Allowed at top level only

Fields:
* cond [NODE]: conditional expression must evaluate to a boolean
* message [STR] (default ""): message for assert failures

Flags:
* doc: comment


### StmtTrap (trap)
Trap statement

Fields:

Flags:
* doc: comment


## Value Node Details

### FieldVal (field_val)
Part of rec literal

    e.g. `.imag = 5`
    If field is empty use `first field` or `next field`.
    

Fields:
* value [NODE]: 
* init_field [STR] (default ""): initializer field or empty (empty means next field)

Flags:
* doc: comment


### IndexVal (index_val)
Part of an array literal

    e.g. `.1 = 5`
    If index is empty use `0` or `previous index + 1`.
    

Fields:
* value_or_undef [NODE]: 
* init_index [NODE] (default ValAuto): initializer index or empty (empty mean next index)

Flags:
* doc: comment


### ValArray (array_val)
An array literal

    `[10]int{.1 = 5, .2 = 6, 77}`

    `expr_size` must be constant or auto
    

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


### ValRec (rec_val)
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
* string [STR]: string literal

Flags:
* raw: ignore escape sequences in string


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
* unary_expr_kind [KIND]: see [Expr1 Kind](#expr1-kind) below
* expr [NODE]: expression


### Expr2
Binary expression.

Fields:
* binary_expr_kind [KIND]: see [Expr2 Kind](#expr2-kind) below
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
* expr_lhs [NODE]: l-value expression

Flags:
* mut: is mutable


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

    Type must have same size and alignment as type of item

    s32,u32,f32 <-> s32,u32,f32
    s64,u64, f64 <-> s64,u64, f64
    sint, uint <-> ptr

    It is also ok to bitcase complex objects like recs
    

Fields:
* expr [NODE]: expression
* type [NODE]: type expression


### ExprCall (call)
Function call expression.
    

Fields:
* callee [NODE]: expression evaluating to the function to be called
* args [LIST]: function call arguments

Flags:
* polymorphic: function definition or call is polymorphic


### ExprDeref (^)
Dereference a pointer represented by `expr`

Fields:
* expr [NODE]: expression


### ExprField (.)
Access field in expression representing a record.
    

Fields:
* container [NODE]: array and slice
* field [STR]: record field


### ExprFront (front)
Address of the first element of an array or slice

    Similar to `(& (at container 0))` but will not fail if container has zero size

    

Fields:
* container [NODE]: array and slice

Flags:
* mut: is mutable


### ExprIndex (at)
Checked indexed access of array or slice
    

Fields:
* container [NODE]: array and slice
* expr_index [NODE]: expression determining the index to be accessed

Flags:
* unchecked: array acces is not checked


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


### ExprPointer
Pointer arithmetic expression - optionally bound checked..

Fields:
* pointer_expr_kind [KIND]: see [PointerOp Kind](#pointerop-kind) below
* expr1 [NODE]: left operand expression
* expr2 [NODE]: righ operand expression
* expr_bound_or_undef [NODE] (default ValUndef): 


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

Flags:
* colon: colon style list


### MacroFor (macro_for)
Macro for-loop like statement

    loops over the macro parameter `name_list` which must be a list and 
    binds each list element to `name` while expanding the AST nodes in `body_for`. 
    

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


### MacroParam (mparam)
Macro Parameter

Fields:
* name [STR]: name of the object
* macro_param_kind [KIND]: type of a macro parameter node, see [MacroParam Kind](#macroparam-kind) below

Flags:
* doc: comment


### MacroVar (macro_let)
Macro Variable definition whose name stems from a macro parameter or macro_gen_id"

    `name` must start with a `$`.

    

Fields:
* name [STR]: name of the object
* type_or_auto [NODE]: type expression
* initial_or_undef_or_auto [NODE] (default ValAuto): initializer

Flags:
* mut: is mutable
* ref: address may be taken
* doc: comment

## Enum Details

### Expr1 Kind

|Kind|Abbrev|
|----|------|
|NOT       |!|
|MINUS     |~|
|NEG       |not|

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
|PDELTA    |pdelta|

### ExprPointer Kind

|Kind|Abbrev|
|----|------|
|INCP      |incp|
|DECP      |decp|

### StmtCompoundAssignment Kind

|Kind|Abbrev|
|----|------|
|ADD       |+=|
|SUB       |-=|
|DIV       |/=|
|MUL       |*=|
|REM       |%=|
|AND       |and=|
|OR        |or=|
|XOR       |xor=|
|SHR       |>>=|
|SHL       |<<=|

### Base Type Kind

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

### ModParam Kind

|Kind|
|----|
|CONST     |
|MOD       |
|TYPE      |

### MacroParam Kind

|Kind|
|----|
|ID        |
|STMT_LIST |
|EXPR_LIST |
|EXPR      |
|STMT      |
|FIELD     |
|TYPE      |
