## Abstract Syntax Tree (AST) Nodes used by Cwerg

WIP 


### Auto
placeholder for an unspecified value or type

    They are only allowed when explicitly mentioned

### Comment
Comment are proper AST nodes and can only occur in certain parts of the tree

Fields:
* string: 

### DefConst
Constant definition

Fields:
* pub: has public visibility
* name: name of the object
* type
* value

### DefEnum
Enum definition

Fields:
* pub: has public visibility
* name: name of the object
* base_type_kind
* items

### DefFun
Function fefinition

Creates a new scope

Fields:
* init: run function at startup
* fini: run function at shutdown
* pub: has public visibility
* extern: is external function (empty body)
* name: name of the object
* params
* result
* body

### DefMod
Module Definition

    The module is a template if `params` is non-empty

Fields:
* pub: has public visibility
* name: name of the object
* params_mod
* body_mod

### DefRec
Record definition

Fields:
* pub: has public visibility
* name: name of the object
* fields

### DefType
Type definition

    `wrapped` forces by-name equivalence).
    

Fields:
* pub: has public visibility
* wrapped: is wrapped type (uses name equivalence
* name: name of the object
* type

### DefVar
Variable definition

Fields:
* pub: has public visibility
* mut: is mutable
* name: name of the object
* type
* initial

### EnumVal
 Enum element.

     `value: ValAuto` means previous value + 1

Fields:
* name: name of the object
* value

### Expr1
Unary expression.

Fields:
* unary_expr_kind
* expr

### Expr2
Binary expression.

Fields:
* binary_expr_kind
* expr1
* expr2

### Expr3
Tertiary expression (like C's `? :`) 

Fields:
* cond
* expr_t
* expr_f

### ExprAddrOf
Create a pointer to object represented by `expr`

Fields:
* expr

### ExprBitCastAs
Bit cast.

    Type must have saame size as type of item

Fields:
* type
* expr

### ExprCall
Function call expression.

Fields:
* callee
* args

### ExprCastAs
Cast

    number <-> number, number -> enum,  val -> wrapped val

Fields:
* type
* expr

### ExprChop
Slicing expression of array or slice

Fields:
* container
* start
* width

### ExprDeref
Dereference a pointer represented by `expr`

Fields:
* expr

### ExprField
Access field in expression representing a record.

Fields:
* container
* field: record field

### ExprIndex
Checked indexed access of array or slice 

Fields:
* container
* expr_index

### ExprLen
Length of array or slice

Fields:
* container

### ExprOffsetof
Byte offset of field in record types

    Type is `uint`

Fields:
* type
* field: record field

### ExprParen
Used for preserving parenthesis in the source

Fields:
* expr

### ExprRange
Range expression for simple for-loops

Fields:
* end
* start
* step

### ExprSizeof
Byte size of type

    Type is `uint`

Fields:
* expr

### FieldVal
Used for rec initialization {.imag = 5, .real = 1}

Fields:
* field: record field
* value

### FunParam
Function parameter

Fields:
* name: name of the object
* type

### Id
Ids represent types, variables, constants, functions, modules

    They may contain a path component indicating which modules they reference.
    

Fields:
* path
* name: name of the object

### IndexVal
Used for array initialization {.1 = 5, .2 = 6}

Fields:
* index: 
* value

### ModParam
Module Parameters

Fields:
* name: name of the object
* mod_param_kind

### RecField
Record field

    `initial` must be a compile-time constant or `ValUndef`

Fields:
* name: name of the object
* type
* initial

### StmtAssert
Assert statement

Fields:
* cond
* string: 

### StmtAssignment
Assignment statement

Fields:
* assignment_kind
* lhs
* expr

### StmtAssignment2
Compound assignment statement

Fields:
* assignment_kind
* lhs
* expr

### StmtBlock
Block statement.

    if `label` is non-empty, nested break/continue statements can target this `block`.     
    

Creates a new scope

Fields:
* label: block  name (if not empty)
* body

### StmtBreak
Break statement

    use "" if the target is the nearest for/while/block 

Fields:
* target: name of enclosing while/for/block to brach to (empty means nearest)

### StmtContinue
Continue statement

    use "" if the target is the nearest for/while/block 

Fields:
* target: name of enclosing while/for/block to brach to (empty means nearest)

### StmtDefer
Defer statement

    Note: defer body's containing return statments have 
    non-straightforward semantics.
    

Creates a new scope

Fields:
* body

### StmtExpr
Expression statement

    If expression does not have type void, `discard` must be `true`
    

Fields:
* discard: ignore non-void expression
* expr

### StmtFor
For statement.

    Defines the non-mut variable `name`.
    

Creates a new scope

Fields:
* name: name of the object
* type
* range
* body

### StmtIf
If statement

Creates a new scope

Fields:
* cond
* body_t
* body_f

### StmtReturn
Return statement

    Use `void` value if the function's return type is `void`  
    

Fields:
* expr_ret

### StmtWhile
While statement.
    

Creates a new scope

Fields:
* cond
* body

### TypeArray
An array of the given `size` 

    which must be evaluatable as a compile time constant

Fields:
* size
* type

### TypeBase
Base type (void, r32, r64, u8, u16, u32, u64, s8 ...)

Fields:
* base_type_kind

### TypeFun
A function signature 

    The `FunParam.name` field is ignored and should be `_`
    

Fields:
* params
* result

### TypePtr
Pointer type (mutable/non-mutable)

Fields:
* mut: is mutable
* type

### TypeSlice
A view of an array with compile time unknown dimentions

    Internally, this is tuple of `start` and `length`
    (mutable/non-mutable)
    

Fields:
* mut: is mutable
* type

### TypeSum
Sum type

    Sum types are tagged unions and "auto flattening", e.g.
    Sum(a, Sum(b,c), Sum(a, d)) = Sum(a, b, c, d)
    

Fields:
* types

### ValArray
An array literal

Fields:
* type
* size
* inits_array

### ValArrayString
An array value encoded as a string 

    type is `u8[strlen(string)]`. `string` may be escaped/raw
    

Fields:
* raw: ignore escape sequences in string
* string: 

### ValFalse
Bool constant `false`

### ValNum
Numeric constant (signed int, unsigned int, real

    Underscores in `number` are ignored. `number` can be explicitly types via
    suffices like `_u64`, `_s16`, `_r32`.
    

Fields:
* number: a number

### ValRec
A record literal

Fields:
* type
* inits_rec

### ValTrue
Bool constant `true`

### ValUndef
Special constant to indiciate *no default value*

### ValVoid
The void value is the only value inhabiting the `TypeVoid` type

    It can be used to model *null* in nullable pointers via a sum type. 
     
