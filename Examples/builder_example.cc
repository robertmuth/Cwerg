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
// Note: actual IR construction was moved to fib_ir.h

#include "BE/Base/ir.h"
#include "BE/Base/serialize.h"
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

#include "Examples/fib_ir.h"

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
