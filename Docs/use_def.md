## Use-Def Chains

Cwerg does not require the input to be in SSA from nor does it use
a full-blown SSA representation internally. Instead it use a modified
use-def chain approach. 

Roughly, each use of a register points to the single instruction defining it.
For local register (live-range is within a Bbl) this is pretty much like SSA.
 
We even may rename local registers which gets us even closer to SSA. 
The A32 register allocator for locals requires SSA form, so that each 
local Reg will map to exactly one CpuReg.

If a register is global (live range crosses Bbls), there may not be 
a single instruction defining it. In such a case the `use` will
point to the Bbl which would contain the phi node.
