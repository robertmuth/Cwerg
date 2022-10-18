## Abstract Syntax Tree (AST) Nodes used by Cwerg

WIP 


### Auto
placeholder for an unspecified value or type

    They are only allowed when explicitly mentioned

### Comment
Comment are proper AST nodes and can only occur in certain parts of the tree

Fields:
* comment [STR]: comment

### DefConst
Constant definition

Fields:
* pub [FLAG]: has public visibility
* name [STR]: name of the object
* type_or_auto [NODE]: type expression
* value [NODE]: 

### DefEnum
Enum definition

Fields:
* pub [FLAG]: has public visibility
* name [STR]: name of the object
* base_type_kind [KIND]: TBD
* items [LIST]: enum items

### DefFun
Function fefinition

Creates a new scope

Fields:
* init [FLAG]: run function at startup
* fini [FLAG]: run function at shutdown
* pub [FLAG]: has public visibility
* extern [FLAG]: is external function (empty body)
* name [STR]: name of the object
* params [LIST]: function parameters
* result [NODE]: return type
* body [LIST]: statement list

### DefMod
Module Definition

    The module is a template if `params` is non-empty

Fields:
* pub [FLAG]: has public visibility
* name [STR]: name of the object
* params_mod [LIST]: module template parameters
* body_mod [LIST]: toplevel module definitions

### DefRec
Record definition

Fields:
* pub [FLAG]: has public visibility
* name [STR]: name of the object
* fields [LIST]: record fields

### DefType
Type definition

    `wrapped` forces by-name equivalence).
    

Fields:
* pub [FLAG]: has public visibility
* wrapped [FLAG]: is wrapped type (uses name equivalence
* name [STR]: name of the object
* type [NODE]: type expression

### DefVar
Variable definition

Fields:
* pub [FLAG]: has public visibility
* mut [FLAG]: is mutable
* name [STR]: name of the object
* type_or_auto [NODE]: type expression
* initial [NODE]: initializer (must be compile-time constant)

### EnumVal
 Enum element.

     `value: ValAuto` means previous value + 1

Fields:
* name [STR]: name of the object
* value [NODE]: 

### Expr1
Unary expression.

Fields:
* unary_expr_kind [KIND]: TBD
* expr [NODE]: expression

### Expr2
Binary expression.

Fields:
* binary_expr_kind [KIND]: TBD
* expr1 [NODE]: left operand expression
* expr2 [NODE]: righ operand expression

### Expr3
Tertiary expression (like C's `? :`) 

Fields:
* cond [NODE]: conditional expression must evaluate to a boolean
* expr_t [NODE]: expression (will only be evaluated if cond == true)
* expr_f [NODE]: expression (will only be evaluated if cond == false)

### ExprAddrOf
Create a pointer to object represented by `expr`

Fields:
* expr [NODE]: expression

### ExprBitCastAs
Bit cast.

    Type must have saame size as type of item

Fields:
* type [NODE]: type expression
* expr [NODE]: expression

### ExprCall
Function call expression.

Fields:
* callee [NODE]: expression evaluating to the function to be called
* args [LIST]: function call arguments

### ExprCastAs
Cast

    number <-> number, number -> enum,  val -> wrapped val

Fields:
* type [NODE]: type expression
* expr [NODE]: expression

### ExprChop
Slicing expression of array or slice

Fields:
* container [NODE]: array and slice
* start [NODE]: desired start of slice
* width [NODE]: desired width of slice

### ExprDeref
Dereference a pointer represented by `expr`

Fields:
* expr [NODE]: expression

### ExprField
Access field in expression representing a record.

Fields:
* container [NODE]: array and slice
* field [STR]: record field

### ExprIndex
Checked indexed access of array or slice 

Fields:
* container [NODE]: array and slice
* expr_index [NODE]: expression determining the index to be accessed

### ExprLen
Length of array or slice

Fields:
* container [NODE]: array and slice

### ExprOffsetof
Byte offset of field in record types

    Type is `uint`

Fields:
* type [NODE]: type expression
* field [STR]: record field

### ExprParen
Used for preserving parenthesis in the source

Fields:
* expr [NODE]: expression

### ExprRange
Range expression for simple for-loops

    Modelled after Python's `range`, e.g.
    Range(end=5) = [0, 1, 2, 3, 4]
    Range(end=5, start=2) = [2, 3, 4]
    Range(end=5, start=1, step=2) = [1, 3]
    Range(end=1, start=5, step=-2) = [5, 3]
    

Fields:
* end [NODE]: range end
* begin [NODE]: range begin: `Auto` => 0
* step [NODE]: range step, `Auto` => 1

### ExprSizeof
Byte size of type

    Type is `uint`

Fields:
* expr [NODE]: expression

### FieldVal
Used for rec initialization, e.g. `.imag = 5`

Fields:
* field [STR]: record field
* value [NODE]: 

### FunParam
Function parameter

Fields:
* name [STR]: name of the object
* type [NODE]: type expression

### Id
Ids represent types, variables, constants, functions, modules

    They may contain a path component indicating which modules they reference.
    

Fields:
* name [STR]: name of the object
* path [STR]: TBD

### IndexVal
Used for array initialization, e.g. `.1 = 5`

Fields:
* index [STR]: initializer index
* value [NODE]: 

### ModParam
Module Parameters

Fields:
* name [STR]: name of the object
* mod_param_kind [KIND]: TBD

### RecField
Record field

    `initial` must be a compile-time constant or `ValUndef`

Fields:
* name [STR]: name of the object
* type [NODE]: type expression
* initial [NODE]: initializer (must be compile-time constant)

### StmtAssert
Assert statement

Fields:
* cond [NODE]: conditional expression must evaluate to a boolean
* message [STR]: message for assert failures

### StmtAssignment
Assignment statement

Fields:
* assignment_kind [KIND]: TBD
* lhs [NODE]: l-value expression
* expr [NODE]: expression

### StmtAssignment2
Compound assignment statement

Fields:
* assignment_kind [KIND]: TBD
* lhs [NODE]: l-value expression
* expr [NODE]: expression

### StmtBlock
Block statement.

    if `label` is non-empty, nested break/continue statements can target this `block`.
    

Creates a new scope

Fields:
* label [STR]: block  name (if not empty)
* body [LIST]: statement list

### StmtBreak
Break statement

    use "" if the target is the nearest for/while/block 

Fields:
* target [STR]: name of enclosing while/for/block to brach to (empty means nearest)

### StmtContinue
Continue statement

    use "" if the target is the nearest for/while/block 

Fields:
* target [STR]: name of enclosing while/for/block to brach to (empty means nearest)

### StmtDefer
Defer statement

    Note: defer body's containing return statments have
    non-straightforward semantics.
    

Creates a new scope

Fields:
* body [LIST]: statement list

### StmtExpr
Expression statement

    If expression does not have type void, `discard` must be `true`
    

Fields:
* discard [FLAG]: ignore non-void expression
* expr [NODE]: expression

### StmtFor
For statement.

    Defines the non-mut variable `name`.
    

Creates a new scope

Fields:
* name [STR]: name of the object
* type_or_auto [NODE]: type expression
* range [NODE]: range expression
* body [LIST]: statement list

### StmtIf
If statement

Creates a new scope

Fields:
* cond [NODE]: conditional expression must evaluate to a boolean
* body_t [LIST]: statement list
* body_f [LIST]: statement list

### StmtReturn
Return statement

    Use `void` value if the function's return type is `void`
    

Fields:
* expr_ret [NODE]: result expression (ValVoid means no result)

### StmtWhile
While statement.
    

Creates a new scope

Fields:
* cond [NODE]: conditional expression must evaluate to a boolean
* body [LIST]: statement list

### TypeArray
An array of the given `size`

    which must be evaluatable as a compile time constant

Fields:
* size [NODE]: compile-time constant size
* type [NODE]: type expression

### TypeBase
Base type (void, r32, r64, u8, u16, u32, u64, s8 ...)

Fields:
* base_type_kind [KIND]: TBD

### TypeFun
A function signature

    The `FunParam.name` field is ignored and should be `_`
    

Fields:
* params [LIST]: function parameters
* result [NODE]: return type

### TypePtr
Pointer type (mutable/non-mutable)

Fields:
* mut [FLAG]: is mutable
* type [NODE]: type expression

### TypeSlice
A view of an array with compile time unknown dimentions

    Internally, this is tuple of `start` and `length`
    (mutable/non-mutable)
    

Fields:
* mut [FLAG]: is mutable
* type [NODE]: type expression

### TypeSum
Sum types are tagged unions

    Sums are "auto flattening", e.g.
    Sum(a, Sum(b,c), Sum(a, d)) = Sum(a, b, c, d)
    

Fields:
* types [LIST]: union types

### ValArray
An array literal

    `[10]int{.1 = 5, .2 = 6}`
    

Fields:
* type [NODE]: type expression
* expr_size [NODE]: expression determining the size or auto
* inits_array [LIST]: array initializers

### ValArrayString
An array value encoded as a string

    type is `u8[strlen(string)]`. `string` may be escaped/raw
    

Fields:
* raw [FLAG]: ignore escape sequences in string
* string [STR]: string literal

### ValFalse
Bool constant `false`

### ValNum
Numeric constant (signed int, unsigned int, real

    Underscores in `number` are ignored. `number` can be explicitly types via
    suffices like `_u64`, `_s16`, `_r32`.
    

Fields:
* number [STR]: a number

### ValRec
A record literal

    `complex{.imag = 5, .real = 1}`
    

Fields:
* type [NODE]: type expression
* inits_rec [LIST]: record initializers

### ValTrue
Bool constant `true`

### ValUndef
Special constant to indiciate *no default value*

### ValVoid
The ValValue is the only value inhabiting the `TypeVoid` type

    It can be used to model *null* in nullable pointers via a sum type.
     
