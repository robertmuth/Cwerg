(module main [] :
(import test)
(import fmt)

(import huffman)
(import bitstream)

@doc r"""Tree0


B = 0
A = 11
C = 101
D = 100
"""

(global Tree0Length auto (array_val 4 u16 [
    (index_val 2)
    (index_val 1)
    (index_val 3)
    (index_val 3)
]))

(global Tree0ExpectedSymbols auto (array_val 4 u16 [
    (index_val (- 'B' 'A'))
    (index_val (- 'A' 'A'))
    (index_val (- 'C' 'A'))
    (index_val (- 'D' 'A'))
]))

(global Tree0ExpectedCounts auto (array_val 4 u16 [
    (index_val 0)
    (index_val 1)
    (index_val 1)
    (index_val 2)
]))

(fun test_tree0_decoding [] void :
   (let @mut counts (array 4 u16))
   (let @mut symbols (array 4 u16))
   (test::AssertEq!
    (huffman::ComputeCountsAndSymbolsFromLengths [Tree0Length counts symbols])
    3_u16)
   (test::AssertSliceEq! symbols Tree0ExpectedSymbols)
   (test::AssertSliceEq! counts Tree0ExpectedCounts)
)

@doc r"""Tree1


 0                        *
                         / \
                        /   \
                       /     \
                      /       \
                     /         \
                    /           \
                   /             \
                  /               \
                 /                 \
                /                   \
               /                     \
1             *                       *
             / \                     / \
            /   \                   /   \
           /     \                 /     \
          /       \               /       \
         /         \             /         \
        *           *           *           *
2       F          / \         / \         / \
                  /   \       /   \       /   \
                 /     \     /     \     /     \
                *       *   *       *   *       *
3               E       G   H       I  / \     / \
                                      *   *   *   *
4                                     A   B   C  / \
                                                *   *
5                                               D  / \
                                                  *   *
6                                                 J   K

5-F 000
4-E 010
6-G 011
7-H 100
8-I 101
0-A 1100
1-B 1101
2-C 1110
3-D 11110
9-J 111110
10-K 111111
"""
(global Tree1Length auto (array_val 11 u16 [
    (index_val 4)
    (index_val 4)
    (index_val 4)
    (index_val 5)
    (index_val 3)
    (index_val 2)
    (index_val 3)
    (index_val 3)
    (index_val 3)
    (index_val 6)
    (index_val 6)
]))

(global Tree1ExpectedSymbols auto (array_val 11 u16 [
    (index_val (- 'F' 'A'))
    (index_val (- 'E' 'A'))
    (index_val (- 'G' 'A'))
    (index_val (- 'H' 'A'))
    (index_val (- 'I' 'A'))
    (index_val (- 'A' 'A'))
    (index_val (- 'B' 'A'))
    (index_val (- 'C' 'A'))
    (index_val (- 'D' 'A'))
    (index_val (- 'J' 'A'))
    (index_val (- 'K' 'A'))
]))

(global Tree1ExpectedCounts auto (array_val 7 u16 [
    (index_val 0)
    (index_val 0)
    (index_val 1)
    (index_val 4)
    (index_val 3)
    (index_val 1)
    (index_val 2)
]))

(fun test_tree1_decoding [] void :
   (let @mut counts (array 7 u16))
   (let @mut symbols (array 11 u16))

   (test::AssertEq!
    (huffman::ComputeCountsAndSymbolsFromLengths [Tree1Length counts symbols])
    10_u16)

   (test::AssertSliceEq! symbols Tree1ExpectedSymbols)
   (test::AssertSliceEq! counts Tree1ExpectedCounts)
)

(fun test_tree1_bitstream_decoding [] void :
   (let @mut counts (array 7 u16))
   (let @mut symbols (array 11 u16))

   (test::AssertEq!
    (huffman::ComputeCountsAndSymbolsFromLengths [Tree1Length counts symbols])
    10_u16)

   (let data auto (array_val 8 u8 [
    (index_val 0b11111100)
    (index_val 0b01001001)
    (index_val 0b1)
    (index_val 0)
    (index_val 0)
    (index_val 0)
    (index_val 0)
    (index_val 0)]))
  (let @mut @ref bs auto (rec_val bitstream::Stream32 [(field_val data)]))
  (test::AssertEq! 5_u16 (huffman::NextSymbol [(& @mut bs) counts symbols]))
  (test::AssertEq! 10_u16 (huffman::NextSymbol [(& @mut bs) counts symbols]))
  (test::AssertEq! 7_u16 (huffman::NextSymbol [(& @mut bs) counts symbols]))
  (test::AssertEq! 7_u16 (huffman::NextSymbol [(& @mut bs) counts symbols]))
  (test::AssertEq! 8_u16 (huffman::NextSymbol [(& @mut bs) counts symbols]))

)

(fun @cdecl main [(param argc s32) (param argv (ptr (ptr u8)))] s32 :
    (stmt (test_tree0_decoding []))
    (stmt (test_tree1_decoding []))
    (stmt (test_tree1_bitstream_decoding []))

    @doc "test end"
    (test::Success!)
    (return 0))
)
