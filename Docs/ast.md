## Abstract Syntax Tree (AST) Nodes used by Cwerg

WIP 


### Auto
placeholder for an unspecified value or type

    They are only allowed when explicitly mentioned

### Comment
Comment are proper AST nodes and can only occur in certain parts of the tree

Fields:
* comment [str]: comment

### DefConst
Constant definition

Fields:
* pub [bool]: has public visibility
* name [str]: name of the object
* type []: 
* value []: 

### DefEnum
Enum definition

Fields:
* pub [bool]: has public visibility
* name [str]: name of the object
* base_type_kind
* items [List[]]: enum items

### DefFun
Function fefinition

Creates a new scope

Fields:
* init [bool]: run function at startup
* fini [bool]: run function at shutdown
* pub [bool]: has public visibility
* extern [bool]: is external function (empty body)
* name [str]: name of the object
* params [List[]]: function parameters
* result []: return type
* body [List[]]: statement list

### DefMod
Module Definition

    The module is a template if `params` is non-empty

Fields:
* pub [bool]: has public visibility
* name [str]: name of the object
* params_mod [List[]]: module template parameters
* body_mod [List[]]: toplevel module definitions

### DefRec
Record definition

Fields:
* pub [bool]: has public visibility
* name [str]: name of the object
* fields [List[]]: record fields

### DefType
Type definition

    `wrapped` forces by-name equivalence).
    

Fields:
* pub [bool]: has public visibility
* wrapped [bool]: is wrapped type (uses name equivalence
* name [str]: name of the object
* type []: 

### DefVar
Variable definition

Fields:
* pub [bool]: has public visibility
* mut [bool]: is mutable
* name [str]: name of the object
* type []: 
* initial []: initializer (must be compile-time constant)

### EnumVal
 Enum element.

     `value: ValAuto` means previous value + 1

Fields:
* name [str]: name of the object
* value []: 

### Expr1
Unary expression.

Fields:
* unary_expr_kind
* expr []: 

### Expr2
Binary expression.

Fields:
* binary_expr_kind
* expr1 []: 
* expr2 []: 

### Expr3
Tertiary expression (like C's `? :`) 

Fields:
* cond []: conditional expression
* expr_t []: 
* expr_f []: 

### ExprAddrOf
Create a pointer to object represented by `expr`

Fields:
* expr []: 

### ExprBitCastAs
Bit cast.

    Type must have saame size as type of item

Fields:
* type []: 
* expr []: 

### ExprCall
Function call expression.

Fields:
* callee []: 
* args [List[]]: function call arguments

### ExprCastAs
Cast

    number <-> number, number -> enum,  val -> wrapped val

Fields:
* type []: 
* expr []: 

### ExprChop
Slicing expression of array or slice

Fields:
* container []: array and slice
* start []: 
* width []: 

### ExprDeref
Dereference a pointer represented by `expr`

Fields:
* expr []: 

### ExprField
Access field in expression representing a record.

Fields:
* container []: array and slice
* field [str]: record field

### ExprIndex
Checked indexed access of array or slice 

Fields:
* container []: array and slice
* expr_index []: 

### ExprLen
Length of array or slice

Fields:
* container []: array and slice

### ExprOffsetof
Byte offset of field in record types

    Type is `uint`

Fields:
* type []: 
* field [str]: record field

### ExprParen
Used for preserving parenthesis in the source

Fields:
* expr []: 

### ExprRange
Range expression for simple for-loops

Fields:
* end []: 
* start []: 
* step []: 

### ExprSizeof
Byte size of type

    Type is `uint`

Fields:
* expr []: 

### FieldVal
Used for rec initialization {.imag = 5, .real = 1}

Fields:
* field [str]: record field
* value []: 

### FunParam
Function parameter

Fields:
* name [str]: name of the object
* type []: 

### Id
Ids represent types, variables, constants, functions, modules

    They may contain a path component indicating which modules they reference.
    

Fields:
* path [List[]]: TBD
* name [str]: name of the object

### IndexVal
Used for array initialization {.1 = 5, .2 = 6}

Fields:
* index [str]: 
* value []: 

### ModParam
Module Parameters

Fields:
* name [str]: name of the object
* mod_param_kind

### RecField
Record field

    `initial` must be a compile-time constant or `ValUndef`

Fields:
* name [str]: name of the object
* type []: 
* initial []: initializer (must be compile-time constant)

### StmtAssert
Assert statement

Fields:
* cond []: conditional expression
* message [str]: message for assert failures

### StmtAssignment
Assignment statement

Fields:
* assignment_kind
* lhs []: 
* expr []: 

### StmtAssignment2
Compound assignment statement

Fields:
* assignment_kind
* lhs []: 
* expr []: 

### StmtBlock
Block statement.

    if `label` is non-empty, nested break/continue statements can target this `block`.     
    

Creates a new scope

Fields:
* label [str]: block  name (if not empty)
* body [List[]]: statement list

### StmtBreak
Break statement

    use "" if the target is the nearest for/while/block 

Fields:
* target [str]: name of enclosing while/for/block to brach to (empty means nearest)

### StmtContinue
Continue statement

    use "" if the target is the nearest for/while/block 

Fields:
* target [str]: name of enclosing while/for/block to brach to (empty means nearest)

### StmtDefer
Defer statement

    Note: defer body's containing return statments have 
    non-straightforward semantics.
    

Creates a new scope

Fields:
* body [List[]]: statement list

### StmtExpr
Expression statement

    If expression does not have type void, `discard` must be `true`
    

Fields:
* discard [bool]: ignore non-void expression
* expr []: 

### StmtFor
For statement.

    Defines the non-mut variable `name`.
    

Creates a new scope

Fields:
* name [str]: name of the object
* type []: 
* range []: range expression
* body [List[]]: statement list

### StmtIf
If statement

Creates a new scope

Fields:
* cond []: conditional expression
* body_t [List[]]: statement list
* body_f [List[]]: statement list

### StmtReturn
Return statement

    Use `void` value if the function's return type is `void`  
    

Fields:
* expr_ret []: result expression (ValVoid means no result)

### StmtWhile
While statement.
    

Creates a new scope

Fields:
* cond []: conditional expression
* body [List[]]: statement list

### TypeArray
An array of the given `size` 

    which must be evaluatable as a compile time constant

Fields:
* size []: 
* type []: 

### TypeBase
Base type (void, r32, r64, u8, u16, u32, u64, s8 ...)

Fields:
* base_type_kind

### TypeFun
A function signature 

    The `FunParam.name` field is ignored and should be `_`
    

Fields:
* params [List[]]: function parameters
* result []: return type

### TypePtr
Pointer type (mutable/non-mutable)

Fields:
* mut [bool]: is mutable
* type []: 

### TypeSlice
A view of an array with compile time unknown dimentions

    Internally, this is tuple of `start` and `length`
    (mutable/non-mutable)
    

Fields:
* mut [bool]: is mutable
* type []: 

### TypeSum
Sum type

    Sum types are tagged unions and "auto flattening", e.g.
    Sum(a, Sum(b,c), Sum(a, d)) = Sum(a, b, c, d)
    

Fields:
* types [List[]]: union types

### ValArray
An array literal

Fields:
* type []: 
* size []: 
* inits_array [List[]]: array initializers

### ValArrayString
An array value encoded as a string 

    type is `u8[strlen(string)]`. `string` may be escaped/raw
    

Fields:
* raw [bool]: ignore escape sequences in string
* string [str]: string literal

### ValFalse
Bool constant `false`

### ValNum
Numeric constant (signed int, unsigned int, real

    Underscores in `number` are ignored. `number` can be explicitly types via
    suffices like `_u64`, `_s16`, `_r32`.
    

Fields:
* number [str]: a number

### ValRec
A record literal

Fields:
* type []: 
* inits_rec [List[]]: record initializers

### ValTrue
Bool constant `true`

### ValUndef
Special constant to indiciate *no default value*

### ValVoid
The void value is the only value inhabiting the `TypeVoid` type

    It can be used to model *null* in nullable pointers via a sum type. 
     
