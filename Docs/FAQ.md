## FAQ

### Why does the IR distinguish between signed and unsigned integer operands?

This keeps the number of opcodes small and orthogonal.
Otherwise, we would have to introduce special opcodes like
`shr_u`, `ble_u`, `div_u`, etc which would only be used with unsigned integers.

Also, at some point we may introduce integers with saturating behavior which would
require even more specialized opcodes.

### Why not fuse pushargs and popargs into the call opcodes

An early version of Cwerg did exactly that but it caused a stark imbalance between
the complexity of call and other instructions.
In the C++ implementation this caused a noticeable increase in memory usage.

The pusharg/poparg opcodes also serve as start and end points for live ranges and at least
for now all opcode write at most one register.

### Is there a style guide for the C++ code?

Not currently. Please follow the style of the existing code.
