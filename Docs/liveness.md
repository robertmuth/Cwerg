## Liveness Analysis

Liveness analysis of a `fun` is triggered as follows for Python


```
  liveness.FunComputeLivenessInfo(fun)
```

This will make the following datastructures available:
```
 bbl.live_out: Set[Reg]  # set of reg live at the end of the Bbl
```

For C++ thins are only slightly more elaborate:
```  
FunNumberReg(fun);  // create an injectivce mapping int <-> Reg
FunComputeLivenessInfo(fun);  // compute the actual liveness information
```

This will make the following datastructures available:
```
bv = BblLiveOut(Bbl bbl)  // a BitVec that can be queried like so:

bv.GetBit(RegNo(reg));
```

Note, we only save the liveness information at the end of the `bbl`.
To use liveness informtation at the `ins` level, iterate backwards
through the `ins` in the `bbl` and update the livenss info along the way.
