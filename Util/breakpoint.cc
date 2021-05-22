#include "Util/breakpoint.h"

namespace cwerg {

BreakPoint* BreakPoint::head = nullptr;

WebResponse ResumeBreakpointHandler(const WebRequest& request) {
  std::string_view path = request.raw_path.substr(1);
  auto pos = path.find("/");
  bool success = false;
  if (pos != std::string_view::npos) {
    path.remove_prefix(pos + 1);
    success = BreakPoint::ResumeByName(path);
  }
  WebResponse out;
  if (success) {
    out.body << "<html><body>resuming breakpoint [" << path
             << "]</body></html>";
  } else {
    out.body << "<html><body>failed to resume breakpoint [" << path
             << "]</body></html>";
  }
  return out;
}

void RenderBreakPointHTML(std::ostream* out) {
  *out << "<h2>Breakpoints</h2>\n";
  *out << "<table>\n";
  for (const BreakPoint* w : BreakPoint::GetAll()) {
    *out << "<tr>\n"
         << "<td>" << w->name() << "</td>";
    if (w->ready()) {
      *out << "<td>inactive<td></td>";
    } else {
      *out << "<td><a href='/resume/" << w->name() << "'>Resume</a></td>";
    }
    *out << "</tr>\n";
  }
  *out << "</table>\n";
}

}  // namespace cwerg
