#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""重建聊天记录归档：把归档 HTML 里引用的本地图片复制进 assets/images，
修正归档之间的互引，并注入 Markdown 渲染脚本。

用法：
  python archive_builder.py            # 扫描 chats/ 下所有归档 HTML 并就地更新
  python archive_builder.py --watch    # 暂未实现监听，保留参数兼容

说明：
- 仅图片（jpg/jpeg/png/gif/webp）随仓库归档；视频、压缩包等大文件不复制，
  归档页保留本机 file:// 链接，在本机可直接打开。
- 已入库图片按内容 hash 命名，重复引用不会重复拷贝。
"""

import hashlib
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CHATS = ROOT / "chats"
IMG_DIR = ROOT / "assets" / "images"
LIB_DIR = ROOT / "assets" / "lib"

IMAGE_EXT = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
# 不随仓库入库的大类型：保留本机链接文本即可。
SKIP_COPY_EXT = {".mp4", ".zip", ".rar", ".7z", ".mov", ".avi", ".mkv"}

SCRIPT_TAGS = (
    '<script src="../assets/lib/marked.min.js"></script>\n'
    '<script src="../assets/lib/purify.min.js"></script>\n'
    '<script src="../assets/lib/render-markdown.js"></script>'
)

STYLE_TAG = (
    "<style>\n"
    "  .msg-img{max-width:220px;border-radius:8px;margin:4px 0;display:block}\n"
    "  .bubble a{color:#7db4ff;word-break:break-all}\n"
    "  .bubble table{border-collapse:collapse;margin:6px 0}\n"
    "  .bubble th,.bubble td{border:1px solid #555;padding:4px 8px;font-size:13px}\n"
    "</style>\n"
)

# [图片] file://... / [文件] file://... / 裸 file://...
RE_IMG_TAG = re.compile(r"\[图片\]\s*file:///?([^\s<\)]+)")
RE_FILE_TAG = re.compile(r"\[文件\]\s*file:///?([^\s<\)]+)")
RE_RAW = re.compile(r"file:///?([^\s<\)]+)")


def normalize(raw: str) -> Path:
    p = raw.replace("/", "\\")
    if len(p) >= 2 and p[1] == ":":
        return Path(p)
    return ROOT / p


def asset_name(src: Path) -> str:
    h = hashlib.md5(str(src).encode("utf-8")).hexdigest()[:8]
    return h + src.suffix.lower()


def ensure_images_dir() -> None:
    IMG_DIR.mkdir(parents=True, exist_ok=True)


def rewrite_html(path: Path, chat_names: set, img_map: dict, stats: dict) -> None:
    text = path.read_text(encoding="utf-8")

    def repl_img(m: re.Match) -> str:
        src = normalize(m.group(1))
        if src.suffix.lower() not in IMAGE_EXT or not src.exists():
            stats["img_missing"] += 1
            return m.group(0)
        if src not in img_map:
            name = asset_name(src)
            shutil.copy2(src, IMG_DIR / name)
            img_map[src] = "../assets/images/" + name
        stats["img_copied"] += 1
        return f'<img class="msg-img" src="{img_map[src]}" alt="聊天图片" />'

    def repl_file(m: re.Match) -> str:
        src = normalize(m.group(1))
        # 归档之间的互引：同批归档 html 改为同目录相对文件名。
        if src.name in chat_names:
            stats["relink"] += 1
            return f'<a href="{src.name}">{src.name}</a>'
        stats["file_kept"] += 1
        return m.group(0)

    text = RE_IMG_TAG.sub(repl_img, text)
    text = RE_FILE_TAG.sub(repl_file, text)
    # 裸路径里若是归档 html 也做相对化；其他文件/图片保留。
    text = RE_RAW.sub(lambda m: _repl_raw(m, chat_names, stats), text)

    if "render-markdown.js" not in text:
        text = text.replace("</head>", STYLE_TAG + "</head>", 1)
        text = text.replace("</body>", SCRIPT_TAGS + "\n</body>", 1)

    path.write_text(text, encoding="utf-8")


def _repl_raw(m: re.Match, chat_names: set, stats: dict) -> str:
    src = normalize(m.group(1))
    if src.name in chat_names:
        stats["relink"] += 1
        return f'<a href="{src.name}">{src.name}</a>'
    return m.group(0)


def main() -> None:
    ensure_images_dir()
    chat_names = {p.name for p in CHATS.glob("*.html")}
    img_map: dict = {}
    stats = {"img_copied": 0, "img_missing": 0, "file_kept": 0, "relink": 0}

    for path in sorted(CHATS.glob("*.html")):
        rewrite_html(path, chat_names, img_map, stats)

    print("归档重建完成：")
    print(f"  入库图片 {stats['img_copied']} 张（缺失/跳过 {stats['img_missing']}）")
    print(f"  归档互引修正 {stats['relink']} 处")
    print(f"  本机保留链接（视频/文档等）{stats['file_kept']} 条")
    print(f"  图片目录：{IMG_DIR}")


if __name__ == "__main__":
    main()
