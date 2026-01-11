#!/bin/env python3
"""
Webserver for debugging/exploring register allocation

An annotated liverange dump can be obtained like so:

  for lr in live_ranges:
        ins = ""
        if lr.def_pos >= 0 and not lr.is_use_lr():
            ins = "\t# " + serialize.InsRenderToAsm(bbl.inss[lr.def_pos])
        print (str(lr) + ins)



Usage:
./reg_alloc_explorer.py TestData/live_ranges.a64.txt  # you need to change the import to CodeGenA64

./reg_alloc_explorer.py TestData/live_ranges.txt   # you need to change the import to CodeGenA32
"""

# import difflib

import json
import heapq
from typing import List, Dict, Optional
import argparse
import http.server

from BE.Base import ir
from BE.Base import reg_alloc
from BE.Base import liveness
from IR import opcode_tab as o

# NOTE NOTE NOTE: you must change this to reflect the  backend where he liveranges originate
if False:
    from BE.CodeGenA32 import regs
else:
    from BE.CodeGenA64 import regs

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
        for (const [line, kind, avail] of this.traces) {
            rows.push(`<tr><td>${n}</td><td>${line}</td><td>${kind}</td><td>${avail}</td></tr>`);
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
        this.traces = js[0];
        this.live_ranges = js[1];
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


POOL: Optional[regs.CpuRegPool] = None
TRACES = []
LIVE_RANGES = []


def logger(lr: LiveRange, message: str):
    available = ""
    if not lr.is_use_lr():
        lac = liveness.LiveRangeFlag.LAC in lr.flags
        is_gpr = lr.reg.kind.flavor() != o.DK_FLAVOR_R
        available = POOL.render_available(lac, is_gpr)
    TRACES.append((str(lr), message, available))
    # print(m)
    assert len(TRACES) < 300, f"target LiveRange reached"


def GetData():
    global TRACES, POOL, LIVE_RANGES
    TRACES = []
    POOL = regs.CpuRegPool(None, None, True,
                           regs.GPR_REGS_MASK & regs.GPR_LAC_REGS_MASK,  #
                           regs.GPR_REGS_MASK & ~regs.GPR_LAC_REGS_MASK, #
                           regs.FLT_REGS_MASK & regs.FLT_LAC_REGS_MASK,  #
                           regs.FLT_REGS_MASK & ~regs.FLT_LAC_REGS_MASK)
    for lr in LIVE_RANGES:
        if liveness.LiveRangeFlag.PRE_ALLOC in lr.flags:
            POOL.add_reserved_range(lr)
        else:
            lr.cpu_reg = ir.CPU_REG_INVALID

    reg_alloc.RegisterAssignerLinearScanFancy(LIVE_RANGES, POOL, debug=logger)

    live_ranges = []
    for lr in LIVE_RANGES:
        flags = [f.name for f in liveness.LiveRangeFlag if f in lr.flags]
        if lr.uses:
            flags.append("USES")
            interval = f"{lr.def_pos}"
            payload = " ".join([f"({x.reg.name} {x.def_pos})" for x in lr.uses])
        else:
            interval = f"{lr.def_pos} - {lr.last_use_pos}"
            payload = f"{lr.reg.name}:{lr.reg.kind.name}"
            if lr.cpu_reg is not ir.CPU_REG_INVALID:
                payload += f" <b>{lr.cpu_reg.name}</b>"
        live_ranges.append((interval, "|".join(flags), payload))
    return bytes(json.dumps([TRACES, live_ranges]), 'utf-8')


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

    LIVE_RANGES = liveness.ParseLiveRanges(open(args.input), regs.CPU_REGS_MAP)
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
