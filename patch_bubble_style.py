#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Patch existing chat HTML files: inject/replace the bubble style block."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CHATS = ROOT / "chats"

NEW_STYLE = (
    '<style>\n'
    '  .msg-img{max-width:220px;border-radius:8px;margin:4px 0;display:block}\n'
    '  .bubble a{color:#7db4ff;word-break:break-all}\n'
    '  .bubble table{border-collapse:collapse;margin:6px 0}\n'
    '  .bubble th,.bubble td{border:1px solid #555;padding:4px 8px;font-size:13px}\n'
    '  .bubble ul,.bubble ol{padding-left:20px;margin:4px 0;list-style-position:inside}\n'
    '  .bubble li{margin:2px 0}\n'
    '  .bubble li::marker{font-size:0.9em}\n'
    '  .bubble{overflow:hidden}\n'
    '  .bubble img{max-width:100%;height:auto;border-radius:6px;margin:4px 0}\n'
    '  /* Markdown list bullets inside bubbles */\n'
    '  .bubble ul{list-style:none;padding-left:0}\n'
    '  .bubble li{padding-left:12px;position:relative}\n'
    '  .bubble li::before{content:"\\2022";position:absolute;left:0;font-size:0.9em;color:#888}\n'
    '</style>\n'
)

# Pattern: match the existing STYLE_TAG block (the second <style>...</style> block,
# i.e. the one that doesn't contain the main body styles)
RE_STYLE_BLOCK = re.compile(
    r'<style>\s*\.msg-img.*?</style>',
    re.DOTALL
)

for path in sorted(CHATS.glob("*.html")):
    text = path.read_text(encoding="utf-8")
    if ".bubble ul" in text:
        # Already patched
        print(f"  skip (already patched): {path.name}")
        continue
    new_text, count = RE_STYLE_BLOCK.subn(NEW_STYLE, text)
    if count:
        path.write_text(new_text, encoding="utf-8")
        print(f"  patched: {path.name}")
    else:
        # No existing style block – insert before </head>
        new_text = text.replace("</head>", NEW_STYLE + "</head>", 1)
        path.write_text(new_text, encoding="utf-8")
        print(f"  inserted: {path.name}")
