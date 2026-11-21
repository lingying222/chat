#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""扫描当前目录，生成 manifest.js / manifest.json 目录清单。

用法：
  python build_manifest.py            # 生成一次
  python build_manifest.py --watch    # 监听目录变化，自动重新生成

清单内容：当前目录下所有子文件夹与 HTML 页面（含标题、大小、修改时间）。
index.html 通过 manifest.js 读取清单，新增/删除文件后重新运行本脚本即可刷新导航。
"""

import json
import re
import sys
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
IGNORE_DIRS = {".git", ".github", "node_modules", "__pycache__", ".venv", "venv"}
TITLE_RE = re.compile(r"<title>(.*?)</title>", re.I | re.S)


def read_title(path: Path) -> str:
    """读取 HTML 的 <title>，取不到就用文件名。"""
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
        match = TITLE_RE.search(text)
        if match:
            return re.sub(r"\s+", " ", match.group(1)).strip()
    except Exception:
        pass
    return path.stem


def build_node(path: Path) -> dict:
    files, folders = [], []
    try:
        entries = sorted(path.iterdir(), key=lambda e: (e.is_file(), e.name.lower()))
    except PermissionError:
        entries = []

    for entry in entries:
        if entry.is_dir():
            if entry.name in IGNORE_DIRS:
                continue
            folders.append(build_node(entry))
        elif entry.suffix.lower() == ".html" and entry.name != "index.html":
            stat = entry.stat()
            files.append({
                "name": entry.name,
                "path": entry.relative_to(ROOT).as_posix(),
                "title": read_title(entry),
                "size": stat.st_size,
                "mtime": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M"),
            })

    rel = path.relative_to(ROOT).as_posix() if path != ROOT else ""
    return {"name": path.name if path != ROOT else ".", "path": rel,
            "folders": folders, "files": files}


def snapshot() -> dict:
    """记录当前所有文件的修改时间，用于监听模式判断变化。"""
    state = {}
    for path in ROOT.rglob("*"):
        if any(part in IGNORE_DIRS for part in path.parts):
            continue
        if path.is_file():
            state[str(path)] = path.stat().st_mtime
    return state


def write_manifest(data: dict) -> None:
    (ROOT / "manifest.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    js = ("// 由 build_manifest.py 自动生成，请勿手动编辑\n"
          "window.__MANIFEST__ = "
          + json.dumps(data, ensure_ascii=False, indent=2) + ";\n")
    (ROOT / "manifest.js").write_text(js, encoding="utf-8")


def build() -> dict:
    """清单只包含目录事实，不带生成时间——同一份目录永远得到同一份清单，
    这样自动提交不会因为时间戳变化而反复触发。"""
    return {"root": build_node(ROOT)}


def main() -> None:
    data = build()
    write_manifest(data)
    print("manifest 已生成：", ROOT / "manifest.js")

    if "--watch" in sys.argv:
        current = snapshot()
        print("监听中，目录变化后自动刷新（Ctrl+C 退出）...")
        while True:
            time.sleep(2)
            new_state = snapshot()
            if new_state != current:
                current = new_state
                write_manifest(build())
                print("已刷新：", datetime.now().strftime("%H:%M:%S"))


if __name__ == "__main__":
    main()
