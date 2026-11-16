#!/usr/bin/env python3
"""Gera index.html (página completa, para servir no Coolify/nginx) a partir de artifact.html
(fonte publicada como artefato no claude.ai, que não leva <html>/<head>)."""
import re, pathlib
root = pathlib.Path(__file__).resolve().parent.parent
src = (root / "artifact.html").read_text(encoding="utf-8")
title = re.search(r"<title>(.*?)</title>", src).group(1)
body = re.sub(r"<title>.*?</title>\s*", "", src, count=1)
body = re.sub(r'<meta name="claude:viewport-fit-sides"[^>]*>\s*', "", body, count=1)
html = f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title}</title>
<style>:root{{color-scheme:light}}body{{margin:0;font:14px system-ui,sans-serif}}img{{max-width:100%}}[hidden]{{display:none!important}}</style>
</head>
<body>
{body}
</body>
</html>
"""
(root / "index.html").write_text(html, encoding="utf-8")
print("index.html gerado:", len(html), "bytes")
