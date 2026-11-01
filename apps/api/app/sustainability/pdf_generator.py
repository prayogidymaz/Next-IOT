"""ESG PDF export via ReportLab."""

from __future__ import annotations

import io
import uuid
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from app.sustainability.models import EsgScorecard


def render_esg_pdf(scorecard: EsgScorecard, carbon_points: list[tuple[str, float]], water_rows: list[tuple[str, float]]) -> bytes:
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, 800, f"ESG Report — {scorecard.period_month}")
    c.setFont("Helvetica", 11)
    c.drawString(50, 770, f"Environmental: {scorecard.environmental_score}")
    c.drawString(50, 755, f"Social: {scorecard.social_score}")
    c.drawString(50, 740, f"Governance: {scorecard.governance_score}")
    c.drawString(50, 725, f"Overall grade: {scorecard.overall_grade}")
    c.drawString(50, 690, "Carbon trend (sample)")
    y = 670
    for label, kg in carbon_points[:12]:
        c.drawString(60, y, f"{label}: {kg:.2f} kg CO2e")
        y -= 14
    c.drawString(50, y - 10, "Water usage by plot")
    y -= 30
    for plot, liters in water_rows[:10]:
        c.drawString(60, y, f"{plot}: {liters:.1f} L")
        y -= 14
    c.showPage()
    c.save()
    return buf.getvalue()


def store_pdf_local(scorecard_id: uuid.UUID, data: bytes) -> str:
    out_dir = Path("/tmp/exports")
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"esg-{scorecard_id}.pdf"
    path.write_bytes(data)
    return str(path)
