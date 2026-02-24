## Abstract Syntax Tree (AST) Nodes used by Cwerg



## Node Overview (Core)

Core nodes are the ones that are known to the code generator.

[DefEnum&nbsp;(enum)](#defenum-enum) &ensp;
[DefFun&nbsp;(fun)](#deffun-fun) &ensp;
[DefGlobal&nbsp;(global)](#defglobal-global) &ensp;
[DefMod&nbsp;(module)](#defmod-module) &ensp;
[DefRec&nbsp;(rec)](#defrec-rec) &ensp;
[DefVar&nbsp;(let)](#defvar-let) &ensp;
[EnumVal](#enumval) &ensp;
[Expr1](#expr1) &ensp;
[Expr2](#expr2) &ensp;
[ExprAddrOf&nbsp;(@)](#expraddrof-) &ensp;
[ExprAs&nbsp;(as)](#expras-as) &ensp;
[ExprBitCast&nbsp;(bitwise_as)](#exprbitcast-bitwise_as) &ensp;
[ExprCall](#exprcall) &ensp;
[ExprDeref&nbsp;(^)](#exprderef-) &ensp;
[ExprField&nbsp;(.)](#exprfield-.) &ensp;
[ExprFront&nbsp;(front)](#exprfront-front) &ensp;
[ExprNarrow&nbsp;(narrow_as)](#exprnarrow-narrow_as) &ensp;
[ExprPointer](#exprpointer) &ensp;
[ExprStmt&nbsp;(expr)](#exprstmt-expr) &ensp;
[ExprUnwrap&nbsp;(unwrap)](#exprunwrap-unwrap) &ensp;
[ExprWiden&nbsp;(widen_as)](#exprwiden-widen_as) &ensp;
[ExprWrap&nbsp;(wrap_as)](#exprwrap-wrap_as) &ensp;
[FunParam](#funparam) &ensp;
[Id](#id) &ensp;
[RecField](#recfield) &ensp;
[StmtAssignment&nbsp;(=)](#stmtassignment-) &ensp;
[StmtBlock&nbsp;(block)](#stmtblock-block) &ensp;
[StmtBreak&nbsp;(break)](#stmtbreak-break) &ensp;
[StmtContinue&nbsp;(continue)](#stmtcontinue-continue) &ensp;
[StmtExpr&nbsp;(do)](#stmtexpr-do) &ensp;
[StmtIf&nbsp;(if)](#stmtif-if) &ensp;
[StmtReturn&nbsp;(return)](#stmtreturn-return) &ensp;
[StmtTrap&nbsp;(trap)](#stmttrap-trap) &ensp;
[TypeAuto&nbsp;(auto)](#typeauto-auto) &ensp;
[ValAuto&nbsp;(auto_val)](#valauto-auto_val) &ensp;
[ValCompound](#valcompound) &ensp;
[ValNum](#valnum) &ensp;
[ValPoint](#valpoint) &ensp;
[ValString](#valstring) &ensp;
[ValUndef&nbsp;(undef)](#valundef-undef) &ensp;
[ValVoid&nbsp;(void_val)](#valvoid-void_val) &ensp;
(41 nodes)

## Node Overview (Non-Core)

Non-core nodes are syntactic sugar and will be eliminated before
code generation.

[Case&nbsp;(case)](#case-case) &ensp;
[DefMacro&nbsp;(macro)](#defmacro-macro) &ensp;
[DefType&nbsp;(type)](#deftype-type) &ensp;
[EphemeralList](#ephemerallist) &ensp;
[Expr3&nbsp;(?)](#expr3-) &ensp;
[ExprIndex&nbsp;(at)](#exprindex-at) &ensp;
[ExprIs&nbsp;(is)](#expris-is) &ensp;
[ExprLen&nbsp;(len)](#exprlen-len) &ensp;
[ExprOffsetof&nbsp;(offset_of)](#exproffsetof-offset_of) &ensp;
[ExprParen](#exprparen) &ensp;
[ExprSizeof&nbsp;(size_of)](#exprsizeof-size_of) &ensp;
[ExprSrcLoc&nbsp;(srcloc)](#exprsrcloc-srcloc) &ensp;
[ExprStringify&nbsp;(stringify)](#exprstringify-stringify) &ensp;
[ExprTypeId&nbsp;(typeid_of)](#exprtypeid-typeid_of) &ensp;
[ExprUnionTag&nbsp;(union_tag)](#expruniontag-union_tag) &ensp;
[ExprUnionUntagged&nbsp;(union_untagged)](#exprunionuntagged-union_untagged) &ensp;
[Import&nbsp;(import)](#import-import) &ensp;
[MacroFor&nbsp;(mfor)](#macrofor-mfor) &ensp;
[MacroId](#macroid) &ensp;
[MacroInvoke](#macroinvoke) &ensp;
[MacroParam](#macroparam) &ensp;
[ModParam](#modparam) &ensp;
[StmtCompoundAssignment](#stmtcompoundassignment) &ensp;
[StmtCond&nbsp;(cond)](#stmtcond-cond) &ensp;
[StmtDefer&nbsp;(defer)](#stmtdefer-defer) &ensp;
[StmtStaticAssert&nbsp;(static_assert)](#stmtstaticassert-static_assert) &ensp;
[TypeBase](#typebase) &ensp;
[TypeFun&nbsp;(funtype)](#typefun-funtype) &ensp;
[TypeOf&nbsp;(type_of)](#typeof-type_of) &ensp;
[TypePtr](#typeptr) &ensp;
[TypeSpan&nbsp;(span)](#typespan-span) &ensp;
[TypeUnion&nbsp;(union)](#typeunion-union) &ensp;
[TypeUnionDelta&nbsp;(union_delta)](#typeuniondelta-union_delta) &ensp;
[TypeVec&nbsp;(vec)](#typevec-vec) &ensp;
[ValSpan&nbsp;(make_span)](#valspan-make_span) &ensp;
(35 nodes)

## Enum Overview

Misc enums used inside of nodes.

[Expr1 Kind](#expr1-kind) &ensp;
[Expr2 Kind](#expr2-kind) &ensp;
[Base Type Kind](#base-type-kind) &ensp;
[ModParam Kind](#modparam-kind) &ensp;
[MacroParam Kind](#macroparam-kind) &ensp;

## Misc Node Details

### Id
Refers to a type, variable, constant, function, module by name.

    Ids may contain a path component indicating which modules they reference.
    If the path component is missing the Id refers to the current module.

    id or mod::id or enum::id or mod::enum:id
    

Fields:
* name [NAME]: name of the object


## Type Node Details

### FunParam
Function parameter

    

Fields:
* name [NAME]: name of the object
* type [NODE]: type expression

Flags:
* arg_ref: in parameter was converted for by-val to pointer
* res_ref: in parameter was converted for by-val to pointer
* doc: possibly multi-line comment


### TypeAuto (auto)
Placeholder for an unspecified (auto derived) type

    My only occur where explicitly allowed.
    

Fields:


### TypeBase
Base type

    One of: void, bool, r32, r64, u8, u16, u32, u64, s8, s16, s32, s64
    

Fields:
* base_type_kind [KIND]: one of: [SINT, S8, S16, S32, S64, UINT, U8, U16, U32, U64, R32, R64, BOOL, TYPEID, VOID, NORET](#base-type-kind)


### TypeFun (funtype)
A function signature

    The `FunParam.name` field is ignored and should be `_`
    

Fields:
* params [LIST]: function parameters and/or comments
* result [NODE]: return type


### TypeOf (type_of)
(Static) type of the expression. Computed at compile-time.
    The underlying expression is not evaluated.
    

Fields:
* expr [NODE]: expression


### TypePtr
Pointer type
    

Fields:
* type [NODE]: type expression

Flags:
* mut: is mutable


### TypeSpan (span)
A span (view) of a vec with compile-time unknown dimensions

    Internally, this is tuple of `start` and `length`
    (mutable/non-mutable)"union
    

Fields:
* type [NODE]: type expression

Flags:
* mut: is mutable


### TypeUnion (union)
Union types (tagged unions)

    Unions are "auto flattening", e.g.
    union(a, union(b,c), union(a, d)) == union(a, b, c, d)

    union! indicates an untagged union
    

Fields:
* types [LIST]: union types

Flags:
* untagged: union type is untagged


### TypeUnionDelta (union_delta)
Type resulting from the difference of TypeUnion and a non-empty subset sets of its members
    

Fields:
* type [NODE]: type expression
* subtrahend [NODE]: type expression


### TypeVec (vec)
An array of the given type and `size`

    

Fields:
* size [NODE]: compile-time constant size
* type [NODE]: type expression


## Statement Node Details

### Case (case)
Single case of a Cond statement

Fields:
* cond [NODE]: conditional expression must evaluate to a boolean
* body [LIST]: new scope: statement list and/or comments

Flags:
* doc: possibly multi-line comment


### DefEnum (enum)
Enum definition

Allowed at top level only

Fields:
* name [NAME]: name of the object
* base_type_kind [KIND]: one of: [SINT, S8, S16, S32, S64, UINT, U8, U16, U32, U64, R32, R64, BOOL, TYPEID, VOID, NORET](#base-type-kind)
* items [LIST]: enum items and/or comments

Flags:
* pub: has public visibility
* doc: possibly multi-line comment


### DefFun (fun)
Function definition

    `init` and `fini` indicate module initializer/finalizers

    `extern` indicates a prototype and hence the function body must be empty.

    `cdecl` disables name mangling

    `ref`  fun may be assigned to a variable (i.e. its address may be taken)
     

Allowed at top level only

Fields:
* name [NAME]: name of the object
* params [LIST]: function parameters and/or comments
* result [NODE]: return type
* body [LIST]: new scope: statement list and/or comments

Flags:
* init: run function at startup
* fini: run function at shutdown
* extern: is external function (empty body)
* cdecl: use c-linkage (no module prefix)
* poly: is polymorphic function
* pub: has public visibility
* ref: address may be taken
* doc: possibly multi-line comment


### DefGlobal (global)
Variable definition at global scope (DefVar is used for local scope)

    Allocates space in static memory and initializes it with `initial_or_undef`.
    `let!` makes the allocated space read/write otherwise it is readonly.
    The attribute `ref` allows the address of the variable to be taken and prevents register allocation.
    

Allowed at top level only

Fields:
* name [NAME]: name of the object
* type_or_auto [NODE]: type expression
* initial_or_undef_or_auto [NODE] (default ValAuto): initializer

Flags:
* pub: has public visibility
* mut: is mutable
* ref: address may be taken
* cdecl: use c-linkage (no module prefix)
* doc: possibly multi-line comment


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
* name [NAME]: name of the object
* macro_result_kind [KIND]: one of: [STMT, STMT_LIST, EXPR, EXPR_LIST, TYPE](#macro-result-kind)
* params_macro [LIST]: macro parameters
* gen_ids [LIST]: name placeholder ids to be generated at macro instantiation time
* body_macro [LIST]: new scope: macro statments/expression

Flags:
* builtin: module is the builtin module
* pub: has public visibility
* doc: possibly multi-line comment


### DefMod (module)
Module Definition

    The module is a template if `params` is non-empty

    ordering is used to put the modules in a deterministic order
    

Fields:
* name [NAME]: name of the object
* params_mod [LIST]: module template parameters
* body_mod [LIST]: toplevel module definitions and/or comments

Flags:
* doc: possibly multi-line comment
* builtin: module is the builtin module


### DefRec (rec)
Record definition

Allowed at top level only

Fields:
* name [NAME]: name of the object
* fields [LIST]: record fields and/or comments

Flags:
* pub: has public visibility
* doc: possibly multi-line comment


### DefType (type)
Type definition

    A `wrapped` gives the underlying type a new name that is not type compatible.
    To convert between the two use an `as` cast expression.

    Note, unions cannot be wrapped.
    

Allowed at top level only

Fields:
* name [NAME]: name of the object
* type [NODE]: type expression

Flags:
* pub: has public visibility
* wrapped: is wrapped type (forces type equivalence by name)
* doc: possibly multi-line comment


### DefVar (let)
Variable definition at local scope (DefGlobal is used for global scope)

    Allocates space on stack (or in a register) and initializes it with `initial_or_undef_or_auto`.
    `let!` makes the allocated space read/write otherwise it is readonly.
    The attribute `ref` allows the address of the variable to be taken and prevents register allocation.

    

Fields:
* name [NAME]: name of the object
* type_or_auto [NODE]: type expression
* initial_or_undef_or_auto [NODE] (default ValAuto): initializer

Flags:
* mut: is mutable
* ref: address may be taken
* doc: possibly multi-line comment


### EnumVal
 Enum element.

     `value: ValAuto` means previous value + 1

Fields:
* name [NAME]: name of the object
* value_or_auto [NODE] (default ValAuto): enum constant or auto

Flags:
* doc: possibly multi-line comment


### Import (import)
Import another Module from `path` as `name`

Fields:
* name [NAME]: name of the object
* path [STR] (default ""): TBD
* args_mod [LIST] (default list): module arguments

Flags:
* doc: possibly multi-line comment


### MacroFor (mfor)
Macro for-loop like statement

    loops over the macro parameter `name_list` which must be a list and
    binds each list element to `name` while expanding the AST nodes in `body_for`.
    

Fields:
* name [NAME]: name of the object
* name_list [NAME]: name of the object list
* body_for [LIST]: statement list for macro_loop

Flags:
* doc: possibly multi-line comment


### ModParam
Module Parameters

Fields:
* name [NAME]: name of the object
* mod_param_kind [KIND]: one of: [CONST_EXPR, TYPE](#modparam-kind)

Flags:
* doc: possibly multi-line comment


### RecField
Record field

    All fields must be explicitly initialized. Use `ValUndef` in performance
    sensitive situations.
    

Fields:
* name [NAME]: name of the object
* type [NODE]: type expression

Flags:
* doc: possibly multi-line comment


### StmtAssignment (=)
Assignment statement

Fields:
* lhs [NODE]: l-value expression
* expr_rhs [NODE]: rhs of assignment

Flags:
* doc: possibly multi-line comment


### StmtBlock (block)
Block statement.

    if `label` is non-empty, nested break/continue statements can target this `block`.
    

Fields:
* label [NAME]: block  name (if not empty)
* body [LIST]: new scope: statement list and/or comments

Flags:
* doc: possibly multi-line comment


### StmtBreak (break)
Break statement

    use "" if the target is the nearest for/while/block 

Fields:
* target [NAME] (default NAME): name of enclosing while/for/block to brach to (empty means nearest)

Flags:
* doc: possibly multi-line comment


### StmtCompoundAssignment
Compound assignment statement

    Note: this does not support pointer inc/dec
    

Fields:
* binary_expr_kind [KIND]: one of: [ADD, SUB, DIV, MUL, MOD, MIN, MAX, SHR, SHL, ROTR, ROTL, AND, OR, XOR, EQ, NE, LT, LE, GT, GE, ANDSC, ORSC, PDELTA](#expr2-kind)
* lhs [NODE]: l-value expression
* expr_rhs [NODE]: rhs of assignment

Flags:
* doc: possibly multi-line comment


### StmtCond (cond)
Multicase if-elif-else statement

Fields:
* cases [LIST]: list of case statements

Flags:
* doc: possibly multi-line comment


### StmtContinue (continue)
Continue statement

    use "" if the target is the nearest for/while/block 

Fields:
* target [NAME] (default NAME): name of enclosing while/for/block to brach to (empty means nearest)

Flags:
* doc: possibly multi-line comment


### StmtDefer (defer)
Defer statement

    Note: defer body's containing return statments have
    non-straightforward semantics.
    

Fields:
* body [LIST]: new scope: statement list and/or comments

Flags:
* doc: possibly multi-line comment


### StmtExpr (do)
Expression statement

    Turns an expression (typically a call) into a statement
    

Fields:
* expr [NODE]: expression

Flags:
* doc: possibly multi-line comment


### StmtIf (if)
If statement

Fields:
* cond [NODE]: conditional expression must evaluate to a boolean
* body_t [LIST]: new scope: statement list and/or comments for true branch
* body_f [LIST]: new scope: statement list and/or comments for false branch

Flags:
* doc: possibly multi-line comment


### StmtReturn (return)
Return statement

    Returns from the first enclosing ExprStmt node or the enclosing DefFun node.
    Uses void_val if the DefFun's return type is void
    

Fields:
* expr_ret [NODE] (default ValVoid): result expression (ValVoid means no result)

Flags:
* doc: possibly multi-line comment


### StmtStaticAssert (static_assert)
Static assert statement (must evaluate to true at compile-time

Allowed at top level only

Fields:
* cond [NODE]: conditional expression must evaluate to a boolean
* message [STR] (default ""): message for assert failures

Flags:
* doc: possibly multi-line comment


### StmtTrap (trap)
Trap statement

Fields:

Flags:
* doc: possibly multi-line comment


## Value Node Details

### ValAuto (auto_val)
Placeholder for an unspecified (auto derived) value

    Used for: array dimensions, enum values, chap and range
    

Fields:


### ValCompound
A compound (Rec or Vec) literal
    e.g.
    `{[10]int : 1 = 5, 2 = 6, 77}`
    or
    `{Point3 : x = 5, y = 8, z = 12}`
    

Fields:
* type_or_auto [NODE]: type expression
* inits [LIST] (default list): rec initializers and/or comments

Flags:
* doc: possibly multi-line comment


### ValNum
Numeric constant (signed int, unsigned int, real

    Underscores in `number` are ignored. `number` can be explicitly typed via
    suffices like `_u64`, `_s16`, `_r32`.
    

Fields:
* number [STR]: a number


### ValPoint
Component of a ValCompound

    The `point` is optional and `ValAuto` if not used.
    It indicates which slot of the ValCompound is being initialized.
    For Recs it represents a field name  for Vecs an index which must be
    a compile-time constant
    

Fields:
* value_or_undef [NODE]: 
* point_or_undef [NODE] (default ValUndef): compound initializer index/field or auto (meaning next pos)

Flags:
* doc: possibly multi-line comment


### ValSpan (make_span)
A span value comprised of a pointer and length

    type and mutability is defined by the pointer
    

Fields:
* pointer [NODE]: pointer component of span
* expr_size [NODE]: expression determining the size or auto


### ValString
An vec_val encoded as a string

    type is `[strlen(string)]u8`. `string` may be escaped/raw
    

Fields:
* string [STR]: string literal


### ValUndef (undef)
Special constant to indicate *no default value*
    

Fields:


### ValVoid (void_val)
Only value inhabiting the `TypeVoid` type

    It can be used to model *null* in nullable pointers via a union type.
     

Fields:


## Expression Node Details

### Expr1
Unary expression.

Fields:
* unary_expr_kind [KIND]: one of: [NOT, NEG, ABS, SQRT](#expr1-kind)
* expr [NODE]: expression


### Expr2
Binary expression.

Fields:
* binary_expr_kind [KIND]: one of: [ADD, SUB, DIV, MUL, MOD, MIN, MAX, SHR, SHL, ROTR, ROTL, AND, OR, XOR, EQ, NE, LT, LE, GT, GE, ANDSC, ORSC, PDELTA](#expr2-kind)
* expr1 [NODE]: left operand expression
* expr2 [NODE]: right operand expression


### Expr3 (?)
Tertiary expression (like C's `? :`)
    

Fields:
* cond [NODE]: conditional expression must evaluate to a boolean
* expr_t [NODE]: expression (will only be evaluated if cond == true)
* expr_f [NODE]: expression (will only be evaluated if cond == false)


### ExprAddrOf (@)
Create a pointer to object represented by `expr`

    Pointer can optionally point to a mutable object if the
    pointee is mutable. This is indicated using `@!`.
    

Fields:
* expr_lhs [NODE]: l-value expression

Flags:
* mut: is mutable


### ExprAs (as)
Safe Cast (Conversion)

    Allowed:
    u8-u64, s8-s64 <-> u8-u64, s8-s64
    u8-u64, s8-s64 -> r32-r64  (note: one way only)
    

Fields:
* expr [NODE]: expression
* type [NODE]: type expression


### ExprBitCast (bitwise_as)
Bit cast.

    Type must have same size and alignment as type of item

    s32,u32,f32 <-> s32,u32,f32
    s64,u64, f64 <-> s64,u64, f64
    sint, uint <-> ptr(x)
    ptr(a) <-> ptr(b)
    (Probably not true anymore: It is also ok to bitcast complex objects like recs
    

Fields:
* expr [NODE]: expression
* type [NODE]: type expression


### ExprCall
Function call expression.
    

Fields:
* callee [NODE]: expression evaluating to the function to be called
* args [LIST]: function call arguments


### ExprDeref (^)
Dereference a pointer represented by `expr`

Fields:
* expr [NODE]: expression


### ExprField (.)
Access field in expression representing a record or the specific EnumVal within a DefEnum

    The second kind of use involving enums is eliminated early on during partial evaluation.
    So it will never be encountered by optimizations.
    

Fields:
* container [NODE]: vec and span
* field [NODE]: record field


### ExprFront (front)
Address of the first element of an vec or span

    Similar to `@container[0]` but will not fail if container has zero size
    If the underlying container is mutable, then `front!` can be  used to
    obtain a mutable pointer.
    

Fields:
* container [NODE]: vec and span

Flags:
* mut: is mutable
* preserve_mut: result type is mutable if underlying type is


### ExprIndex (at)
Optionally unchecked indexed access of vec or span
    

Fields:
* container [NODE]: vec and span
* expr_index [NODE]: expression determining the index to be accessed

Flags:
* unchecked: array acces is not checked


### ExprIs (is)
Test actual expression (run-time) type

    Typically used when `expr` is a tagged union type.
    Otherwise, the node can be evaluated at compile-time/ constant folded.

    `type` can be a tagged union itself.
    

Fields:
* expr [NODE]: expression
* type [NODE]: type expression


### ExprLen (len)
Length of vec or span

    Result type is `uint`.
    

Fields:
* container [NODE]: vec and span


### ExprNarrow (narrow_as)
Narrowing Cast (for unions)

    `narrow_as!` forces an unchecked narrowing
    Note: a narrow_as can be an l-value
    

Fields:
* expr [NODE]: expression
* type [NODE]: type expression

Flags:
* unchecked: array acces is not checked


### ExprOffsetof (offset_of)
Byte offset of field in record types

    Result has type `uint`

Fields:
* type [NODE]: type expression
* field [NODE]: record field


### ExprParen
Used for preserving parenthesis in the source
    

Fields:
* expr [NODE]: expression


### ExprPointer
Pointer arithmetic expression - optionally bound checked..

Fields:
* pointer_expr_kind [KIND]: one of: [INCP, DECP](#pointerop-kind)
* expr1 [NODE]: left operand expression
* expr2 [NODE]: right operand expression
* expr_bound_or_undef [NODE] (default ValUndef): 


### ExprSizeof (size_of)
Byte size of type

    Result has type is `uint`

Fields:
* type [NODE]: type expression


### ExprSrcLoc (srcloc)
Source Location encoded as string

    expr is not evaluated but just used for its x_srcloc
    

Fields:
* expr [NODE]: expression


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


### ExprTypeId (typeid_of)
TypeId of type

    Result has type is `typeid`

Fields:
* type [NODE]: type expression


### ExprUnionTag (union_tag)
Typetag of tagged union type

    result has type is `typeid`

Fields:
* expr [NODE]: expression


### ExprUnionUntagged (union_untagged)
Untagged union portion of tagged union type

    Result has type untagged union

Fields:
* expr [NODE]: expression


### ExprUnwrap (unwrap)
Cast: enum/wrapped -> underlying type
    

Fields:
* expr [NODE]: expression


### ExprWiden (widen_as)
Widening Cast (for unions)

    Usually this is implicit
    

Fields:
* expr [NODE]: expression
* type [NODE]: type expression


### ExprWrap (wrap_as)
Cast: underlying type -> enum/wrapped
    

Fields:
* expr [NODE]: expression
* type [NODE]: type expression


## Macro Node Details

### EphemeralList
Only exist in the context of macro parameters:
       STMT_LIST, EXPR_LIST, EXPR_LIST_REST
       and is not used after macro expansion


    

Fields:
* args [LIST]: function call arguments

Flags:
* colon: colon style list


### MacroId
Placeholder for a parameter

    This node will be expanded with the actual argument
    

Fields:
* name [NAME]: name of the object


### MacroInvoke
Macro Invocation

Fields:
* name [NAME]: name of the object
* args [LIST]: function call arguments

Flags:
* doc: possibly multi-line comment


### MacroParam
Macro Parameter

Fields:
* name [NAME]: name of the object
* macro_param_kind [KIND]: one of: [ID, EXPR, FIELD, TYPE, ID_DEF, STMT_LIST, EXPR_LIST_REST](#macro-param-kind)

Flags:
* doc: possibly multi-line comment

## Enum Details

### Expr1 Kind

|Kind|Abbrev|
|----|------|
|NOT       |!|
|NEG       |neg|
|ABS       |abs|
|SQRT      |sqrt|

### Expr2 Kind

|Kind|Abbrev|
|----|------|
|ADD       |+|
|SUB       |-|
|DIV       |/|
|MUL       |*|
|MOD       |%|
|MIN       |min|
|MAX       |max|
|SHR       |>>|
|SHL       |<<|
|ROTR      |>>>|
|ROTL      |<<<|
|AND       |&|
|OR        |||
|XOR       |~|
|EQ        |==|
|NE        |!=|
|LT        |<|
|LE        |<=|
|GT        |>|
|GE        |>=|
|ANDSC     |&&|
|ORSC      ||||
|PDELTA    |ptr_diff|

### ExprPointer Kind

|Kind|Abbrev|
|----|------|
|INCP      |ptr_inc|
|DECP      |ptr_dec|

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
|BOOL      |
|TYPEID    |
|VOID      |
|NORET     |

### ModParam Kind

|Kind|
|----|
|CONST_EXPR|
|TYPE      |

### MacroParam Kind

|Kind|
|----|
|ID        |
|EXPR      |
|FIELD     |
|TYPE      |
|ID_DEF    |
|STMT_LIST |
|EXPR_LIST_REST|

### MacroResult Kind

|Kind|
|----|
|STMT      |
|STMT_LIST |
|EXPR      |
|EXPR_LIST |
|TYPE      |
