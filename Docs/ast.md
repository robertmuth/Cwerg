## Abstract Syntax Tree (AST) Nodes used by Cwerg

WIP 

## Node Overview
[Auto&nbsp;(auto)](#Auto) &ensp;
[Case&nbsp;(case)](#Case) &ensp;
[Catch&nbsp;(catch)](#Catch) &ensp;
[Comment&nbsp;(#)](#Comment) &ensp;
[DefConst&nbsp;(const)](#DefConst) &ensp;
[DefEnum&nbsp;(defenum)](#DefEnum) &ensp;
[DefFun&nbsp;(defun)](#DefFun) &ensp;
[DefMod&nbsp;(defmod)](#DefMod) &ensp;
[DefRec&nbsp;(defrec)](#DefRec) &ensp;
[DefType&nbsp;(deftype)](#DefType) &ensp;
[DefVar&nbsp;(let)](#DefVar) &ensp;
[EnumVal&nbsp;(entry)](#EnumVal) &ensp;
[Expr1](#Expr1) &ensp;
[Expr2](#Expr2) &ensp;
[Expr3&nbsp;(?)](#Expr3) &ensp;
[ExprAddrOf&nbsp;(&)](#ExprAddrOf) &ensp;
[ExprAs&nbsp;(as)](#ExprAs) &ensp;
[ExprBitCast&nbsp;(bitcast)](#ExprBitCast) &ensp;
[ExprCall&nbsp;(call)](#ExprCall) &ensp;
[ExprChop&nbsp;(chop)](#ExprChop) &ensp;
[ExprDeref&nbsp;(^)](#ExprDeref) &ensp;
[ExprField&nbsp;(.)](#ExprField) &ensp;
[ExprIndex&nbsp;(at)](#ExprIndex) &ensp;
[ExprIs&nbsp;(is)](#ExprIs) &ensp;
[ExprLen&nbsp;(len)](#ExprLen) &ensp;
[ExprOffsetof&nbsp;(offsetof)](#ExprOffsetof) &ensp;
[ExprParen](#ExprParen) &ensp;
[ExprRange&nbsp;(range)](#ExprRange) &ensp;
[ExprSizeof&nbsp;(sizeof)](#ExprSizeof) &ensp;
[ExprTryAs&nbsp;(tryas)](#ExprTryAs) &ensp;
[ExprUnsafeCast&nbsp;(cast)](#ExprUnsafeCast) &ensp;
[FieldVal](#FieldVal) &ensp;
[FunParam&nbsp;(param)](#FunParam) &ensp;
[Id](#Id) &ensp;
[Import&nbsp;(import)](#Import) &ensp;
[IndexVal](#IndexVal) &ensp;
[ModParam&nbsp;(None)](#ModParam) &ensp;
[RecField&nbsp;(field)](#RecField) &ensp;
[StmtAssert&nbsp;(assert)](#StmtAssert) &ensp;
[StmtAssignment&nbsp;(=)](#StmtAssignment) &ensp;
[StmtBlock&nbsp;(block)](#StmtBlock) &ensp;
[StmtBreak&nbsp;(break)](#StmtBreak) &ensp;
[StmtCompoundAssignment](#StmtCompoundAssignment) &ensp;
[StmtCond&nbsp;(cond)](#StmtCond) &ensp;
[StmtContinue&nbsp;(continue)](#StmtContinue) &ensp;
[StmtDefer&nbsp;(defer)](#StmtDefer) &ensp;
[StmtExpr&nbsp;(expr)](#StmtExpr) &ensp;
[StmtFor&nbsp;(for)](#StmtFor) &ensp;
[StmtIf&nbsp;(if)](#StmtIf) &ensp;
[StmtReturn&nbsp;(return)](#StmtReturn) &ensp;
[StmtTrap&nbsp;(trap)](#StmtTrap) &ensp;
[StmtWhile&nbsp;(while)](#StmtWhile) &ensp;
[Try&nbsp;(try)](#Try) &ensp;
[TypeArray](#TypeArray) &ensp;
[TypeBase](#TypeBase) &ensp;
[TypeFun&nbsp;(sig)](#TypeFun) &ensp;
[TypePtr&nbsp;(ptr)](#TypePtr) &ensp;
[TypeSlice&nbsp;(slice)](#TypeSlice) &ensp;
[TypeSum&nbsp;(union)](#TypeSum) &ensp;
[ValArray](#ValArray) &ensp;
[ValFalse](#ValFalse) &ensp;
[ValNum](#ValNum) &ensp;
[ValRec&nbsp;(rec)](#ValRec) &ensp;
[ValString](#ValString) &ensp;
[ValTrue](#ValTrue) &ensp;
[ValUndef](#ValUndef) &ensp;
[ValVoid](#ValVoid) &ensp;
## Node Details

### Auto (auto) {#Auto}
Placeholder for an unspecified value or type

    My only occur where explicitly allowed.
    

### Case (case) {#Case}
Single case of a Cond statement

Creates a new scope

Fields:
* cond [NODE]: conditional expression must evaluate to a boolean
* body [LIST]: statement list and/or comments

### Catch (catch) {#Catch}
Used with Try only

Creates a new scope

Fields:
* name [STR]: name of the object
* body_except [LIST]: statement list and/or comments when type narrowing fails

### Comment (#) {#Comment}
Comment 

    Comments are proper AST nodes and may only occur where explicitly allowed.
    They refer to the next sibling in the tree.
    

Fields:
* comment [STR]: comment

### DefConst (const) {#DefConst}
Constant definition

Allowed at top level only

Fields:
* pub [FLAG]: has public visibility
* name [STR]: name of the object
* type_or_auto [NODE]: type expression
* value [NODE]: 

### DefEnum (defenum) {#DefEnum}
Enum definition

Allowed at top level only

Fields:
* pub [FLAG]: has public visibility
* name [STR]: name of the object
* base_type_kind [KIND]: see Base Types below
* items [LIST]: enum items and/or comments

### DefFun (defun) {#DefFun}
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

### DefMod (defmod) {#DefMod}
Module Definition

    The module is a template if `params` is non-empty

Fields:
* pub [FLAG]: has public visibility
* name [STR]: name of the object
* params_mod [LIST]: module template parameters
* body_mod [LIST]: toplevel module definitions and/or comments

### DefRec (defrec) {#DefRec}
Record definition

Allowed at top level only

Fields:
* pub [FLAG]: has public visibility
* name [STR]: name of the object
* fields [LIST]: record fields and/or comments

### DefType (deftype) {#DefType}
Type definition

    

Allowed at top level only

Fields:
* pub [FLAG]: has public visibility
* wrapped [FLAG]: is wrapped type (forces type equivalence by name)
* name [STR]: name of the object
* type [NODE]: type expression

### DefVar (let) {#DefVar}
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
* initial_or_undef [NODE] (default ValUndef): initializer (must be compile-time constant)

### EnumVal (entry) {#EnumVal}
 Enum element.

     `value: ValAuto` means previous value + 1

Fields:
* name [STR]: name of the object
* value [NODE]: 

### Expr1 {#Expr1}
Unary expression.

Fields:
* unary_expr_kind [KIND]: see Expr1 Kind below
* expr [NODE]: expression

### Expr2 {#Expr2}
Binary expression.

Fields:
* binary_expr_kind [KIND]: see Expr2 Kind below
* expr1 [NODE]: left operand expression
* expr2 [NODE]: righ operand expression

### Expr3 (?) {#Expr3}
Tertiary expression (like C's `? :`) 
    

Fields:
* cond [NODE]: conditional expression must evaluate to a boolean
* expr_t [NODE]: expression (will only be evaluated if cond == true)
* expr_f [NODE]: expression (will only be evaluated if cond == false)

### ExprAddrOf (&) {#ExprAddrOf}
Create a pointer to object represented by `expr`

    Pointer can optionally point to a mutable object if the
    pointee is mutable.
    

Fields:
* mut [FLAG]: is mutable
* expr [NODE]: expression

### ExprAs (as) {#ExprAs}
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

### ExprBitCast (bitcast) {#ExprBitCast}
Bit cast.

    Type must have same size as type of item

    s32,u32,f32 <-> s32,u32,f32
    s64,u64, f64 <-> s64,u64, f64
    sint, uint <-> ptr
    

Fields:
* expr [NODE]: expression
* type [NODE]: type expression

### ExprCall (call) {#ExprCall}
Function call expression.
    

Fields:
* callee [NODE]: expression evaluating to the function to be called
* args [LIST]: function call arguments

### ExprChop (chop) {#ExprChop}
Slicing expression of array or slice
    

Fields:
* container [NODE]: array and slice
* start [NODE] (default Auto): desired start of slice
* width [NODE] (default Auto): desired width of slice

### ExprDeref (^) {#ExprDeref}
Dereference a pointer represented by `expr`

Fields:
* expr [NODE]: expression

### ExprField (.) {#ExprField}
Access field in expression representing a record.
    

Fields:
* container [NODE]: array and slice
* field [STR]: record field

### ExprIndex (at) {#ExprIndex}
Checked indexed access of array or slice 
    

Fields:
* container [NODE]: array and slice
* expr_index [NODE]: expression determining the index to be accessed

### ExprIs (is) {#ExprIs}
Test actual expression type within a Sum Type

    

Fields:
* expr [NODE]: expression
* type [NODE]: type expression

### ExprLen (len) {#ExprLen}
Length of array or slice

Fields:
* container [NODE]: array and slice

### ExprOffsetof (offsetof) {#ExprOffsetof}
Byte offset of field in record types

    Type is `uint`

Fields:
* type [NODE]: type expression
* field [STR]: record field

### ExprParen {#ExprParen}
Used for preserving parenthesis in the source
    

Fields:
* expr [NODE]: expression

### ExprRange (range) {#ExprRange}
Range expression for simple for-loops

    Modelled after Python's `range`, e.g.
    Range(end=5) = [0, 1, 2, 3, 4]
    Range(end=5, start=2) = [2, 3, 4]
    Range(end=5, start=1, step=2) = [1, 3]
    Range(end=1, start=5, step=-2) = [5, 3]
    

Fields:
* end [NODE]: range end
* begin_or_auto [NODE] (default Auto): range begin: `Auto` => 0
* step_or_auto [NODE] (default Auto): range step, `Auto` => 1

### ExprSizeof (sizeof) {#ExprSizeof}
Byte size of type

    Type is `uint`

Fields:
* expr [NODE]: expression

### ExprTryAs (tryas) {#ExprTryAs}
Narrow a `expr` which is of Sum to `type` 

    If the is not possible return `default_or_undef` if that is not undef
    or trap otherwise.

    

Fields:
* expr [NODE]: expression
* type [NODE]: type expression
* default_or_undef [NODE]: value if type narrowing fail or trap if undef

### ExprUnsafeCast (cast) {#ExprUnsafeCast}
Unsafe Cast

    Allowed:
    ptr a <-> ptr b

    

Fields:
* expr [NODE]: expression
* type [NODE]: type expression

### FieldVal {#FieldVal}
Part of rec literal

    e.g. `.imag = 5`
    If field is empty use `first field` or `next field`.
    

Fields:
* value [NODE]: 
* init_field [STR] (default ""): initializer field or empty (empty means next field)

### FunParam (param) {#FunParam}
Function parameter

    

Fields:
* name [STR]: name of the object
* type [NODE]: type expression

### Id {#Id}
Refers to a type, variable, constant, function, module by name.

    Ids may contain a path component indicating which modules they reference.
    

Fields:
* name [STR]: name of the object
* path [STR] (default ""): TBD

### Import (import) {#Import}
Import another Module

Fields:
* name [STR]: name of the object
* alias [STR] (default ""): name of imported module to be used instead of given name

### IndexVal {#IndexVal}
Part of an array literal

    e.g. `.1 = 5`
    If index is empty use `0` or `previous index + 1`.
    

Fields:
* value_or_undef [NODE]: 
* init_index [STR] (default ""): initializer index or empty (empty mean next index)

### ModParam (None) {#ModParam}
Module Parameters

Fields:
* name [STR]: name of the object
* mod_param_kind [KIND]: see ModParam Kind below

### RecField (field) {#RecField}
Record field

    All fields must be explicitly initialized. Use `ValUndef` in performance 
    sensitive situations.
    

Fields:
* name [STR]: name of the object
* type [NODE]: type expression
* initial_or_undef [NODE] (default ValUndef): initializer (must be compile-time constant)

### StmtAssert (assert) {#StmtAssert}
Assert statement

Fields:
* cond [NODE]: conditional expression must evaluate to a boolean
* message [STR]: message for assert failures

### StmtAssignment (=) {#StmtAssignment}
Assignment statement

Fields:
* lhs [NODE]: l-value expression
* expr [NODE]: expression

### StmtBlock (block) {#StmtBlock}
Block statement.

    if `label` is non-empty, nested break/continue statements can target this `block`.
    

Creates a new scope

Fields:
* label [STR]: block  name (if not empty)
* body [LIST]: statement list and/or comments

### StmtBreak (break) {#StmtBreak}
Break statement

    use "" if the target is the nearest for/while/block 

Fields:
* target [STR] (default ""): name of enclosing while/for/block to brach to (empty means nearest)

### StmtCompoundAssignment {#StmtCompoundAssignment}
Compound assignment statement

Fields:
* assignment_kind [KIND]: see StmtCompoundAssignment Kind below
* lhs [NODE]: l-value expression
* expr [NODE]: expression

### StmtCond (cond) {#StmtCond}
Multicase if-elif-else statement

Fields:
* cases [LIST]: list of case statements

### StmtContinue (continue) {#StmtContinue}
Continue statement

    use "" if the target is the nearest for/while/block 

Fields:
* target [STR] (default ""): name of enclosing while/for/block to brach to (empty means nearest)

### StmtDefer (defer) {#StmtDefer}
Defer statement

    Note: defer body's containing return statments have
    non-straightforward semantics.
    

Creates a new scope

Fields:
* body [LIST]: statement list and/or comments

### StmtExpr (expr) {#StmtExpr}
Expression statement

    If expression does not have type void, `discard` must be `true`
    

Fields:
* discard [FLAG]: ignore non-void expression
* expr [NODE]: expression

### StmtFor (for) {#StmtFor}
For statement.

    Defines the non-mut variable `name`.
    

Creates a new scope

Fields:
* name [STR]: name of the object
* type_or_auto [NODE]: type expression
* range [NODE]: range expression
* body [LIST]: statement list and/or comments

### StmtIf (if) {#StmtIf}
If statement

Creates a new scope

Fields:
* cond [NODE]: conditional expression must evaluate to a boolean
* body_t [LIST]: statement list and/or comments for true branch
* body_f [LIST]: statement list and/or comments for false branch

### StmtReturn (return) {#StmtReturn}
Return statement

    Use `void` value if the function's return type is `void`
    

Fields:
* expr_ret [NODE] (default ValVoid): result expression (ValVoid means no result)

### StmtTrap (trap) {#StmtTrap}
Trap statement

### StmtWhile (while) {#StmtWhile}
While statement.
    

Creates a new scope

Fields:
* cond [NODE]: conditional expression must evaluate to a boolean
* body [LIST]: statement list and/or comments

### Try (try) {#Try}
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

### TypeArray {#TypeArray}
An array of the given type and `size`

    Size must be evaluatable as a compile time constant

Fields:
* size [NODE]: compile-time constant size
* type [NODE]: type expression

### TypeBase {#TypeBase}
Base type 

    One of: void, bool, r32, r64, u8, u16, u32, u64, s8, s16, s32, s64    
    

Fields:
* base_type_kind [KIND]: see Base Types below

### TypeFun (sig) {#TypeFun}
A function signature

    The `FunParam.name` field is ignored and should be `_`
    

Fields:
* params [LIST]: function parameters and/or comments
* result [NODE]: return type

### TypePtr (ptr) {#TypePtr}
Pointer type
    

Fields:
* mut [FLAG]: is mutable
* type [NODE]: type expression

### TypeSlice (slice) {#TypeSlice}
A view/slice of an array with compile time unknown dimensions

    Internally, this is tuple of `start` and `length`
    (mutable/non-mutable)
    

Fields:
* mut [FLAG]: is mutable
* type [NODE]: type expression

### TypeSum (union) {#TypeSum}
Sum types (tagged unions)

    Sums are "auto flattening", e.g.
    Sum(a, Sum(b,c), Sum(a, d)) = Sum(a, b, c, d)
    

Fields:
* types [LIST]: union types

### ValArray {#ValArray}
An array literal

    `[10]int{.1 = 5, .2 = 6, 77}`
    

Fields:
* type [NODE]: type expression
* expr_size [NODE]: expression determining the size or auto
* inits_array [LIST]: array initializers and/or comments

### ValFalse {#ValFalse}
Bool constant `false`

### ValNum {#ValNum}
Numeric constant (signed int, unsigned int, real

    Underscores in `number` are ignored. `number` can be explicitly typed via
    suffices like `_u64`, `_s16`, `_r32`.
    

Fields:
* number [STR]: a number

### ValRec (rec) {#ValRec}
A record literal

    `E.g.: complex{.imag = 5, .real = 1}`
    

Fields:
* type [NODE]: type expression
* inits_rec [LIST]: record initializers and/or comments

### ValString {#ValString}
An array value encoded as a string

    type is `[strlen(string)]u8`. `string` may be escaped/raw
    

Fields:
* raw [FLAG]: ignore escape sequences in string
* string [STR]: string literal

### ValTrue {#ValTrue}
Bool constant `true`

### ValUndef {#ValUndef}
Special constant to indiciate *no default value*
    

### ValVoid {#ValVoid}
Only value inhabiting the `TypeVoid` type

    It can be used to model *null* in nullable pointers via a sum type.
     
## Enum Details

### Expr1 Kind {#UNARY_EXPR_KIND}

|Kind|Abbrev|
|----|------|
|NOT       |!|
|MINUS     |~|
|NEG       |neg|

### Expr2 Kind {#BINARY_EXPR_KIND}

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

### StmtCompoundAssignment Kind {#ASSIGNMENT_KIND}

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

### Base Types Kind {#BASE_TYPE_KIND}

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

### ModParam Types Kind {#MOD_PARAM_KIND}

|Kind|
|----|
|CONST     |
|MOD       |
|TYPE      |
