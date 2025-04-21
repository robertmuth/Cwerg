## Instruction Selection

All backends (Arm32, Arm64, x86-64) use the same approach to instruction selection
described below.


### Cwerg IR Recap

Cwerg IR instructions have the form

```
opcode operand1 operand2 ...
```

An operand can be either a
1. a **typed** register or immediate or
2. something else, e.g. a label

The opcode determines which of the two must hold.
For instruction selection we only care about operands of the first kind.


### Patterns and Curbs

Given a concrete Cwerg IR instruction:
```
opcode operand1 operand2 ...
```

We iterate over the catalog of Patterns specified for that opcode in order.
The first pattern that matches will be used to expand the Cwerg IR instruction into 
zero or more target CPU instructions.

The Pattern specifies two constraints called **curbs** for each register/immediate operand
* a type curb, e.g. U32, S64, F32, ...
* an immediate curb, e.g. "must fit in 16bit", "must be zero", "no immediate"
   (must be a register), ...

The expanded CPU Instructions contain placeholders which will be backfilled from the IR Instruction.

### Matching

First we check if the pattern's type curbs are satisfied: For each register or immediate operand
the type must match the type curb.

Next we check if the pattern's immediate curbs are satisfied: For each register operand there must NOT 
be an immediate curb. For each immediate operand there must be an immediate curb AND the value of the 
immediate must satifies the actual kind of curb.

### Examples

Note, all patterns can be listed using `./isel_tab.py`. Here is a commented subset for a32.

We show three patterns for expanding the *blt* opcode  (`blt [BBL REG_OR_CONST REG_OR_CONST]`).
The zeroth operand is label, i.e. neither a register nor an immediate and hence ignored.

```
type:[* U32 U32] imm:[* * *]                  #  Pattern 1: op1 is U32 reg, op2 is U32 reg 
  cmp [ARG.reg1 SHIFT.lsl ARG.reg2 0]         #    1. A32 instruction of the expansion
  b [PRED.cc ARG.bbl0]                        #    2. A32 instriction of the expansion
type:[* U32 U32] imm:[* * pos_8_bits_shifted] #  Pattern 2: op1 is U32 reg, op2 is U32 immediate
  cmp [ARG.reg1 ARG.num2]                     #    1. A32 instruction of the expansion
  b [PRED.cc ARG.bbl0]                        #    2. A32 instruction of the expansion
type:[* S32 S32] imm:[* * *]                  #  Pattern 3: op1 is S32 reg, op2 is S32 reg 
  cmp [ARG.reg1 SHIFT.lsl ARG.reg2 0]         #    1. A32 instruction of the expansion
  b [PRED.lt ARG.bbl0]                        #    2. A32 instruction of the expansion
```

| Cwerg Instruction | Matching Pattern |
|-------------------| -----------------|
|`blt target x:U32 y:U32` | Pattern 1 |
|`blt target x:U32 10:U32` | Pattern 2 (assuming 10 satisfies `pos_8_bits_shifted`) |
|`blt target 10:U32 y:U32` | No Match |
|`blt target x:U32 1000:U32` | No Match (assuming 1000 does not satisfy `pos_8_bits_shifted`) |
|`blt target x:S32 y:S32` | Pattern 3 |
|`blt target x:S32 10:s32` | No Match |

### Additional Uses of Patterns for Legalization

The matching mechanism is used by two compiler passes.
In an earlier pass we use it to rewrite Cwerg IR instruction that have no real match but a
"close" one. Example, suppose
```
add x:U32 y:U32 369:U32
```
has no match but this Pattern matches closely:
```
add type:[U32 U32 U32] imm:[* * *] 
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














