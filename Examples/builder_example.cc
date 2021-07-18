// This example shows how to programmatically build the IR data structures
// equivalent to the code further below.
// This is similar to the UnitParseFromAsm helper which de-serializes textual
// representation of the Cwerg IR.
//
// Build like so:
// * cd ../build; make builder_example.exe
//
// Run like so:
// * cd ../build; ./builder_example.exe 8080
// * point you browser at URL printed to stderr to inspect the IR
// * press ctrl-C to quit
//
//  .fun fibonacci NORMAL [U32] = [U32]
//      .reg U32 [x in out]
//
//  .bbl start
//      poparg in
//      blt 1:U32 in difficult
//      pusharg in
//      ret
//
//  .bbl difficult
//      mov out = 0
//      sub x = in 1
//
//      pusharg x
//      bsr fibonacci
//      poparg x
//
//      add out = out x
//      sub x = in 2
//
//      pusharg x
//      bsr fibonacci
//      poparg x
//
//      add out = out x
//      pusharg out
//      ret

#include "Base/ir.h"
#include "Base/serialize.h"
#include "Util/breakpoint.h"
#include "Util/webserver.h"

#include <chrono>
#include <iomanip>
#include <iostream>
#include <memory>
#include <thread>

namespace {
using namespace cwerg;
using namespace cwerg::base;

Unit MakeFibonacci() {
  Unit unit = UnitNew(StrNew("fibonacci"));
  Fun fun = UnitFunAdd(unit, FunNew(StrNew("fib"), FUN_KIND::NORMAL));
  FunOutputTypes(fun)[0] = DK::U32;
  FunNumOutputTypes(fun) = 1;
  FunInputTypes(fun)[0] = DK::U32;
  FunNumInputTypes(fun) = 1;
  Bbl bbl_start = FunBblAdd(fun, BblNew(StrNew("start")));
  Bbl bbl_difficult = FunBblAdd(fun, BblNew(StrNew("difficult")));
  Reg reg_in = FunRegAdd(fun, RegNew(DK::U32, StrNew("in")));
  Reg reg_out = FunRegAdd(fun, RegNew(DK::U32, StrNew("out")));
  Reg reg_x = FunRegAdd(fun, RegNew(DK::U32, StrNew("x")));
  Const zero = ConstNewU(DK::U32, 0);
  Const one = ConstNewU(DK::U32, 1);
  Const two = ConstNewU(DK::U32, 2);
  // start
  BblInsAdd(bbl_start, InsNew(OPC::POPARG, reg_in));
  BblInsAdd(bbl_start, InsNew(OPC::BLT, one, reg_in, bbl_difficult));
  BblInsAdd(bbl_start, InsNew(OPC::PUSHARG, reg_in));
  BblInsAdd(bbl_start, InsNew(OPC::RET));
  // difficult
  BblInsAdd(bbl_difficult, InsNew(OPC::MOV, reg_out, zero));
  BblInsAdd(bbl_difficult, InsNew(OPC::SUB, reg_x, reg_in, one));
  BblInsAdd(bbl_difficult, InsNew(OPC::PUSHARG, reg_x));
  BblInsAdd(bbl_difficult, InsNew(OPC::BSR, fun));
  BblInsAdd(bbl_difficult, InsNew(OPC::POPARG, reg_x));
  BblInsAdd(bbl_difficult, InsNew(OPC::ADD, reg_out, reg_out, reg_x));
  BblInsAdd(bbl_difficult, InsNew(OPC::SUB, reg_x, reg_in, two));
  BblInsAdd(bbl_difficult, InsNew(OPC::PUSHARG, reg_x));
  BblInsAdd(bbl_difficult, InsNew(OPC::BSR, fun));
  BblInsAdd(bbl_difficult, InsNew(OPC::POPARG, reg_x));
  BblInsAdd(bbl_difficult, InsNew(OPC::ADD, reg_out, reg_out, reg_x));
  BblInsAdd(bbl_difficult, InsNew(OPC::PUSHARG, reg_out));
  BblInsAdd(bbl_difficult, InsNew(OPC::RET));

  return unit;
}

// Below is boilerplate stuff that should go into its own library


WebResponse CodeHandler(base::Unit unit, const WebRequest& request) {
  WebResponse out;
  out.body << WebServer::kHtmlProlog;
  for (Mem mem : UnitMemIter(unit)) {
    out.body << "<hr>\n";
    out.body << "<pre>";
    MemRenderToAsm(mem, &out.body);
    out.body << "</pre>";
  }
  for (Fun fun : UnitFunIter(unit)) {
    out.body << "<hr>\n";
    out.body << "<pre>";
    FunRenderToAsm(fun, &out.body);
    out.body << "</pre>";
  }
  out.body << WebServer::kHtmlEpilog;
  return out;
}

void SleepForever() {
  std::cerr << "execution asserted webserver still active\n";
  std::this_thread::sleep_for(std::chrono::hours(1000));
}

}  // namespace

int main(int argc, const char* argv[]) {
  using namespace std::placeholders;

  if (argc != 2) {
    std::cerr << "you must specify exactly one argument: the port number "
              << "of the webserver for inspecting the IR.";
    return 1;
  }
  const int port = atoi(argv[1]);

  // If the synchronization is turned off, the C++ standard streams are allowed
  // to buffer their I/O independently from their stdio counterparts, which may
  // be considerably faster in some cases.
  std::ios_base::sync_with_stdio(false);

  // Set-up internal memory pools.
  cwerg::InitStripes(1);

  cwerg::base::Unit unit = MakeFibonacci();

  std::cerr << "Launching webserver on port " << port << "\n"
            << "Go to http://localhost:" << port << " to browser the IR\n"
            << "Press Ctrl-C to exit.";
  cwerg::WebServer web_server;
  web_server.handler.push_back(
      WebHandler{"/", "GET", std::bind(CodeHandler, unit, _1)});

  std::thread webserver_thread(&cwerg::WebServer::Start, &web_server, port, "");
  // Make sure the program does not simply abort when an assert is triggered.
  SetAbortHandler(&SleepForever);
  webserver_thread.join();
  return 0;
}
