# Cwerg Casting and Conversion

## No cast required (implicit conversion)

mut ptr T -> ptr T
mut slice T -> slice T

sum A|B|C -> sum A|B|C|D|E
A -> sum A|B|C|D|E

mut array T size -> mut slice T
mut array T size -> slice T
array T size -> slice T

For array constants `array T size -> slice T`
will materialized the array constant in 
readonly memory.


## Regular cast 

u8 -> u16, u32, u64, s16, s32, s64
u16 -> u32, u64, s32, s64
u32 -> u64, s64

s8 -> s16, s32, s64
s16 -> s32, s64
s32 -> s64

r32 -> r64

## Bitcasts

s32 <-> u32 <-> r32
s64 <-> u64 <-> r64

sint <-> uint <-> ptr T

## Unsafe cast 

ptr T -> mut ptr T
slice T -> mut slice T

TBD
