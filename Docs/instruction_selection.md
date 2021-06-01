## Instruction Selection

Both the Arm32 and Arm64 backend use the same approach to instruction selection
described below.


### Patterns

Given a concrete Cwerg IR instruction:
```
opcode operand1 operand2 ...
```

We iterate over the catalog of Patterns specified for that opcode in order.
The first pattern that matches will be used to expand the Cwerg IR instruction into 
zero or more target CPU instructions.

The Pattern specifies two constraints for each register/immediate operand
* a type constraint, e.g. U32, S64, F32, ...
* an immediate constraint (aka "curb"), e.g. "must fit in 16bit", "must be zero", "no immediate"
   (must be a register), ...

If the operand cannot be a register/immediate the constraint is ignored.
Note, that:
* the IR opcode dictates which operands are registers/immediates
* both registers and immediates are typed


#### Matching

First we match operand types of the Cwerg IR instruction against the type constraints.
If the types match we proceed to check the constraints for immediates.

The matching mechanism is used by two compiler passes.
In an earlier pass we use it to rewrite Cwerg IR instruction that have no real match but a
"close" one. Example, suppose
```
ADD x:U32 y:U32 369:U32
```
has no match but this Pattern matches closely:
```
ADD type-constr:[U32 U32 U32] imm_constr=[no-immediate no-immediate  no-immediate] 
```
This triggers a rewrite of the original instruction to:
```
MOV tmp:U32 369:U32
ADD x:U32 y:U32 tmp:U32
```
Now the second instruction can be matched. But we need to make sure we have matching Patterns
for all possible MOV instructions.

The later pass will actually emit CPU instructions and failure find a match is bug.

#### Instruction Templates

TBD














