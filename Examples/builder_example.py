#!/usr/bin/python3

from typing import Optional
import argparse
import http.server

from BE.Base import serialize
from BE.Base import ir
from BE.Base import opcode_tab as o
from BE.Base import optimize

"""
  The point of this example is to show how to programmatically build the IR
  data structures equivalent to the code below:

  .fun fibonacci NORMAL [U32] = [U32]
      .reg U32 [x in out] 
  
  .bbl start
      poparg in
      blt 1:U32 in difficult
      pusharg in
      ret
  
  .bbl difficult
      mov out = 0
      sub x = in 1
  
      pusharg x
      bsr fibonacci
      poparg x
  
      add out = out x
      sub x = in 2
  
      pusharg x
      bsr fibonacci
      poparg x
  
      add out = out x
      pusharg out
      ret
"""


def BuildExample() -> ir.Unit:
    unit = ir.Unit("fib")
    fun_fib = unit.AddFun(ir.Fun("fib", o.FUN_KIND.NORMAL, [o.DK.U32], [o.DK.U32]))
    bbl_start = fun_fib.AddBbl(ir.Bbl("start"))
    bbl_difficult = fun_fib.AddBbl(ir.Bbl("difficult"))

    reg_in = fun_fib.AddReg(ir.Reg("in", o.DK.U32))
    reg_x = fun_fib.AddReg(ir.Reg("x", o.DK.U32))
    reg_out = fun_fib.AddReg(ir.Reg("out", o.DK.U32))

    bbl_start.AddIns(ir.Ins(o.POPARG, [reg_in]))
    bbl_start.AddIns(ir.Ins(o.BLT, [ir.Const(o.DK.U32, 1), reg_in, bbl_difficult]))
    bbl_start.AddIns(ir.Ins(o.PUSHARG, [reg_in]))
    bbl_start.AddIns(ir.Ins(o.RET, []))

    bbl_difficult.AddIns(ir.Ins(o.MOV, [reg_out, ir.Const(o.DK.U32, 0)]))
    bbl_difficult.AddIns(ir.Ins(o.SUB, [reg_x, reg_in, ir.Const(o.DK.U32, 1)]))

    bbl_difficult.AddIns(ir.Ins(o.PUSHARG, [reg_x]))
    bbl_difficult.AddIns(ir.Ins(o.BSR, [fun_fib]))
    bbl_difficult.AddIns(ir.Ins(o.POPARG, [reg_x]))
    bbl_difficult.AddIns(ir.Ins(o.ADD, [reg_out, reg_out, reg_x]))

    bbl_difficult.AddIns(ir.Ins(o.SUB, [reg_x, reg_in, ir.Const(o.DK.U32, 2)]))
    bbl_difficult.AddIns(ir.Ins(o.PUSHARG, [reg_x]))
    bbl_difficult.AddIns(ir.Ins(o.BSR, [fun_fib]))
    bbl_difficult.AddIns(ir.Ins(o.POPARG, [reg_x]))
    bbl_difficult.AddIns(ir.Ins(o.ADD, [reg_out, reg_out, reg_x]))

    bbl_difficult.AddIns(ir.Ins(o.PUSHARG, [reg_out]))
    bbl_difficult.AddIns(ir.Ins(o.RET, []))
    return unit


UNIT: Optional[ir.Unit] = None

PROLOG = f"""<!DOCTYPE html>
<html>
<head>
</head>
<body>
<pre>
"""

EPILOG = """
</pre>
</body>
</html>
"""


class MyRequestHandler(http.server.BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        http.server.BaseHTTPRequestHandler.__init__(self, *args, **kwargs)

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        content = PROLOG + "\n".join(serialize.UnitRenderToASM(UNIT)) + EPILOG
        self.wfile.write(content.encode("utf-8"))


def main():
    global UNIT
    parser = argparse.ArgumentParser(description="build_example")
    parser.add_argument("--port", type=int, default=0, help='start webserver if port != 0')
    parser.add_argument("--optimize", action='store_true', help='optimize')

    args = parser.parse_args()

    UNIT = BuildExample()

    if args.optimize:
        optimize.UnitCfgInit(UNIT)
        # Most noticeable effects will be bbl and reg live-range splitting
        optimize.UnitOptBasic(UNIT, None)

    if args.port > 0:
        http_server = http.server.HTTPServer(("", args.port), MyRequestHandler)
        print(f"Starting HTTP server at http://localhost:{args.port}")
        try:
            http_server.serve_forever()
        except KeyboardInterrupt:
            pass
        print('Stopping HTTP server')
        http_server.server_close()
    else:
        print("\n".join(serialize.UnitRenderToASM(UNIT)))


if __name__ == "__main__":
    main()
