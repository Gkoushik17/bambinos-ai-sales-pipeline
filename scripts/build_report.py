#!/usr/bin/env python3
"""Render report/Case_Report.md to report/Case_Report.pdf.  Requires: pip install markdown weasyprint"""
from pathlib import Path
import markdown
from weasyprint import HTML

ROOT = Path(__file__).resolve().parent.parent
md = (ROOT / "report" / "Case_Report.md").read_text(encoding="utf-8")
body = markdown.markdown(md, extensions=["tables", "md_in_html", "sane_lists"])

CSS = """
@page { size: A4; margin: 16mm 14mm 16mm 14mm;
  @bottom-left { content: "Bambinos.live · AI Program Manager (Sales) · Case Report"; font-size: 8pt; color: #64748b; }
  @bottom-right { content: "Page " counter(page) " / " counter(pages); font-size: 8pt; color: #64748b; } }
body { font-family: "Helvetica Neue", Helvetica, Arial, sans-serif; font-size: 9.4pt; line-height: 1.42; color: #0f172a; }
.cover { border-left: 6px solid #c8102e; padding: 4mm 0 4mm 6mm; margin-bottom: 6mm; }
.kicker { color: #c8102e; font-weight: 700; font-size: 8.5pt; letter-spacing: .06em; }
h1.title { font-size: 22pt; margin: 2mm 0 1mm; line-height: 1.15; }
.subtitle { font-size: 11pt; color: #334155; margin: 0 0 2mm; }
.meta { font-size: 8.5pt; color: #64748b; margin: 0; }
h2 { font-size: 13.5pt; color: #c8102e; border-bottom: 1.5px solid #e2e8f0; padding-bottom: 1.5mm; margin: 6mm 0 2.5mm; page-break-after: avoid; }
h3 { font-size: 10.8pt; color: #1e293b; margin: 4.5mm 0 1.8mm; page-break-after: avoid; }
p { margin: 1.4mm 0 2mm; }
table { width: 100%; border-collapse: collapse; margin: 1.5mm 0 3mm; font-size: 8.2pt; page-break-inside: auto; }
tr { page-break-inside: avoid; }
th { background: #1e293b; color: #fff; text-align: left; padding: 1.6mm 1.8mm; font-weight: 600; }
td { border-bottom: 0.6px solid #e2e8f0; padding: 1.4mm 1.8mm; vertical-align: top; }
tr:nth-child(even) td { background: #f8fafc; }
code { font-family: Menlo, Consolas, monospace; font-size: 8pt; background: #f1f5f9; padding: 0 1mm; border-radius: 2px; }
hr { border: none; border-top: 1px solid #e2e8f0; margin: 4mm 0; }
.diagram { border: 1px solid #e2e8f0; border-radius: 6px; padding: 2mm; margin: 2mm 0 3mm; }
.diagram svg { width: 100%; height: auto; }
ul, ol { margin: 1mm 0 2mm 5mm; padding-left: 3mm; } li { margin: 0.8mm 0; }
.appendix { font-size: 8.4pt; color: #334155; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px; padding: 2mm 4mm; }
strong { color: #0f172a; }
th strong { color: #fff; }
"""
html = f"<!doctype html><html><head><meta charset='utf-8'><title>Bambinos Case Report</title><style>{CSS}</style></head><body>{body}</body></html>"
out = ROOT / "report" / "Case_Report.pdf"
HTML(string=html, base_url=str(ROOT)).write_pdf(out)
print("wrote", out)
