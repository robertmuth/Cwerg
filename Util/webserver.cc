#include <Util/assert.h>
#include <Util/webserver.h>

#include <netinet/in.h>
#include <unistd.h>
#include <iostream>

namespace cwerg {
namespace {

const int kMaxHeaderSize = 8 * 1024;
const int kConnectionBufferSize = 4;

void ltrim(std::string_view* s) {
  while (!s->empty() && (*s)[0] == ' ') {
    s->remove_prefix(1);
  }
}

WebRequest ParseHeaders(std::string_view header) {
  WebRequest request;
  size_t pos = header.find("\r\n");
  ASSERT(pos != std::string_view::npos, "bad header");
  std::string_view start_line = header.substr(0, pos);
  header.remove_prefix(pos + 2);
  {
    pos = start_line.find(' ');
    ASSERT(pos != std::string_view::npos, "bad header");
    request.method = start_line.substr(0, pos);
    start_line.remove_prefix(pos + 1);
    ltrim(&start_line);
    pos = start_line.find(' ');
    ASSERT(pos != std::string_view::npos, "bad header");
    request.raw_path = start_line.substr(0, pos);
    start_line.remove_prefix(pos + 1);
    ltrim(&start_line);
    request.protocol = start_line;
  }
  while (true) {
    pos = header.find("\r\n");
    if (pos == 0) {
      break;
    }
    std::string_view line = header.substr(0, pos);
    header.remove_prefix(pos + 2);
    pos = line.find(':');
    ASSERT(pos != std::string_view::npos, "bad header");
    std::string_view key = line.substr(0, pos);
    line.remove_prefix(pos + 1);
    ltrim(&line);
    request.header.emplace_back(HeaderAttribute{std::string(key), std::string(line)});
  }
  return request;
}

void SendResponse(int sc, const WebResponse& response) {
  std::ostringstream header;
  header << "HTTP/1.0 " << response.code << " " << response.code_str << "\r\n";
  for (const auto& [key, val] : response.header) {
    header << key << ": " << val << "\r\n";
  }
  const std::string body = response.body.str();
  header << "Content-Length:" << body.size() << "\r\n\r\n";
  const std::string head = header.str();

  ssize_t res = write(sc, head.data(), head.size());
  ASSERT( res >= 0, "writing http header data failed");
  res = write(sc, body.data(), body.size());
  ASSERT( res >= 0, "writing http body data failed");
}

WebResponse DefaultHandler(const WebRequest& request) {
  WebResponse out;
  out.code = 404;
  out.code_str = "Error";
  out.AddDateToHeader();
  out.AddMimeTypeToHeader();
  out.body << "<html><body>bad request:<pre>" << request.raw_path << "\n\n";
  for (const auto& [key, val] : request.header) {
    out.body << key << " " << val << "\n";
  }
  out.body << "</pre></body></html>";
  return out;
}

}  // namespace

std::string TimeStringNow() {
  char buf[128];
  time_t now = time(nullptr);
  struct tm tstruct = *gmtime(&now);
  strftime(buf, sizeof(buf), "%a, %d %b %Y %H:%M:%S %Z", &tstruct);
  return std::string(buf);
}

bool WebServer::Start(int port, std::string_view host) {
  // TODO: make use of host
  int sc = socket(AF_INET, SOCK_STREAM, 0);
  ASSERT(sc >= 0, "Cannot start server");

  struct sockaddr_in server_addr;
  server_addr.sin_family = AF_INET;
  server_addr.sin_addr.s_addr = INADDR_ANY;
  server_addr.sin_port = htons(port);

  int status = bind(sc, (struct sockaddr*)&server_addr, sizeof(server_addr));
  ASSERT(status >= 0, "cannot bind server address with port " << port);

  listen(sc, kConnectionBufferSize);

  while (!shut_down) {
    struct sockaddr_in client_addr;
    socklen_t client_addr_size;
    int client_sc =
        accept(sc, (struct sockaddr*)&client_addr, &client_addr_size);
    // TODO: this pathetic error handling is good enough for our purposes
    ASSERT(client_sc >= 0, "client connection failed");
    char header[kMaxHeaderSize];
    ssize_t header_len = read(client_sc, header, sizeof header);
    ASSERT(header_len >= 0, "failed to read header");
    WebRequest request = ParseHeaders(std::string_view(header, header_len));
    for (const WebHandler& h : handler) {
      if (request.raw_path.substr(0, h.path.size()) == h.path &&
          request.method == h.method) {
        SendResponse(client_sc, h.handler(request));
        break;
      }
    }
    SendResponse(client_sc, DefaultHandler(request));
  }
  return true;
}

void WebServer::Shutdown(){
  shut_down = true;
}


const std::string_view WebServer::kHtmlProlog(R"(<!doctype html>
<html>
<head>
<meta charset=utf-8">
<style>
body {
    font-family: sans-serif;
}
</style>
</head>
<body>
)");

const std::string_view WebServer::kHtmlEpilog(R"(
</body>
</html>
)");

}  // namespace cwerg

#if 0
cwerg::WebResponse hello(const cwerg::WebRequest& request) {
  cwerg::WebResponse out;
  out.AddMimeTypeToHeader();
  out.AddDateToHeader();
  out.body << "<html><body>Hello World!</body></html>";
  return out;
}

int main(int argc, const char* argv[]) {
  cwerg::WebServer server;
  server.handler.emplace_back(cwerg::WebHandler{"/index.html", "GET", hello});
  int port = 5000;
  std::cout << "Listening on port " << port << "\n";
  server.Start(port, "0.0.0.0");

  return 0;
}
#endif

