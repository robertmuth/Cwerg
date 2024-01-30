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
    2
    1
    3
    3
]))

(global Tree0ExpectedSymbols auto (array_val 4 u16 [
    (- 'B' 'A')
    (- 'A' 'A')
    (- 'C' 'A')
    (- 'D' 'A')
]))

(global Tree0ExpectedCounts auto (array_val 4 u16 [
    0
    1
    1
    2
]))

(fun test_tree0_decoding [] void :
   (let @mut counts (array 4 u16))
   (let @mut symbols (array 4 u16))
   (test::AssertEq#
    (huffman::ComputeCountsAndSymbolsFromLengths [Tree0Length counts symbols])
    4_u16)
   (test::AssertSliceEq# symbols Tree0ExpectedSymbols)
   (test::AssertSliceEq# counts Tree0ExpectedCounts)
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
    4
    4
    4
    5
    3
    2
    3
    3
    3
    6
    6
]))

(global Tree1ExpectedSymbols auto (array_val 11 u16 [
    (- 'F' 'A')
    (- 'E' 'A')
    (- 'G' 'A')
    (- 'H' 'A')
    (- 'I' 'A')
    (- 'A' 'A')
    (- 'B' 'A')
    (- 'C' 'A')
    (- 'D' 'A')
    (- 'J' 'A')
    (- 'K' 'A')
]))

(global Tree1ExpectedCounts auto (array_val 7 u16 [
    0
    0
    1
    4
    3
    1
    2
]))

(fun test_tree1_decoding [] void :
   (let @mut counts (array 7 u16))
   (let @mut symbols (array 11 u16))

   (test::AssertEq#
    (huffman::ComputeCountsAndSymbolsFromLengths [Tree1Length counts symbols])
    11_u16)

   (test::AssertSliceEq# symbols Tree1ExpectedSymbols)
   (test::AssertSliceEq# counts Tree1ExpectedCounts)
)

(fun test_tree1_bitstream_decoding [] void :
   (let @mut counts (array 7 u16))
   (let @mut symbols (array 11 u16))

   (test::AssertEq#
    (huffman::ComputeCountsAndSymbolsFromLengths [Tree1Length counts symbols])
    11_u16)

   (let data auto (array_val 8 u8 [
    0b11111100
    0b01001001
    0b1
    0
    0
    0
    0
    0
  ]))
  (let @mut @ref bs auto (rec_val bitstream::Stream32 [(field_val data)]))
  (test::AssertEq# 5_u16 (huffman::NextSymbol [(& @mut bs) counts symbols]))
  (test::AssertEq# 10_u16 (huffman::NextSymbol [(& @mut bs) counts symbols]))
  (test::AssertEq# 7_u16 (huffman::NextSymbol [(& @mut bs) counts symbols]))
  (test::AssertEq# 7_u16 (huffman::NextSymbol [(& @mut bs) counts symbols]))
  (test::AssertEq# 8_u16 (huffman::NextSymbol [(& @mut bs) counts symbols]))

)

(fun test_helper [] void :
   (let @mut lengths (array 285 u16))
   (= (at lengths 0) 1)
   (= (at lengths 256) 2)
   (= (at lengths 284) 2)

   (let @mut counts (array 8 u16))
   (let @mut symbols (array 8 u16))
   (test::AssertEq#
        (huffman::ComputeCountsAndSymbolsFromLengths [lengths counts symbols])
    3_u16)
    (test::AssertEq# 0_u16 (at counts 0))
    (test::AssertEq# 1_u16 (at counts 1))
    (test::AssertEq# 2_u16 (at counts 2))

    (test::AssertEq# 0_u16 (at symbols 0))
    (test::AssertEq# 256_u16 (at symbols 1))
    (test::AssertEq# 284_u16 (at symbols 2))
)

(fun test_helper_single_code [] void :
   (let @mut lengths (array 285 u16))
   (= (at lengths 66) 1)

   (let @mut counts (array 8 u16))
   (let @mut symbols (array 8 u16))
   (test::AssertEq#
        (huffman::ComputeCountsAndSymbolsFromLengths [lengths counts symbols])
    2_u16)
    (test::AssertEq# 0_u16 (at counts 0))
    (test::AssertEq# 2_u16 (at counts 1))

    (test::AssertEq# 66_u16 (at symbols 0))
    (test::AssertEq# huffman::BAD_SYMBOL (at symbols 1))

)

(fun @cdecl main [(param argc s32) (param argv (ptr (ptr u8)))] s32 :
    (shed (test_helper []))
    (shed (test_helper_single_code []))

    (shed (test_tree0_decoding []))
    (shed (test_tree1_decoding []))
    (shed (test_tree1_bitstream_decoding []))

    @doc "test end"
    (test::Success#)
    (return 0))
)
