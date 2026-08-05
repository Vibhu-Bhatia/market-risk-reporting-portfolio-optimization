"""One-page executive market-risk PDF pack generation."""

from datetime import date
from pathlib import Path
from typing import Any

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

import config


def generate_commentary(var_estimate: float, breaches: list[dict[str, Any]], exceptions: Any) -> str:
    """Generate deterministic commentary from VaR status and the most frequent reconciliation exception type."""
    breached = [item["limit_name"] for item in breaches if item["status"] == "BREACH"]
    limit_text = f"Breaches require review: {', '.join(breached)}." if breached else "All monitored portfolio limits are within tolerance."
    exception_text = "No reconciliation exceptions were identified." if exceptions.empty else f"{len(exceptions)} reconciliation exception(s) were identified; the leading type is {exceptions['exception_type'].mode().iloc[0]}."
    return f"One-day 99% VaR is ${var_estimate:,.0f}. {limit_text} {exception_text}"


def generate_risk_pack(var_summary: dict[str, float], breaches: list[dict[str, Any]], exceptions: Any, output_path: Path) -> Path:
    """Render a concise one-page PDF risk pack with VaR, controls, reconciliation and commentary sections."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    pdf = canvas.Canvas(str(output_path), pagesize=letter)
    y = config.PDF_PAGE_HEIGHT - config.PDF_MARGIN
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(config.PDF_MARGIN, y, f"Daily Market Risk Pack | {date.today().isoformat()}")
    y -= config.PDF_LINE_HEIGHT * 2
    pdf.setFont("Helvetica-Bold", 11)
    pdf.drawString(config.PDF_MARGIN, y, "Value at Risk")
    pdf.setFont("Helvetica", 10)
    for name, value in var_summary.items():
        y -= config.PDF_LINE_HEIGHT
        pdf.drawString(config.PDF_MARGIN, y, f"{name}: ${value:,.0f}")
    y -= config.PDF_LINE_HEIGHT * 2
    pdf.setFont("Helvetica-Bold", 11)
    pdf.drawString(config.PDF_MARGIN, y, "Limit Controls")
    pdf.setFont("Helvetica", 10)
    for item in breaches:
        if item["status"] == "BREACH":
            y -= config.PDF_LINE_HEIGHT
            pdf.drawString(config.PDF_MARGIN, y, f"{item['status']} | {item['limit_name']}: {item['current_value']:.2%}" if "Single" in item["limit_name"] or "Sector" in item["limit_name"] else f"{item['status']} | {item['limit_name']}: ${item['current_value']:,.0f}")
    y -= config.PDF_LINE_HEIGHT * 2
    pdf.setFont("Helvetica-Bold", 11)
    pdf.drawString(config.PDF_MARGIN, y, "Management Commentary")
    y -= config.PDF_LINE_HEIGHT
    pdf.setFont("Helvetica", 10)
    pdf.drawString(config.PDF_MARGIN, y, generate_commentary(var_summary["Parametric 99%"], breaches, exceptions)[:130])
    pdf.save()
    return output_path
