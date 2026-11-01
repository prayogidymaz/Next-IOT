"""Export report templates to PDF, CSV, Excel."""

from __future__ import annotations

import csv
import io
import uuid
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from sqlalchemy.ext.asyncio import AsyncSession

from app.reports.models import ReportGeneration, ReportTemplate


def render_pdf(template: ReportTemplate) -> bytes:
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, 800, template.name)
    c.setFont("Helvetica", 10)
    c.drawString(50, 780, template.description[:200])
    sections = template.config_json.get("sections")
    y = 750
    if isinstance(sections, list):
        for sec in sections[:20]:
            if isinstance(sec, dict):
                title = str(sec.get("type", "section"))
                c.drawString(60, y, f"- {title}")
                y -= 14
    c.showPage()
    c.save()
    return buf.getvalue()


def render_csv(template: ReportTemplate) -> bytes:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["report", template.name])
    writer.writerow(["description", template.description])
    sections = template.config_json.get("sections")
    if isinstance(sections, list):
        writer.writerow(["sections"])
        for sec in sections:
            writer.writerow([str(sec)])
    return buf.getvalue().encode("utf-8")


def render_excel(template: ReportTemplate) -> bytes:
    from openpyxl import Workbook

    wb = Workbook()
    ws = wb.active
    ws.title = "Report"
    ws["A1"] = template.name
    ws["A2"] = template.description
    sections = template.config_json.get("sections")
    if isinstance(sections, list):
        row = 4
        for sec in sections:
            ws.cell(row=row, column=1, value=str(sec))
            row += 1
    out = io.BytesIO()
    wb.save(out)
    return out.getvalue()


async def generate_report(db: AsyncSession, template: ReportTemplate, fmt: str) -> ReportGeneration:
    gen = ReportGeneration(template_id=template.id, status="running")
    db.add(gen)
    await db.flush()
    if fmt == "csv":
        data = render_csv(template)
        ext = "csv"
    elif fmt == "excel":
        data = render_excel(template)
        ext = "xlsx"
    else:
        data = render_pdf(template)
        ext = "pdf"
    out_dir = Path("/tmp/reports")
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{gen.id}.{ext}"
    path.write_bytes(data)
    gen.status = "completed"
    gen.file_url = str(path)
    await db.commit()
    await db.refresh(gen)
    return gen


async def render_template(db: AsyncSession, template_id: uuid.UUID, fmt: str) -> ReportGeneration:
    template = await db.get(ReportTemplate, template_id)
    if template is None:
        raise ValueError("template not found")
    return await generate_report(db, template, fmt)
