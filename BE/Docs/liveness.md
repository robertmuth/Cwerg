## Liveness Analysis

Liveness analysis of a `fun` is triggered as follows for Python


```
  liveness.FunComputeLivenessInfo(fun)
```

This will make the following datastructure available:
```
 bbl.live_out: Set[Reg]  # set of reg live at the end of the Bbl
```

For C++ things are only slightly more elaborate:
```
FunNumberReg(fun);  // create an injective mapping int <-> Reg
FunComputeLivenessInfo(fun);  // compute the actual liveness information
```

This will make the following datastructures available:
```
bv = BblLiveOut(Bbl bbl)  // a BitVec that can be queried like so:

bv.GetBit(RegNo(reg));
```

Usage

We only save the liveness information at the end of the `bbl`.
To use liveness information at the `ins` level, iterate backwards
through the `ins` in the `bbl` and update the liveness info along the way.


Liveness is primarily used to compute live ranges.
