#!/usr/bin/python3
"""
Webserver for debugging optimization and code generation.

Usage:
./Tools/inspector.py TestData/nano_jpeg.a32.asm
"""

# MODE = "opt"     # only run optimizer
# MODE = "a32"   # run everything and generate a32 code
MODE = "a64"  # run everything and generate a64 code

from typing import List, Dict, Tuple, Any
import argparse
import collections
import copy
import difflib
import http.server
import json

from Base import ir
from Base import optimize
from Base import serialize

if MODE == "a32":
    import CpuA32.opcode_tab as arm
    from CodeGenA32 import codegen
if MODE == "a64":
    print("Selected mode A64")
    import CpuA64.opcode_tab as arm
    from CodeGenA64 import codegen

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

.bbl {
    font-weight: bold;
}

.mem {
    font-weight: bold;
}

.fun {
    font-weight: bold;
    font-size: 110%;
}

.the_mod {
    font-weight: bold;
}

.insert {
    background-color: #7df;
}

.replace {
    background-color: #9e9;
}

.delete {
    background-color: #e88;
}

.column {
    width: 19%;
    vertical-align: top;
}
"""

# language=JavaScript
JS = """
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
        this.mod_names = [];
        this.mods = {}
        this.sel_obj = document.getElementsByClassName(
                            "global_sel_obj")[0];
        this.sel_obj.onchange = this.UpdateObj.bind(this);
    }

    process(js) {
        let all_mems= {};
        let all_funs = {};

        const first_time = this.mod_names.length == 0;
        for (const mod of js) {
            console.log(`Received Mod: ${mod.name}`);
            this.mod_names.push(mod.name);
            this.mods[mod.name] = mod;
            for (const v of mod.mems) {
                all_mems[v[0]] = 1;
            }
            for (const v of mod.funs) {
                all_funs[v[0]] = 1;
            }
        }
        let options = `<option value='ALL'>ALL</option>`
        for (const v in all_mems) {
            options += `<option value="${v}">${v}</option>`;
        }
        for (const v in all_funs) {
            options += `<option value="${v}">${v}</option>`;
        }
        this.sel_obj.innerHTML = options;
        
        for (const mv of VIEWERS) {
            mv.UpdateModList();
        }
    }

    UpdateObj() {
         console.log(`GLOBAL VALUE: ${this.sel_obj.value}`);
         for (const mv of VIEWERS) {
            mv.sel_obj.value = this.sel_obj.value;
            console.log(`LOCAL VALUE: ${mv.sel_obj.value}`);
            mv.UpdateViewArea();
        }
    }
    
    refresh() {
        HttpGetJSON("/GetModules", this.process.bind(this));
    }
}


class ModuleViewer {
  constructor(n, sel_mod, sel_obj, the_mod, view_area, datastore) {
    console.log(`Modviewer ${n}: ${sel_mod} ${sel_obj} ${view_area}`)
    this.n = n;
    this.sel_mod = sel_mod;
    this.the_mod = the_mod;
    this.sel_obj = sel_obj;
    this.view_area = view_area;
    this.datastore = datastore;

    this.sel_obj.onchange = this.UpdateViewArea.bind(this);
    this.sel_mod.onchange = this.UpdateMod.bind(this);
  }

  UpdateModList() {
    let options = "<option value='AUTO'>AUTO</option>";
    for (const v of this.datastore.mod_names) {
        options += `<option value="${v}">${v}</option>`;
    }
    this.sel_mod.innerHTML = options;
    this.UpdateMod();
  }

  GetCurrentMod() {
    const mod_name = this.sel_mod.value;
    if (mod_name == "AUTO") {
        const names = this.datastore.mod_names;
        let pos = names.length - 1 - this.n;
        if (pos < 0) {
            pos = 0;
        }
        return this.datastore.mods[names[pos]]
    }
    return this.datastore.mods[mod_name];
  }

  UpdateMod() {
    let mod = this.GetCurrentMod();
    let options = `<option value='ALL'>ALL</option>`
    for (const v of mod.mems) {
        options += `<option value="${v[0]}">${v[0]}</option>`;
    }
    for (const v of mod.funs) {
        options += `<option value="${v[0]}">${v[0]}</option>`;
    }
    this.sel_obj.innerHTML = options;

    this.the_mod.innerHTML = mod.name;
    this.UpdateViewArea();
  }

  UpdateViewArea() {
    let mod = this.GetCurrentMod();
    const obj_name = this.sel_obj.value;
    console.log(`Update [${mod.name}] [${obj_name}]`);
    let html = "";
    for (const [name, mem] of mod.mems) {
        if (obj_name == "ALL" || obj_name == name) {
            html += mem;
            html += "<hr>";
        }
    }
    for (const [name, fun] of mod.funs) {
        if (obj_name == "ALL" || obj_name == name) {
            html += fun;
            html += "<hr>";
        }
    }

    this.view_area.innerHTML = html;
  }
}


function main() {
    console.log("main");
    const ds = new DataStore();
    const sel_mods = document.getElementsByClassName("sel_mod");
    const the_mods = document.getElementsByClassName("the_mod");
    const sel_objs = document.getElementsByClassName("sel_obj");
    const view_areas = document.getElementsByClassName("view_area");
    for (let i = 0; i < sel_mods.length; ++i) {
        VIEWERS.push(new ModuleViewer(
                i, sel_mods[i], sel_objs[i], the_mods[i], view_areas[i], ds));
    }
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

APP_HTML = f"""<!DOCTYPE html>
<html>
<head>
<style>
{STYLE}
</style
</head>
<body>

<div class=actions>
<p></p>
GLOBAL-OBJ: <select class=global_sel_obj></select>
<p></p>
</div>
<table>
<tr class=row>
<td class=column>{COLUMN_HTML}</td>
<td class=column>{COLUMN_HTML}</td>
<td class=column>{COLUMN_HTML}</td>
<td class=column>{COLUMN_HTML}</td>
<td class=column>{COLUMN_HTML}</td>
</tr>
</table>

<script>
{JS}
</script>
</body>
</html>
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

# ============================================================

MODS: List[Dict] = []


def RenderMem(mem: ir.Mem) -> List[str]:
    out = []
    for line in serialize.MemRenderToAsm(mem):
        if line.startswith(".mem"):
            out.append(f"<span class=mem>{line}</span>")
        else:
            prefix = "&nbsp; &nbsp;" if line.startswith(" ") else ""
            out.append(f"{prefix}{line}")
    return out


def RenderFun(fun: ir.Fun) -> List[str]:
    out = []
    for line in serialize.FunRenderToAsm(fun):
        if line.startswith(".fun"):
            out.append(f"<span class=fun>{line}</span>")
        elif line.startswith(".bbl"):
            out.append(f"<span class=bbl>{line}</span>")
        else:
            prefix = "&nbsp; &nbsp;" if line.startswith(" ") else ""
            out.append(f"{prefix}{line}")
    return out


def RenderArmMem(mem: List[Any]) -> str:
    out = []
    for opc, args in mem:
        a = ' '.join(args)
        if opc == ".mem":
            out.append(f"<span class=mem>{opc} {a}</span>")
        elif opc == ".endmem":
            out.append(f"{opc} {a}")
        else:
            out.append(f"&nbsp; &nbsp;{opc} {a}")
    return out


def RenderArmFun(mem: List[Any]) -> str:
    out = []
    for opc, args in mem:
        a = ' '.join(args)
        if opc == ".fun":
            out.append(f"<span class=fun>{opc} {a}</span>")
        elif opc == ".bbl":
            out.append(f"<span class=bbl>{opc} {a}</span>")
        elif opc == ".endfun":
            out.append(f"<span class=fun>{opc} {a}</span>")
        elif isinstance(opc, arm.Opcode):
            out.append(f"&nbsp; &nbsp;{opc.name}_{opc.variant} {a}")
        else:
            out.append(f"&nbsp; &nbsp;{opc} {a}")
    return out


def Join(lines: List[str]) -> str:
    return "<tt>\n" + "<br>\n".join(lines) + "</tt>\n"


def AddDiffInfo(out: List[Dict]):
    last: Dict[str, List[str]] = {a: b for a, b in out[0]["funs"]}
    for t in out[1:-1]:
        new_funs = []
        for name, fun in t["funs"]:
            old_fun = last.get(name)
            if not old_fun:
                new_funs.append((name, fun))
            else:
                sm = difflib.SequenceMatcher(a=old_fun, b=fun)
                new_fun = []
                for tag, i1, i2, j1, j2 in sm.get_opcodes():
                    if tag == "delete":
                        lines = ["&nbsp; &nbsp;"] * (i2 - i1)
                    else:
                        lines = fun[j1:j2]
                    new_fun += [f"<span class={tag}>{line}</span>"
                                for line in lines]
                new_funs.append((name, new_fun))
            last[name] = fun

        t["funs"] = new_funs


def RenderCpu(name: str, mod: codegen.Unit):
    funs = [(name, RenderArmFun(fun)) for name, fun in mod.funs]
    mems = [(name, RenderArmMem(mem)) for name, mem in mod.mems]
    return {"name": name, "funs": funs, "mems": mems}


def RenderCwerg(name: str, mod: ir.Unit):
    funs = [(fun.name, RenderFun(fun)) for fun in mod.funs]
    mems = [(mem.name, RenderMem(mem)) for mem in mod.mems]
    return {"name": name, "funs": funs, "mems": mems}


def GetModules():
    global MODS
    AddDiffInfo(MODS)
    for t in MODS:
        t["funs"] = [(name, Join(fun)) for name, fun in t["funs"]]
        t["mems"] = [(name, Join(mem)) for name, mem in t["mems"]]
    return bytes(json.dumps(MODS), "utf-8")


def Index():
    return bytes(APP_HTML, "utf-8")


GET_ROUTES = [
    (r'/GetModules', GetModules, 'application/json'),
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


# Deepcopy does not work without this - maybe we have dangling refs?
def CleanUnit(unit: ir.Unit):
    for fun in unit.funs:
        for bbl in fun.bbls:
            for ins in bbl.inss:
                for op in ins.operands:
                    if isinstance(op, ir.Reg):
                        op.def_bbl = None
                        op.def_ins = None


def main():
    parser = argparse.ArgumentParser(description='inspector')
    parser.add_argument('-debug', help='enable webserver debugging',
                        action='store_true')
    parser.add_argument('-port', type=int, help='web server port', default=5000)
    parser.add_argument('input', type=str, help='input file')
    args = parser.parse_args()

    opt_stats: Dict[str, int] = collections.defaultdict(int)
    unit = serialize.UnitParseFromAsm(open(args.input))
    MODS.append(RenderCwerg("orig", unit))

    if MODE == "opt":
        optimize.UnitCfgInit(unit)
        MODS.append(RenderCwerg("prepped", unit))
        optimize.UnitOpt(unit, False)
        CleanUnit(unit)
        MODS.append(RenderCwerg("optimized", unit))
        optimize.UnitCfgExit(unit)
        CleanUnit(unit)
        MODS.append(RenderCwerg("final", unit))
    else:
        stats: Dict[str, int] = collections.defaultdict(int)
        codegen.LegalizeAll(unit, stats, None)
        CleanUnit(unit)
        MODS.append(RenderCwerg("legalized", unit))

        codegen.RegAllocGlobal(unit, stats, None)
        CleanUnit(unit)
        MODS.append(RenderCwerg("global_allocated", unit))

        codegen.RegAllocLocal(unit, stats, None)
        CleanUnit(unit)
        MODS.append(RenderCwerg("locals_allocated", unit))

        arm_mod = codegen.codegen(unit)
        MODS.append(RenderCpu("assembler", arm_mod))

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

    app.run(debug=True, port=5000)
