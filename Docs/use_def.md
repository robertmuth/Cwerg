## Use-Def Chains

Cwerg does not require the input to be in SSA from nor does it use
a full-blown SSA representation internally. Instead it use a modified
use-def chain approach. 

Roughly, each use of a register points to the single instruction defining it.
This defining instruction may not be in the same basic block.
Note, that Cwerg IR instructions write at most one register.

WE actually split local live ranges at each write to the register, so for 
local register (live-range is within a Bbl) we pretty much have SSA form.

If a register is global (live range crosses Bbls), there may not be 
a single instruction defining it. In such a case the `use` will
point to the Bbl which would contain the phi node.

The reason for not adding real phi nodes is that we try to avoid data structures that
need to be dynamically sized as much as possible. (Phi node have potentially
unlimited number of inputs.)
