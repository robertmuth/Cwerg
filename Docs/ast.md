## Abstract Syntax Tree (AST) Nodes used by Cwerg

WIP 


## Node Overview
[Case&nbsp;(case)](#case-case) &ensp;
[Catch&nbsp;(catch)](#catch-catch) &ensp;
[Comment&nbsp;(#)](#comment-) &ensp;
[DefConst&nbsp;(const)](#defconst-const) &ensp;
[DefEnum&nbsp;(defenum)](#defenum-defenum) &ensp;
[DefFun&nbsp;(defun)](#deffun-defun) &ensp;
[DefMacro&nbsp;(macro)](#defmacro-macro) &ensp;
[DefMod&nbsp;(defmod)](#defmod-defmod) &ensp;
[DefRec&nbsp;(defrec)](#defrec-defrec) &ensp;
[DefType&nbsp;(deftype)](#deftype-deftype) &ensp;
[DefVar&nbsp;(let)](#defvar-let) &ensp;
[EnumVal&nbsp;(entry)](#enumval-entry) &ensp;
[Expr1](#expr1) &ensp;
[Expr2](#expr2) &ensp;
[Expr3&nbsp;(?)](#expr3-) &ensp;
[ExprAddrOf&nbsp;(&)](#expraddrof-) &ensp;
[ExprAs&nbsp;(as)](#expras-as) &ensp;
[ExprAsNot&nbsp;(asnot)](#exprasnot-asnot) &ensp;
[ExprBitCast&nbsp;(bitcast)](#exprbitcast-bitcast) &ensp;
[ExprCall&nbsp;(call)](#exprcall-call) &ensp;
[ExprChop&nbsp;(chop)](#exprchop-chop) &ensp;
[ExprDeref&nbsp;(^)](#exprderef-) &ensp;
[ExprField&nbsp;(.)](#exprfield-.) &ensp;
[ExprIndex&nbsp;(at)](#exprindex-at) &ensp;
[ExprIs&nbsp;(is)](#expris-is) &ensp;
[ExprLen&nbsp;(len)](#exprlen-len) &ensp;
[ExprOffsetof&nbsp;(offsetof)](#exproffsetof-offsetof) &ensp;
[ExprParen](#exprparen) &ensp;
[ExprRange&nbsp;(range)](#exprrange-range) &ensp;
[ExprSizeof&nbsp;(sizeof)](#exprsizeof-sizeof) &ensp;
[ExprSrcLoc&nbsp;(src_loc)](#exprsrcloc-src_loc) &ensp;
[ExprTryAs&nbsp;(tryas)](#exprtryas-tryas) &ensp;
[ExprUnsafeCast&nbsp;(cast)](#exprunsafecast-cast) &ensp;
[FieldVal](#fieldval) &ensp;
[FunParam&nbsp;(param)](#funparam-param) &ensp;
[Id&nbsp;(id)](#id-id) &ensp;
[Import&nbsp;(import)](#import-import) &ensp;
[IndexVal](#indexval) &ensp;
[MacroId&nbsp;(macro_id)](#macroid-macro_id) &ensp;
[MacroParam&nbsp;(macro_param)](#macroparam-macro_param) &ensp;
[MacroRepeat&nbsp;(macro_repeat)](#macrorepeat-macro_repeat) &ensp;
[MacroVar&nbsp;(macro_let)](#macrovar-macro_let) &ensp;
[MacroVarIndirect&nbsp;(macro_let_indirect)](#macrovarindirect-macro_let_indirect) &ensp;
[ModParam](#modparam) &ensp;
[RecField&nbsp;(field)](#recfield-field) &ensp;
[StmtAssert&nbsp;(assert)](#stmtassert-assert) &ensp;
[StmtAssignment&nbsp;(=)](#stmtassignment-) &ensp;
[StmtBlock&nbsp;(block)](#stmtblock-block) &ensp;
[StmtBreak&nbsp;(break)](#stmtbreak-break) &ensp;
[StmtCompoundAssignment](#stmtcompoundassignment) &ensp;
[StmtCond&nbsp;(cond)](#stmtcond-cond) &ensp;
[StmtContinue&nbsp;(continue)](#stmtcontinue-continue) &ensp;
[StmtDefer&nbsp;(defer)](#stmtdefer-defer) &ensp;
[StmtExpr&nbsp;(stmt)](#stmtexpr-stmt) &ensp;
[StmtFor&nbsp;(for)](#stmtfor-for) &ensp;
[StmtIf&nbsp;(if)](#stmtif-if) &ensp;
[StmtReturn&nbsp;(return)](#stmtreturn-return) &ensp;
[StmtStaticAssert&nbsp;(static_assert)](#stmtstaticassert-static_assert) &ensp;
[StmtTrap&nbsp;(trap)](#stmttrap-trap) &ensp;
[StmtWhile&nbsp;(while)](#stmtwhile-while) &ensp;
[Try&nbsp;(try)](#try-try) &ensp;
[TypeArray&nbsp;(array)](#typearray-array) &ensp;
[TypeAuto&nbsp;(auto)](#typeauto-auto) &ensp;
[TypeBase](#typebase) &ensp;
[TypeFun&nbsp;(sig)](#typefun-sig) &ensp;
[TypePtr&nbsp;(ptr)](#typeptr-ptr) &ensp;
[TypeSlice&nbsp;(slice)](#typeslice-slice) &ensp;
[TypeSum&nbsp;(union)](#typesum-union) &ensp;
[ValArray](#valarray) &ensp;
[ValAuto&nbsp;(auto_val)](#valauto-auto_val) &ensp;
[ValFalse&nbsp;(false)](#valfalse-false) &ensp;
[ValNum](#valnum) &ensp;
[ValRec&nbsp;(rec)](#valrec-rec) &ensp;
[ValString](#valstring) &ensp;
[ValTrue&nbsp;(true)](#valtrue-true) &ensp;
[ValUndef&nbsp;(undef)](#valundef-undef) &ensp;
[ValVoid&nbsp;(void_val)](#valvoid-void_val) &ensp;

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

### DefEnum (defenum)
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
* mut [FLAG]: is mutable
* size [NODE]: compile-time constant size
* type [NODE]: type expression

### TypeAuto (auto)
Placeholder for an unspecified (auto derived) type

    My only occur where explicitly allowed.
    

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

Creates a new scope

Fields:
* cond [NODE]: conditional expression must evaluate to a boolean
* body [LIST]: statement list and/or comments

### Catch (catch)
Used with Try only

Creates a new scope

Fields:
* name [STR]: name of the object
* body_except [LIST]: statement list and/or comments when type narrowing fails

### DefFun (defun)
Function definition

Creates a new scope

Allowed at top level only

Fields:
* init [FLAG]: run function at startup
* fini [FLAG]: run function at shutdown
* pub [FLAG]: has public visibility
* extern [FLAG]: is external function (empty body)
* name [STR]: name of the object
* params [LIST]: function parameters and/or comments
* result [NODE]: return type
* body [LIST]: statement list and/or comments

### DefMacro (macro)
Define a macro

Creates a new scope

Allowed at top level only

Fields:
* name [STR]: name of the object
* params_macro [LIST]: macro parameters
* body_macro [LIST]: macro statments/expression

### DefMod (defmod)
Module Definition

    The module is a template if `params` is non-empty

Fields:
* pub [FLAG]: has public visibility
* name [STR]: name of the object
* params_mod [LIST]: module template parameters
* body_mod [LIST]: toplevel module definitions and/or comments

### DefType (deftype)
Type definition

    

Allowed at top level only

Fields:
* pub [FLAG]: has public visibility
* wrapped [FLAG]: is wrapped type (forces type equivalence by name)
* name [STR]: name of the object
* type [NODE]: type expression

### DefVar (let)
Variable definition

    public visibily only makes sense for module level definitions.

    Variables must be explicitly initialized. Use `ValUndef` in performance
    sensitive situations.
    

Allowed at top level

Fields:
* pub [FLAG]: has public visibility
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

### StmtAssert (assert)
Assert statement

Fields:
* cond [NODE]: conditional expression must evaluate to a boolean
* message [STR] (default ""): message for assert failures

### StmtAssignment (=)
Assignment statement

Fields:
* lhs [NODE]: l-value expression
* expr [NODE]: expression

### StmtBlock (block)
Block statement.

    if `label` is non-empty, nested break/continue statements can target this `block`.
    

Creates a new scope

Fields:
* label [STR]: block  name (if not empty)
* body [LIST]: statement list and/or comments

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
* expr [NODE]: expression

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
    

Creates a new scope

Fields:
* body [LIST]: statement list and/or comments

### StmtExpr (stmt)
Expression statement

    If expression does not have type void, `discard` must be `true`
    

Fields:
* discard [FLAG]: ignore non-void expression
* expr [NODE]: expression

### StmtFor (for)
For statement.

    Defines the non-mut variable `name`.
    

Creates a new scope

Fields:
* name [STR]: name of the object
* type_or_auto [NODE]: type expression
* range [NODE]: range expression
* body [LIST]: statement list and/or comments

### StmtIf (if)
If statement

Creates a new scope

Fields:
* cond [NODE]: conditional expression must evaluate to a boolean
* body_t [LIST]: statement list and/or comments for true branch
* body_f [LIST]: statement list and/or comments for false branch

### StmtReturn (return)
Return statement

    Use `void` value if the function's return type is `void`
    

Fields:
* expr_ret [NODE] (default ValVoid): result expression (ValVoid means no result)

### StmtStaticAssert (static_assert)
Static assert statement (must evaluate to true at compile-time

Allowed at top level

Fields:
* cond [NODE]: conditional expression must evaluate to a boolean
* message [STR] (default ""): message for assert failures

### StmtTrap (trap)
Trap statement

### StmtWhile (while)
While statement.
    

Creates a new scope

Fields:
* cond [NODE]: conditional expression must evaluate to a boolean
* body [LIST]: statement list and/or comments

### Try (try)
Variable definition if type matches otherwise `catch`

    This is the most complex node in Cwerg. It only makes sense for `expr` that
    evaluate to a sum type `S`. Assuming that `S = Union[type, type-rest].
    The statement desugar to this:

    (let `mut` tmp auto `expr`)
    if (tmp is `type-rest`) [
        (let `catch.name` (tmp as `type-rest`)
        ...`catch.body_except`
        (trap)
    ] [])
    (let `name` auto (tmp as `type`))

    

Fields:
* mut [FLAG]: is mutable
* name [STR]: name of the object
* type [NODE]: type expression
* expr [NODE]: expression
* catch [NODE]: handler for type mismatch (implictly terminated by trap)

## Value Node Details

### DefConst (const)
Constant definition

Allowed at top level only

Fields:
* pub [FLAG]: has public visibility
* name [STR]: name of the object
* type_or_auto [NODE]: type expression
* value [NODE]: 

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

### ValArray
An array literal

    `[10]int{.1 = 5, .2 = 6, 77}`
    

Fields:
* type [NODE]: type expression
* expr_size [NODE]: expression determining the size or auto
* inits_array [LIST]: array initializers and/or comments

### ValAuto (auto_val)
Placeholder for an unspecified (auto derived) value

    Used for: array dimensions, enum values, chap and range
    

Fields:

### ValFalse (false)
Bool constant `false`

Fields:

### ValNum
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
* expr [NODE]: expression

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
* callee [NODE]: expression evaluating to the function to be called
* args [LIST]: function call arguments

### ExprChop (chop)
Slicing expression of array or slice
    

Fields:
* container [NODE]: array and slice
* start [NODE] (default ValAuto): desired start of slice (default 0)
* width [NODE] (default ValAuto): desired width of slice (default: length of container)

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

### ExprRange (range)
Range expression for simple for-loops

    Modelled after Python's `range`, e.g.
    Range(end=5) = [0, 1, 2, 3, 4]
    Range(end=5, start=2) = [2, 3, 4]
    Range(end=5, start=1, step=2) = [1, 3]
    Range(end=1, start=5, step=-2) = [5, 3]
    

Fields:
* end [NODE]: range end
* begin_or_auto [NODE] (default 0): range begin
* step_or_auto [NODE] (default 1): range step

### ExprSizeof (sizeof)
Byte size of type

    Type is `uint`

Fields:
* type [NODE]: type expression

### ExprSrcLoc (src_loc)
Source Location encoded as u32

Fields:

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

### MacroId (macro_id)
Placeholder for a parameter

    This node will be expanded with the actual argument
    

Fields:
* name [STR]: name of the object

### MacroParam (macro_param)
Macro Parameter

Fields:
* repeat [FLAG]: last macro parameter is repeated
* name [STR]: name of the object
* macro_param_kind [KIND]: see MacroParam Kind below

### MacroRepeat (macro_repeat)
Macro Repeated Statement

### MacroVar (macro_let)
Macro Variable definition with a name that will be uniquified

    Will generate a unique name inspired by the provided name to avoid accidental
    capture.

    Variable must be explicitly initialized. Use `ValUndef` in performance
    sensitive situations.
    

Fields:
* mut [FLAG]: is mutable
* name [STR]: name of the object
* type_or_auto [NODE]: type expression
* initial_or_undef [NODE] (default ValUndef): initializer

### MacroVarIndirect (macro_let_indirect)
Macro Variable definition whose name is a macro parameter


    Variable must be explicitly initialized. Use `ValUndef` in performance
    sensitive situations.
    

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
|PADD      |padd|
|PSUB      |psub|
|PDELTA    |pdelta|

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
|FLAG      |
|ID        |
|EXPR      |
|STMT_LIST |
|LAZY_EXPR |
