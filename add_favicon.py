#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Add favicon link to all chat HTML files."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CHATS = ROOT / "chats"

FAVICON_TAG = '  <link rel="icon" type="image/x-icon" href="../favicon.ico">\n'

for path in sorted(CHATS.glob("*.html")):
    text = path.read_text(encoding="utf-8")
    if 'favicon.ico' in text:
        continue
    # insert after <meta name="viewport" line
    text = text.replace(
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">\n',
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">\n' + FAVICON_TAG
    )
    path.write_text(text, encoding="utf-8")
    print(f"  added favicon to {path.name}")
