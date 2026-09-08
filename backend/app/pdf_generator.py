"""
PDF report generation (used by GET /reports/{id}/download), Step 6.
Built with reportlab.
"""
import io

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
)
from reportlab.lib import colors

from app.models import Report, Scan


def generate_report_pdf(scan: Scan, report: Report) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("Privacy & Consent Analysis Report", styles["Title"]))
    story.append(Spacer(1, 0.2 * inch))
    story.append(Paragraph(f"URL: {scan.url}", styles["Normal"]))
    story.append(Paragraph(f"Scan date: {scan.created_at}", styles["Normal"]))
    story.append(Spacer(1, 0.2 * inch))

    story.append(Paragraph(f"Privacy Score: {report.score}/100", styles["Heading2"]))
    story.append(Spacer(1, 0.1 * inch))

    story.append(Paragraph("Summary", styles["Heading2"]))
    story.append(Paragraph(report.summary or "No summary available.", styles["Normal"]))
    story.append(Spacer(1, 0.2 * inch))

    story.append(Paragraph("Flagged Clauses", styles["Heading2"]))
    clauses = report.clauses or []
    if clauses:
        table_data = [["Category", "Risk", "Detail"]]
        for c in clauses:
            table_data.append([c.get("category", ""), c.get("risk", ""), c.get("text", "")])
        table = Table(table_data, colWidths=[1.5 * inch, 0.8 * inch, 3.5 * inch])
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#333333")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ]))
        story.append(table)
    else:
        story.append(Paragraph("No risky clauses detected.", styles["Normal"]))
    story.append(Spacer(1, 0.2 * inch))

    story.append(Paragraph("Trackers & Cookies Found", styles["Heading2"]))
    trackers = report.trackers or []
    if trackers:
        for t in trackers:
            story.append(Paragraph(
                f"- {t.get('name', 'Unknown')} ({t.get('domain', '')})", styles["Normal"]
            ))
    else:
        story.append(Paragraph("No known trackers detected.", styles["Normal"]))
    story.append(Spacer(1, 0.2 * inch))

    story.append(Paragraph("Recommendations", styles["Heading2"]))
    recs = report.recommendations or []
    if recs:
        for r in recs:
            story.append(Paragraph(f"- {r}", styles["Normal"]))
    else:
        story.append(Paragraph("No recommendations available.", styles["Normal"]))

    doc.build(story)
    buffer.seek(0)
    return buffer.read()
