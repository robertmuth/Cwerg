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

struct HeaderAttribute {
  std::string key;
  std::string value;
};

struct WebRequest {
  std::string_view method;
  std::string_view raw_path;
  std::string_view protocol;
  std::vector<HeaderAttribute> header;
};



struct WebResponse {
  unsigned code = 200;
  std::string code_str = "OK";
  std::vector<HeaderAttribute> header;
  std::ostringstream body;

  void AddMimeTypeToHeader(std::string_view mime_type = kMimeTypeHTML) {
    header.emplace_back(HeaderAttribute{"Content-Type", std::string(mime_type)});
  }

  void AddDateToHeader(std::string_view date = TimeStringNow()) {
    header.emplace_back(HeaderAttribute{"Date", std::string(date)});
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

  void Shutdown();
  static const std::string_view kHtmlProlog;
  static const std::string_view kHtmlEpilog;
};
}  // namespace cwerg
