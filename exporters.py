from pathlib import Path
from uuid import uuid4

from fpdf import FPDF

from app.config import settings


def _local_image_path(image_url: str) -> Path:
    relative = image_url.lstrip("/")

    return settings.static_dir.parent / relative


def _safe_text(value: str) -> str:
    if not value:
        return ""

    return value.encode(
        "latin-1",
        errors="replace",
    ).decode("latin-1")


def save_pdf(
    comic: dict,
) -> str:

    filename = (
        f"comic_{uuid4().hex[:10]}.pdf"
    )

    output_path = settings.exports_dir / filename

    pdf = FPDF(
        orientation="P",
        unit="mm",
        format="A4",
    )

    pdf.set_auto_page_break(
        auto=True,
        margin=15,
    )

    title = _safe_text(
        comic.get("title", "ComicCraft")
    )

    for panel in comic.get("panels", []):

        pdf.add_page()

        pdf.set_font(
            "Helvetica",
            "B",
            20,
        )

        pdf.cell(
            0,
            12,
            title,
            ln=True,
            align="C",
        )

        pdf.set_font(
            "Helvetica",
            "B",
            13,
        )

        pdf.cell(
            0,
            10,
            f"Panel {panel.get('panel_number', '')}",
            ln=True,
        )

        image_url = panel.get("image", "")

        if image_url:

            image_path = _local_image_path(
                image_url
            )

            if image_path.exists():

                pdf.image(
                    str(image_path),
                    x=15,
                    y=40,
                    w=180,
                    h=110,
                )

        pdf.set_y(155)

        narration = _safe_text(
            panel.get("narration", "")
        )

        dialogue = _safe_text(
            panel.get("dialogue", "")
        )

        if narration:

            pdf.set_font(
                "Helvetica",
                "I",
                11,
            )

            pdf.multi_cell(
                0,
                7,
                f"Narration: {narration}",
            )

        if dialogue:

            pdf.ln(3)

            pdf.set_font(
                "Helvetica",
                "",
                11,
            )

            pdf.multi_cell(
                0,
                7,
                f"Dialogue: {dialogue}",
            )

    pdf.output(str(output_path))

    return f"/static/exports/{filename}"