## Cwerg Language Macros

Macros were not part of the initial vision of Cwerg because of their 
implementation complexity and the loss of readability they often 
create in code using them.

On the other hand macros make it easy to provide feature like:
* syntactic sugar
* lazy evaluation as needed for logging, etc
* printf like functionality

Ultimately a macro system with the following properties was added to Cwerg: 

* macros and their invocation are represented in the ASTs
* only a small number of additional AST node are related to macros (< 10)
  (several other AST nodes like `for` and `while` could be replaced by macros)
* macro definitions can only occur at the module level
* macro invocations can only occur inside function bodies
* the expansion of macros occurs early on before most symbols or types have been resolved.
* it is possible to write hygenic macros by allowing the creation of per macro invocation unique symbols
* macros can invoke other macros, exapansion happens "outside-in".

### Macro Definition

Macro definitions have the form: 

```
(macro <name> 
    [<parameter1> <parameter2> ...] 
    [<body-node1> <body-node2> ...])
```
`Body-nodeX` represent the AST nodes used for expansion.

`ParameterX` have the form: `(macro_parameter <name> <kind>)`

`Name` must start with `$` which is not permitted for identifiers outside of macros.

`Kind` is one of the following:
* `ID`: argument is a `Id` node (only the Id `name` is relevant)
* `STMT_LIST`: argument is a `MacroListArg` node (usually containing statement nodes)
* `EXPR`:  argument is an expression node
* `FIELD`:  argument is a `Id` node (only the Id `name` is relevant and refers to struct field)
* `TYPE`:  argument is a type node

### Macro Invocations


Macro invocations have the form:
```
(macro_invoke <name> [<arg1> < arg2> ...])
```

However, invocation can be abbreviated like so:
```
(<name> <arg1> < arg2> ...)
```

which looks like a regular AST node and hence can be used
to create syntactic sugar.

`argX` is an AST node. A special node `MacroListArg` 
can be used when the argument is a list of nodes.

### Simple example: c-style -> operator

In C `p->next` is equivalent to `(*p).next`.
In Cwerg this can be expressed as a macro:

```
(# "^ is the reference operator in Cwerg")

(macro -> [(macro_param $pointer EXPR) 
           (macro_param $field FIELD)] [
    (. (^ $pointer) $field)
])
```

A corresponding macro invocation:

```
(-> list_pointer next)
```

which is short for

```
(macro_invoke -> [list_pointer next])
```

will be expanded towiamis77
: 
```
 (. (^ list_pointer) next)
```


### Another example: while loop

Given the macro:

```
(macro while [(macro_param $cond EXPR) 
              (macro_param $body STMT_LIST)] [
    (block _ [
          (if $cond [] [(break)])
          $body
          (continue)
    ])
])   
```

This code:
```
(while (!= i 1) [
   (stmt call print [i])
   (if (== (% i 2) 0) [(= i (/ i 2))] [(= i (+ (* i 3) 1))])
])
```

which is short for
```
(macro_invoke while [(!= i 1) (MacroListArg [
    (stmt call print [i])
    (if (== (% i 2) 0)  [(= i (/ i 2))]  [(= i (+ (* i 3) 1))])
]]))
```


Expands to:
```
(block _ [
    (if (!= i 1) [] [(break)])
    (stmt call print [i])
    (if (== (% i 2) 0)  [(= i (/ i 2))]  [(= i (+ (* i 3) 1))])
    (continue)
])

```

### Hygienic example: for loop over range

```
(# "loop over range equivalent to Python's range($start, $end, $step)")
(macro for [(macro_param $index ID) 
            (macro_param $type TYPE) 
            (macro_param $start EXPR) 
            (macro_param $end EXPR) 
            (macro_param $step EXPR) 
            (macro_param $body STMT_LIST)] [
    (macro_let $end_eval $type $end)
    (macro_let $step_eval $type $step)
    (macro_let mut $it $type $start)
    (block _ [
          (if (>= $it $end_eval) [(break)] [])
          (macro_let_indirect $index auto $it)
          (+=  $it $step_eval)
          $body
          (continue)
    ])
])
```

Sample invocation:
```
(for i uint32 0 (* 10 10) 1 [
  (stmt call print [i])
])
```


`(macro_let $var ...)` defines a new variable `$var`. 
The name must start with a "$" and will be replaced with a
unique name at macro expansion time to avoid nameclashes.

`(macro_let_indirect $var ...)` defines a new variable whose name
is detemined by the macro argument `$var`. 

So the sample invocation exapands to:
```
(let end_eval_312 uint32 (* 10 10))
(let step_eval_312 uint32 1)
(let mut it_312 uint32 0)
(block _ [
      (if (>= it_312 end_eval_312) [(break)] [])
      (let_indirect i auto it_312)
      (+=  it_312 step_eval_312)
      (stmt call print [i])
      (continue)
])
```



