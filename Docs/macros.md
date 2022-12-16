## Cwerg Language Macros

Macros were not part of the initial vision of Cwerg because of their 
implementation complexity and the loss of readability they often 
create in code using them.

On the other hand macros make it easy to provide feature like:
* syntactic sugar
* lazy evaluation as needed for logging, etc
* printf like functionality

As a compromise a fairly restricted macro system with the following properties was added:

* only a small number (< 10) of additional AST nodes where introduced to support macros.
* several other AST nodes like `for` and `while` could be replaced by macros and were removed.
* macros and their invocation are represented in the ASTs so the existing parser could be used
  almost unchanged
* macros expansion occurs before types resolution and partial evaluation so these and later phases
  of the compiler do not need to change
* since partial evaluation follow macro expansion #if style conditional compilation is NOT available
* macro definitions can only occur at the module level
* macro invocations can only occur inside function bodies
* hygenic macros are supported by allowing the creation of per macro invocation unique symbols
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
can be used when the argument is logically a list of nodes.

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

will be expanded to:
: 
```
 (. (^ list_pointer) next)
```


### Another example: while loop

Given the macro:

```
(macro while [(macro_param $cond EXPR) 
              (macro_param $body STMT_LIST)] [
    (block [
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
(block [
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
    (macro_gen_id $end_eval)      
    (macro_let $end_eval $type $end)
    (macro_gen_id $step_eval)      
    (macro_let $step_eval $type $step)
    (macro_gen_id $it)      
    (macro_let mut $it $type $start)
    (block [
          (if (>= $it $end_eval) [(break)] [])
          (macro_let $index auto $it)
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


`(macro_gen_id $var ...)` defines a new identifier `$var`. 
The identifier must start with a "$" and will be bound to a new unique name
picked for this macro expansion. 
This will guarantee the absence of name clashes and/or involuntary capture.

`(macro_let $var ...)` defines a new variable whose name
is detemined by the macro argument or macro_gen_id `$var`. 

So the sample invocation exapands to:
```
(let end_eval_$312 uint32 (* 10 10))
(let step_eval_$312 uint32 1)
(let mut it_$312 uint32 0)
(block [
      (if (>= it_$312 end_eval_$312) [(break)] [])
      (let_indirect i auto it_$312)
      (+=  it_$312 step_eval_$312)
      (stmt call print [i])
      (continue)
])
```



