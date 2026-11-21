#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""本地删除服务：接收导航页长按删除请求，删除对应归档 HTML 并重算清单。

启动：python delete_server.py
监听：127.0.0.1:8765
接口：
  GET  /health            探活
  POST /delete?path=xxx   删除 ROOT 内指定 .html（防目录穿越），成功后重建清单
"""

import json
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer

import build_manifest

ROOT = build_manifest.ROOT
HOST = "127.0.0.1"
PORT = 8765
PROTECTED = {
    "index.html", "manifest.js", "manifest.json",
    "build_manifest.py", "delete_server.py",
}


def safe_delete(rel: str):
    """返回 (ok, message)。校验路径在 ROOT 内、只删归档 HTML、不碰受保护文件。"""
    rel = rel.strip().lstrip("/\\")
    target = (ROOT / rel).resolve()
    if not target.is_relative_to(ROOT):
        return False, "路径越界"
    if target.name in PROTECTED:
        return False, "受保护文件不可删除"
    if target.suffix.lower() != ".html":
        return False, "仅支持删除 HTML 页面"
    if not target.exists():
        return False, "文件不存在"
    target.unlink()
    build_manifest.write_manifest(build_manifest.build())
    return True, "已删除"


class Handler(BaseHTTPRequestHandler):
    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def _json(self, code, payload):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self._cors()
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/health":
            self._json(200, {"ok": True})
        else:
            self._json(404, {"ok": False, "error": "not found"})

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path != "/delete":
            self._json(404, {"ok": False, "error": "not found"})
            return
        qs = urllib.parse.parse_qs(parsed.query)
        rel = (qs.get("path") or [""])[0]
        ok, msg = safe_delete(rel)
        self._json(200 if ok else 400, {"ok": ok, "message": msg})

    def log_message(self, fmt, *args):
        print("[delete_server]", fmt % args)


if __name__ == "__main__":
    print(f"删除服务已启动：http://{HOST}:{PORT} （Ctrl+C 退出）")
    HTTPServer((HOST, PORT), Handler).serve_forever()
