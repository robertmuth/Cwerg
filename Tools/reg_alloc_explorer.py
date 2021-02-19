#!/usr/bin/python3
"""
Webserver for debugging/exploring register allocation

Usage:
./Tools/reg_alloc_explorer.py TestData/live_ranges.txt
"""

# import difflib

import json
import heapq
from typing import List, Dict, Set
import argparse
import http.server

from Base import ir
from Base import reg_alloc
from Base.liveness import LiveRange, LiveRangeFlag, BEFORE_BBL, AFTER_BBL
from Base import opcode_tab as o

# language=css
STYLE = """
table {
  border-collapse: collapse;
}

table, th, td {
  border: 1px solid black;
}

body {		/* TH & TD because NS tables don't inherit font */
    font-family: Helvetica, sans-serif;
}

.column {
  float: left;
  width: 50%;
}

/* Clear floats after the columns */
.row:after {
  content: "";
  display: table;
  clear: both;
}
"""

# language=javascript
JS = r"""
let VIEWERS = [];

function HttpGetJSON(url, handler) {
    console.log(`requesting ${url}`);
    const req = new XMLHttpRequest();
    req.onreadystatechange = function() {
        if (req.readyState == 4 && req.status == 200) {
            handler(JSON.parse(req.responseText));
        }
    }

    req.open( "GET", url);
    req.send( null );
}

class DataStore {
    constructor() {
        this.pool = [];
        this.traces = [];
        this.live_ranges = [];
        this.elem_live_ranges = document.getElementById("live_ranges");
        this.elem_pool = document.getElementById("pool");
        this.elem_traces = document.getElementById("traces");
    }


    redraw_traces() {
        console.log("redraw_traces");
        var rows = [];
        var n = 0
        for (const line of this.traces) {
            rows.push(`<tr><td>${n}</td><td>${line}</td></tr>`);
            ++n;
        }
        this.elem_traces.innerHTML = rows.join("\n");
    }
    
     redraw_live_ranges() {
        console.log("redraw_live_ranges");
        var rows = [];
        for (const lr of this.live_ranges) {
            rows.push(`<tr><td>${lr[0]}</td><td>${lr[1]}</td><td>${lr[2]}</td></tr>`)
        }
        this.elem_live_ranges.innerHTML = rows.join("\n");
    }
    
    redraw_pool() {
        console.log("redraw_pool");
        var rows = [];
        for (const regs of this.pool) {
            rows.push(`<tr><td>${regs[0]}</td><td>${regs[1]}</td></tr>`)
        }
        this.elem_pool.innerHTML = rows.join("\n");
    }
        
    process(js) {
        console.log("processing");
        console.log(js);
        this.pool = js[0];    
        this.traces = js[1];    
        this.live_ranges = js[2];
        this.redraw_traces()
        this.redraw_live_ranges()
        this.redraw_pool()

    }
    
    refresh() {
        HttpGetJSON("/GetData", this.process.bind(this));
    }
}

function main() {
    console.log("main");
    const ds = new DataStore();
    ds.refresh();
}

window.onload = main;
"""

COLUMN_HTML = """
<div class=history>
MOD: <select class=sel_mod></select>
OBJ: <select class=sel_obj></select>
<span class=the_mod></span>
</div>

<p></p>

<div class=view_area>
Hello
</div>
"""

# language=html
ERROR_HTML = """<!DOCTYPE html>
<html>
<body>
No handler for request: 
<pre>
%s
</pre>
</body>
</html>
"""

# language=html
APP_HTML = f"""<!DOCTYPE html>
<html>
<head>
<style>
{STYLE}
</style>
</head>
<body>

<div class="row">
  <div class="column">
    <div id="step"></div>
    <h3>Live Ranges</h3>
    <table id="live_ranges"></table>
  </div>

  <div class="column">
    <h3>Pool</h3>
    <table id="pool"></table>

    <h3>Traces</h3>
    <table id="traces"></table>
  </div>
</div>

<script>
{JS}
</script>
</body>
</html>
"""

LAC = 16
GPR_NOT_LAC = 1
GPR_LAC = LAC + GPR_NOT_LAC
FLT_NOT_LAC = 2
FLT_LAC = LAC + FLT_NOT_LAC

A32_REGS = ([ir.CpuReg(f"r{i}", i, GPR_NOT_LAC) for i in range(6)] +
            [ir.CpuReg(f"r12", 12, GPR_NOT_LAC), ir.CpuReg(f"r14", 14, GPR_NOT_LAC)] +
            [ir.CpuReg(f"r{i}", i, GPR_LAC) for i in range(6, 12)] +
            [ir.CpuReg(f"s{i}", i, FLT_NOT_LAC) for i in range(16)] +
            [ir.CpuReg(f"s{i}", i, FLT_LAC) for i in range(16, 32)])


class TestRegPool(reg_alloc.RegPool):
    def __init__(self, regs: List[ir.CpuReg]):
        self.available: Dict[int, List[ir.CpuReg]] = {
            GPR_NOT_LAC: [],
            GPR_LAC: [],
            FLT_NOT_LAC: [],
            FLT_LAC: [],
        }
        self.set_available: Set[ir.CpuReg] = set()
        self.reserved: Dict[ir.CpuReg, reg_alloc.PreAllocation] = {}
        for cpu_reg in regs:
            self.reserved[cpu_reg] = reg_alloc.PreAllocation()
            heapq.heappush(self.available[cpu_reg.kind], cpu_reg)
            self.set_available.add(cpu_reg)

    def get_cpu_reg_family(self, kind: o.DK) -> int:
        return FLT_NOT_LAC if kind.flavor() is o.DK_FLAVOR_F else GPR_NOT_LAC

    def backtrack_reset(self, cpu_reg: ir.CpuReg):
        assert cpu_reg != ir.CPU_REG_SPILL
        if cpu_reg not in self.set_available:
            heapq.heappush(self.available[cpu_reg.kind], cpu_reg)

    def give_back_available_reg(self, cpu_reg: ir.CpuReg):
        return self.backtrack_reset(cpu_reg)

    def get_available_reg(self, lr: LiveRange) -> ir.CpuReg:
        kind = self.get_cpu_reg_family(lr.reg.kind)
        if LiveRangeFlag.LAC in lr.flags:
            kind += LAC
        available = self.available[kind]
        unsuitable = []
        while available:
            candidate = heapq.heappop(available)
            if self.reserved[candidate].has_conflict(lr):
                unsuitable.append(candidate)
            else:
                for cpu_reg in unsuitable:
                    heapq.heappush(available, cpu_reg)
                self.set_available.discard(candidate)
                return candidate
        for cpu_reg in unsuitable:
            heapq.heappush(available, cpu_reg)
        return ir.CPU_REG_SPILL

    def add_reserved_range(self, lr: LiveRange):
        self.reserved[lr.reg.cpu_reg].add(lr)


def FindDefRange(reg_name: str, def_pos: int, ranges: List[LiveRange]):
    for lr in ranges:
        if lr.reg.name == reg_name and lr.def_pos == def_pos:
            return lr
    assert False


def ParseLiveRanges(fin, cpu_reg_map: Dict[str, ir.CpuReg]) -> List[LiveRange]:
    out: List[LiveRange] = []
    for line in fin:
        token = line.split()
        if not token or token[0] == "#":
            continue
        assert token.pop(0) == "RANGE"
        start_str = token.pop(0)
        start = BEFORE_BBL if start_str == "BEFORE_BBL" else int(start_str)
        assert token.pop(0) == "-"
        end_str = token.pop(0)
        end = AFTER_BBL if end_str == "AFTER_BBL" else int(end_str)
        flags = 0
        lr = LiveRange(start, end, ir.REG_INVALID, 0)
        out.append(lr)
        while token:
            t = token.pop(0)
            if t == "PRE_ALLOC":
                lr.flags |= LiveRangeFlag.PRE_ALLOC
            elif t == "LAC":
                lr.flags |= LiveRangeFlag.LAC
            elif t == "def:":
                reg_str = token.pop(0)
                cpu_reg_str = ""
                reg_name, kind_str = reg_str.split(":")
                if "@" in kind_str:
                    kind_str, cpu_reg_str = kind_str.split("@")
                lr.reg = ir.Reg(reg_name, o.DK[kind_str])
                if cpu_reg_str:
                    lr.reg.cpu_reg = cpu_reg_map[cpu_reg_str]
                    lr.cpu_reg = lr.reg.cpu_reg
                break
            elif t == "uses:":
                uses = [u.split(":") for u in token.pop(0).split(",")]
                for reg_name, def_pos_str in uses:
                    lr.uses.append(FindDefRange(reg_name, int(def_pos_str), out))
            else:
                assert False
    return out


POOL = None
TRACES = []
LIVE_RANGES = []


def logger(lr, message):
    m = f"{lr} {message}"
    TRACES.append(m)
    # print(m)
    assert len(TRACES) < 300, f"target LiveRange reached"


def GetData():
    global TRACES, POOL, LIVE_RANGES
    TRACES = []
    POOL = TestRegPool(A32_REGS)
    for lr in LIVE_RANGES:
        if LiveRangeFlag.PRE_ALLOC not in lr.flags:
            lr.cpu_reg = ir.CPU_REG_INVALID
        else:
            POOL.add_reserved_range(lr)
    try:
        reg_alloc.RegisterAssignerLinearScanFancy(LIVE_RANGES, POOL, debug=logger)
    except Exception as e:
        TRACES.append(f"EXCEPTION {e}")
    live_ranges = []
    for lr in LIVE_RANGES:
        flags = [f.name for f in LiveRangeFlag if f in lr.flags]
        if lr.uses:
            interval = f"{lr.def_pos}"
            payload = " ".join([f"({x.reg.name} {x.def_pos})" for x in lr.uses])
        else:
            interval = f"{lr.def_pos} - {lr.last_use_pos}"
            payload = f"{lr.reg.name}:{lr.reg.kind.name}"
            if lr.cpu_reg is not ir.CPU_REG_INVALID:
                payload += f" <b>{lr.cpu_reg.name}</b>"
        live_ranges.append((interval, "|".join(flags), payload))
    available = []
    for name, key in [("GPR", GPR_NOT_LAC), ("GPR_LAC", GPR_LAC),
                      ("FLT", FLT_NOT_LAC), ("FLT_LAC", FLT_LAC)]:
        regs = sorted(POOL.available[key])
        available.append((name, " ".join(r.name for r in regs)))
    return bytes(json.dumps([available, TRACES, live_ranges]), 'utf-8')


def Index():
    return bytes(APP_HTML, 'utf-8')


GET_ROUTES = [
    (r'/GetData', GetData, 'application/json'),
    (r'/', Index, 'text/html'),
]


class MyRequestHandler(http.server.BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        return http.server.BaseHTTPRequestHandler.__init__(self, *args, **kwargs)

    def _handle_methods(self, routes):
        for prefix, handler, mime_type in routes:
            if self.path.startswith(prefix):
                self.send_response(200)
                self.send_header('Content-type', mime_type)
                self.end_headers()
                self.wfile.write(handler())
                break
        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(bytes(ERROR_HTML % self.path, 'utf-8'))

    def do_GET(self):
        # print("GET handler")
        self._handle_methods(GET_ROUTES)


def main():
    global LIVE_RANGES
    parser = argparse.ArgumentParser(description='reg_alloc_explorer')
    parser.add_argument('-debug', help='enable webserver debugging',
                        action='store_true')
    parser.add_argument('-port', type=int, help='web server port', default=5000)
    parser.add_argument('input', type=str, help='input file')
    args = parser.parse_args()

    reg_map = {reg.name: reg for reg in A32_REGS}
    LIVE_RANGES = ParseLiveRanges(open(args.input), reg_map)
    # print(f"read {len(LIVE_RANGES)} LiveRanges")

    http_server = http.server.HTTPServer(('', args.port), MyRequestHandler)
    print(f'Starting HTTP server at http://localhost:{args.port}')
    try:
        http_server.serve_forever()
    except KeyboardInterrupt:
        pass
    print('Stopping HTTP server')
    http_server.server_close()


if __name__ == '__main__':
    main()
