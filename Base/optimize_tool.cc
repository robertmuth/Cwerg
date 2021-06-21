
#include "Base/liveness.h"
#include "Base/optimize.h"
#include "Base/reg_stats.h"
#include "Base/serialize.h"
#include "Util/breakpoint.h"
#include "Util/parse.h"
#include "Util/switch.h"
#include "Util/webserver.h"

#include <chrono>
#include <iomanip>
#include <iostream>
#include <memory>
#include <thread>

namespace {
using namespace cwerg;
using namespace cwerg::base;

// +-prefix converts an enum the underlying type
template <typename T>
constexpr auto operator+(T e) noexcept
    -> std::enable_if_t<std::is_enum<T>::value, std::underlying_type_t<T>> {
  return static_cast<std::underlying_type_t<T>>(e);
}

void UnitCfgInit(Unit unit) {
  for (Fun fun : UnitFunIter(unit)) FunCfgInit(fun);
}

void UnitCfgExit(Unit unit) {
  for (Fun fun : UnitFunIter(unit)) FunCfgExit(fun);
}

void UnitOptBasic(Unit unit, bool dump_reg_stats) {
  for (Fun fun : UnitFunIter(unit)) {
    if (FunKind(fun) != FUN_KIND::NORMAL) continue;
    FunOptBasic(fun, true);
    if (dump_reg_stats) {
      FunComputeRegStatsExceptLAC(fun);
      FunNumberReg(fun);
      FunComputeLivenessInfo(fun);
      FunComputeRegStatsLAC(fun);
      const FunRegStats rs = FunCalculateRegStats(fun);
      std::cout << "# " << std::setw(30) << std::left << Name(fun)
                << " RegStats: " << rs << "\n";
    }
  }
}

constexpr uint8_t StdDKMapping(uint8_t i) {
  const DK rk = DK(i);
  if (rk == DK::S8 || rk == DK::S16 || rk == DK::S32 || rk == DK::A32 ||
      rk == DK::U8 || rk == DK::U16 || rk == DK::U32 || rk == DK::C32) {
    return +DK::S32;
  } else if (rk == DK::S64 || rk == DK::U64 || rk == DK::A64 || rk == DK::C64) {
    return +DK::S64;
  } else if (rk == DK::F32 || rk == DK::F64) {
    return +rk;
  } else {
    return +DK::INVALID;
  }
}

// based on:
// https://stackoverflow.com/questions/19019252/create-n-element-constexpr-array-in-c11
template <class Function, std::size_t... Indices>
constexpr auto make_array_helper(Function f, std::index_sequence<Indices...>)
    -> std::array<typename std::result_of<Function(std::size_t)>::type,
                  sizeof...(Indices)> {
  return {{f(Indices)...}};
}

const DK_MAP kStdRKMap =
    make_array_helper(StdDKMapping, std::make_index_sequence<256>{});

void UnitOpt(Unit unit, bool dump_reg_stats) {
  for (Fun fun : UnitFunIter(unit)) {
    if (FunKind(fun) != FUN_KIND::NORMAL) continue;
    FunOpt(fun, kStdRKMap);
    if (dump_reg_stats) {
      FunComputeRegStatsExceptLAC(fun);
      FunNumberReg(fun);
      FunComputeLivenessInfo(fun);
      FunComputeRegStatsLAC(fun);
      const FunRegStats rs = FunCalculateRegStats(fun);

      DK_LAC_COUNTS local_stats = FunComputeBblRegUsageStats(fun, kStdRKMap);
      std::cout << "# " << std::setw(30) << std::left << Name(fun)
                << " RegStats: " << rs << "  " << local_stats << "\n";
    }
  }
}

WebResponse DefaultHandler(const WebRequest& request) {
  WebResponse out;

  out.body << WebServer::kHtmlProlog;
  out.body << "<h1>Debug Console</h1>\n";

  RenderBreakPointHTML(&out.body);

  out.body << "<h2>Code</h2>\n";
  out.body << "<a href='/code'>Code</a>\n";

  out.body << "<h2>BST Stats</h2>\n";
  out.body << "<pre>\n";
  DumpBstStates(out.body);
  out.body << "</pre>\n";

  out.body << "<h2>Stripes</h2>\n";
  out.body << "<pre>\n";
  cwerg::StripeGroup::DumpAllGroups(out.body);
  out.body << "</pre>\n";

  out.body << WebServer::kHtmlEpilog;
  return out;
}

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

SwitchInt32 sw_multiplier("multiplier",
                          "adjust multiplies for item pool sizes",
                          4);

SwitchString sw_mode("mode", "mode indicating what to do", "optimize");

SwitchBool sw_show_stats("show_stats", "emit stats to cout");

SwitchBool sw_break_after_load("break_after_load", "break after load IR");

SwitchInt32 sw_webserver_port("webserver_port",
                              "launch webserver at given port",
                              -1);

void SleepForever() {
  std::cerr << "execution asserted webserver still active\n";
  std::this_thread::sleep_for(std::chrono::hours(1000));
}

BreakPoint bp_after_load("after_load");
BreakPoint bp_before_exit("before_exit");

}  // namespace

int main(int argc, const char* argv[]) {
  if (argc != cwerg::SwitchBase::ParseArgv(argc, argv, &std::cerr)) {
    std::cerr << "possibly unused commandline args\n";
    return 1;
  }

  // If the synchronization is turned off, the C++ standard streams are allowed
  // to buffer their I/O independently from their stdio counterparts, which may
  // be considerably faster in some cases.
  std::ios_base::sync_with_stdio(false);

  cwerg::InitStripes(sw_multiplier.Value());

  const std::vector<char> input = cwerg::SlurpDataFromStream(&std::cin);
  cwerg::base::Unit unit = cwerg::base::UnitParseFromAsm(
      "unit", std::string_view(input.data(), input.size()), {});
  if (unit.isnull()) return 1;

  std::unique_ptr<cwerg::WebServer> webserver;
  std::unique_ptr<std::thread> webserver_thread;
  const bool launch_webserver = sw_webserver_port.Value() >= 0;
  if (launch_webserver) {
    using namespace std::placeholders;
    std::cerr << "Launching webserver on port " << sw_webserver_port.Value()
              << "\n";
    webserver = std::make_unique<cwerg::WebServer>();
    webserver->handler.push_back(
        WebHandler{"/code", "GET", std::bind(CodeHandler, unit, _1)});
    webserver->handler.push_back(
        WebHandler{"/resume/", "GET", ResumeBreakpointHandler});
    webserver->handler.push_back(WebHandler{"/", "GET", DefaultHandler});

    webserver_thread =
        std::make_unique<std::thread>(&cwerg::WebServer::Start, webserver.get(),
                                      sw_webserver_port.Value(), "");
    SetAbortHandler(&SleepForever);
  }

  if (launch_webserver && sw_break_after_load.Value()) {
    bp_after_load.Break();
  }

  if (sw_mode.Value() == "optlite") {
    UnitCfgInit(unit);
    UnitOptBasic(unit, true);
    UnitCfgExit(unit);
    std::ostringstream out;
    cwerg::base::UnitRenderToAsm(unit, &out);
    std::cout << out.str();
  } else if (sw_mode.Value() == "optimize") {
    UnitCfgInit(unit);
    UnitOpt(unit, true);
    UnitCfgExit(unit);
    std::ostringstream out;
    cwerg::base::UnitRenderToAsm(unit, &out);
    std::cout << out.str();
  } else if (sw_mode.Value() == "cfg") {
    UnitCfgInit(unit);
    std::ostringstream out;
    cwerg::base::UnitRenderToAsm(unit, &out);
    std::cout << out.str();
  } else if (sw_mode.Value() == "cfg2") {
    UnitCfgInit(unit);
    UnitCfgExit(unit);
    std::ostringstream out;
    cwerg::base::UnitRenderToAsm(unit, &out);
    std::cout << out.str();
  } else if (sw_mode.Value() == "serialize") {
    std::ostringstream out;
    cwerg::base::UnitRenderToAsm(unit, &out);
    std::cout << out.str();
  } else {
    std::cerr << "unknown mode [" << sw_mode.Value() << "]\n";
  }
  if (sw_show_stats.Value()) {
    cwerg::StripeGroup::DumpAllGroups(std::cout);
  }

  // If we spawned a webserver break before exiting so we can expect the  code.
  if (sw_webserver_port.Value() >= 0) {
    bp_before_exit.Break();
    webserver_thread->join();
  }
  return 0;
}
