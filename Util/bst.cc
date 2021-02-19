// (c) Robert Muth - see LICENSE for more info
#include "Util/bst.h"

namespace cwerg {

uint32_t bst_stats_num_finds;
uint32_t bst_stats_num_find_steps;

uint32_t bst_stats_num_adds;
uint32_t bst_stats_num_add_steps;

uint32_t bst_stats_left_rotations;
uint32_t bst_stats_right_rotations;

void DumpBstStates(std::ostream& os) {
  os << "BST\n"
     << "finds:" << bst_stats_num_finds
     << "  steps: " << bst_stats_num_find_steps
     << "  avg-depth: " << bst_stats_num_find_steps / bst_stats_num_finds
     << "\n\n"  //
     << "adds:" << bst_stats_num_adds << "  steps: " << bst_stats_num_add_steps
     << "  avg-depth: " << bst_stats_num_add_steps / bst_stats_num_adds << "\n"
     << "   left rots: " << bst_stats_left_rotations << "\n"
     << "   right rots: " << bst_stats_right_rotations << "\n";
}

}  // namespace cwerg
