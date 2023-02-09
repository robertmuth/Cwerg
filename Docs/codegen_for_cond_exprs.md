## Problem: generate code for an if-statement with short circuit operators

The if-statement looks like this

```
if <cond>:
    <body-true>
else:
    <body-false>
```

where `<cond>` is an expression evaluating to a bool which may contain the short circuit operators `&&` and `||`.

## Assumptions

Our AST has expression nodes of the form:

* `ExprUnaryNot` (logical not) with fields
  * expr
* `ExprBinary` (misc binary operation) with fields
  * expr1
  * expr2
  * kind (one of <, >, <=, >=, +, -, *, ...)
* `Expr&&` (short circuit `and`) with fields
  * expr1
  * expr2
* `Expr||` (short circuit `or`) with fields
  * expr1
  * expr2


The target language (assembler or IR) includes the following instructions

* `bra <target>` (unconditional branch)
* `bxx <op1> <op2> <target>` (conditional branch, the condion modifier `xx` is one of eq, ne, ge, gt, le, lt ...)


A function `AstCmpToAsmCmp` translates `ExprBinary.kind` to the condition modifier,
e.g. `!=` -> `ne`, `<` -> `lt`, etc.

## First solution

This is a straught forward solution that is easy to implement and reason about

The if-statement will be emitted as

```
    <code-for-the-cond-expr>
label-true:
    <code-for-body-true>
    bra label-join 
label-false:
    <code-for-body-false>
label-join:
```

where `code-for-the-cond-expr`  is the result of calling 
`EmitConditional(cond, "label-true","label-false")` whose implementation is shown below:


```
def EmitConditional(cond, label_true, label_false):
    if cond is-a ExprUnaryNot:
        EmitConditional(cond.expr, label_false, label_true)
    elif cond is-a ExprBinary:
        op1 = EmitExpr(cond.expr1)   # op1 contains the register/var with value of cond.expr1
        op2 = EmitExpr(cond.expr2)   # similar as above
        Emit("   b{AstCmpToAsmCmp(cond.kind)} {op1} {op2} {label_true}")
        Emit("   bra {label_false}")
    elif cond is-a Expr&&:
        label_and = NewLabel()
        EmitConditional(cond.expr1, label_and, label_false)
        Emit(f"{label_and}:")
        EmitConditional(cond.expr2, label_true, label_false)
    elif kind is cwast.BINARY_EXPR_KIND.ORSC:
        label_or = NewLabel()
        EmitConditional(cond.expr1, label_true, label_or)
        Emit(f"{label_or}:")
        EmitConditional(cond.expr2, label_true, label_false)
    else:
        assert False, f"unexpected node {cond}"
```

For the common case where the `else` branch is empty we will emit:


``` 
    <code-for-the-cond-expr>
label-true:
    <code-for-body-true>
label-join:
```

where `code-for-the-cond-expr`  is the result of calling  `EmitConditional(cond, "label-true", "label-join")`


## Second solution

The first solution creates lots of labels and unconditionl branches which makes it
difficult to spot problems/bugs in the emitted code.

To avoid this we mddify `EmitConditional` and only pass one label, `label_false`  as a parameter. 
The `label_true` is assumed  to be following immediately after the code generated for the conditional.
We also add a parameter `inverse` that inverts the  condition as if a `ExprUnaryNot` had been added.

For this solution the if-statement will be emitted as

```
    <code-for-the-cond-expr>
    <code-for-body-true>
    bra label-join 
label-false:
    <code-for-body-false>
label-join:
```

where `code-for-the-cond-expr` is the result of calling `EmitConditional(cond, True, label_false)`
whose implementation is shown below:

```
def EmitIRConditional(cond, invert, label_false):
    if cond is-a ExprUnaryNot:
        EmitConditional(cond.expr, not invert, label_false)
    elif cond is-a ExprBinary:
            op1 = EmitIRExpr(cond.expr1, tc, id_gen)
            op2 = EmitIRExpr(cond.expr2, tc, id_gen)
            Emit("   b{AstCmpToAsmCmp(cond.kind, invert)} {op1} {op2} {label_true}")
    elif cond is-a Expr&&:
        if invert:
            EmitIRConditional(cond.expr1, True, label_false)
            EmitIRConditional(cond.expr2, True, label_false)
        else:
            label_and = NewLabel()
            EmitConditional(cond.expr1, True, label_and)
            EmitConditional(cond.expr2, False, label_false)
            Emit(f"{label_and}:")
    elif cond is-a Expr||:
        if invert:
            label_or = NewLabel()
            EmitConditional(cond.expr1, False, or)
            EmitConditional(cond.expr2, True, label_false)
            Emit(f".{label_or}:")
        else:
            EmitConditional(cond.expr1, False, label_false)
            EmitConditional(cond.expr2, False, label_false)
    else:
        assert False, f"unexpected node {cond}"
```