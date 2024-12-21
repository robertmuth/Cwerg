-- towers of hanoi
module:

import test

global NUM_DISKS = 13_s32

global NO_DISK = -1_s32

global NUM_PILES = 3_u32

rec Disk:
    size s32
    next_in_pile s32

global! all_disks = {[NUM_DISKS]Disk:}

global! piles = {[NUM_PILES]s32: NO_DISK}

fun MoveTopDisk(src_pile u32, dst_pile u32) u32:
    -- pop top disk from src_pile
    let d = piles[src_pile]
    set piles[src_pile] = all_disks[d].next_in_pile
    -- push disk on dst_pile
    set all_disks[d].next_in_pile = piles[dst_pile]
    set piles[dst_pile] = d
    return 1

fun MoveDisks(disks s32, src_pile u32, dst_pile u32) u32:
    if disks == 1:
        return MoveTopDisk(src_pile, dst_pile)
    let other_pile = 3_u32 - src_pile - dst_pile
    let! count = MoveDisks(disks - 1, src_pile, other_pile)
    set count += MoveTopDisk(src_pile, dst_pile)
    set count += MoveDisks(disks - 1, other_pile, dst_pile)
    return count

fun CreateTower(n s32) s32:
    let! last = NO_DISK
    for size = n, 0_s32, -1:
        let d = @!all_disks[n - 1]
        set d^.size = size
        set d^.next_in_pile = last
        set last = n - 1
    return last

fun main(argc s32, argv ^^u8) s32:
    set piles[0] = CreateTower(NUM_DISKS)
    let count = MoveDisks(NUM_DISKS, 0, 1)
    test::AssertEq#(count, 8191_u32)
    test::Success#()
    return 0
