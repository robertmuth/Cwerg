#pragma once

#include <functional>
#include <sstream>
#include <string>

namespace cwerg {

constexpr const std::string_view kMimeTypeCSS = "text/css";
constexpr const std::string_view kMimeTypeJS = "application/x-javascript";
constexpr const std::string_view kMimeTypeHTML = "text/html";
constexpr const std::string_view kMimeTypeText = "text/plain";
constexpr const std::string_view kMimeTypeJPEG = "image/jpeg";

std::string TimeStringNow();

struct WebRequest {
  std::string_view method;
  std::string_view raw_path;
  std::string_view protocol;
  std::vector<std::pair<std::string_view, std::string_view>> header;
};

struct WebResponse {
  unsigned code = 200;
  std::string code_str = "OK";
  std::vector<std::pair<std::string, std::string>> header;
  std::ostringstream body;

  void AddMimeTypeToHeader(std::string_view mime_type = kMimeTypeHTML) {
    header.emplace_back(std::make_pair("Content-Type", mime_type));
  }

  void AddDateToHeader(std::string_view date = TimeStringNow()) {
    header.emplace_back(std::make_pair("Date", date));
  }
};

struct WebHandler {
  std::string path;
  std::string method;
  std::function<WebResponse(const WebRequest&)> handler;
};

struct WebServer {
  std::vector<WebHandler> handler;

  bool shut_down = false;
  bool Start(int port, std::string_view host);
};
}  // namespace cwerg
