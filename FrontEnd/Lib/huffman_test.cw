(module main [] :
(import test)
(import fmt)

(import huffman)


@doc r"""
                            *
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
                *                       *
               / \                     / \
              /   \                   /   \
             /     \                 /     \
            /       \               /       \
           /         \             /         \
          *           *           *           *
         / \         / \         / \          F       2
        /   \       /   \       /   \
       /     \     /     \     /     \
      *       *   *       *   *       *
     / \     / \  E       G   H       I               3
    *   *   *   *
   / \  A   B   C                                     4
  *   *
 / \  D                                               5
*   *
J   K                                                 6

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

(fun test_tree_decoding [] void :
   (let @mut counts (array 7 u16))
   (let @mut symbols (array 11 u16))

   (test::AssertEq!
    (huffman::ComputeCountsAndSymbolsFromLengths [Tree1Length counts symbols])
    10_u16)

   (test::AssertSliceEq! symbols Tree1ExpectedSymbols)
   (test::AssertSliceEq! counts Tree1ExpectedCounts)

)

(fun @cdecl main [(param argc s32) (param argv (ptr (ptr u8)))] s32 :
    (stmt (test_tree_decoding []))
    @doc "test end"
    (test::Success!)
    (return 0))
)
