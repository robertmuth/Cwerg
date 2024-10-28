import logging
import collections

from typing import Set, Dict, List

from FE import cwast


logger = logging.getLogger(__name__)

_Hell = cwast.DefFun("hell", [], cwast.TypeBase(cwast.BASE_TYPE_KIND.VOID), [])


def ShakeTree(mods: List[cwast.DefMod], entry_fun: cwast.DefFun):
    # callgraph - map fun to its callers
    cg: Dict[cwast.DefFun, Set[cwast.DefFun]] = collections.defaultdict(set)
    cg[_Hell].add(_Hell)  # force hell to be alive

    def visitor(call, parents):
        nonlocal cg
        if isinstance(call, cwast.ExprCall):
            if isinstance(call.callee, cwast.Id):
                callee = call.callee.x_symbol
                assert isinstance(
                    callee, cwast.DefFun), f"expected fun: {call} {callee}"
                caller = parents[0]
                if caller is not callee:
                    logging.info(f"@@@@ {caller.name} -> {callee.name}")
                    cg[callee].add(caller)

    # create call graph
    for m in mods:
        for fun in m.body_mod:
            if not isinstance(fun, cwast.DefFun):
                continue
            if fun.init or fun.fini or fun.ref or fun == entry_fun:
                cg[fun].add(_Hell)
            else:
                # make sure the function is recorded
                _ = cg[fun]
            cwast.VisitAstRecursivelyWithAllParents(fun, [], visitor)

    # compute dead functions
    change = True
    while change:
        dead_funs: List[cwast.DefFun] = []
        for fun, callers in cg.items():
            has_live_caller = False
            for c in callers:
                if c in cg:
                    has_live_caller = True
                    break
            if not has_live_caller:
                logging.info(f"@@@ DEAD: {fun.name}")
                dead_funs.append(fun)
        for d in dead_funs:
            del cg[d]
        change = len(dead_funs) > 0
    for fun in cg:
        logging.info(f"@@@ ALIVE: {fun.name}")
    for m in mods:
        new_body = [f for f in m.body_mod if not isinstance(f, cwast.DefFun) or f in cg]
        m.body_mod = new_body
