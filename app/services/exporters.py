from pathlib import Path
import re

from fpdf import FPDF

from app.config import EXPORTS_DIR


def _clean_text(text: str) -> str:
    """
    Convert text to characters that FPDF can safely write.
    """
    if not text:
        return ""

    text = str(text)

    replacements = {
        "“": '"',
        "”": '"',
        "‘": "'",
        "’": "'",
        "–": "-",
        "—": "-",
        "…": "...",
        "•": "-",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    return text.encode("latin-1", "replace").decode("latin-1")


def _safe_filename(name: str) -> str:
    name = re.sub(r"[^a-zA-Z0-9_-]", "_", name)
    return name.strip("_") or "comic"


def save_pdf(layout: list[dict]) -> str:
    """
    Create a PDF from the generated comic layout.
    """

    if not layout:
        raise RuntimeError("Cannot create PDF because the comic is empty.")

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    for panel in layout:
        pdf.add_page()

        pdf.set_font("Arial", "B", 18)
        pdf.cell(
            0,
            12,
            _clean_text(
                f"Panel {panel.get('panel_number', '')}: "
                f"{panel.get('title', '')}"
            ),
            ln=True,
        )

        image_url = panel.get("image_url", "")

        if image_url.startswith("/static/"):
            relative_path = image_url.replace("/static/", "", 1)
            image_path = Path("static") / relative_path
        else:
            image_path = Path(image_url)

        if image_path.exists():
            try:
                pdf.image(
                    str(image_path),
                    x=15,
                    y=35,
                    w=180,
                )
            except Exception:
                pass

        pdf.ln(100)

        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 8, "Scene Description", ln=True)

        pdf.set_font("Arial", "", 11)
        pdf.multi_cell(
            0,
            6,
            _clean_text(panel.get("scene_description", "")),
        )

        pdf.ln(3)

        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 8, "Caption", ln=True)

        pdf.set_font("Arial", "", 11)
        pdf.multi_cell(
            0,
            6,
            _clean_text(panel.get("caption", "")),
        )

        pdf.ln(3)

        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 8, "Narration", ln=True)

        pdf.set_font("Arial", "", 11)
        pdf.multi_cell(
            0,
            6,
            _clean_text(panel.get("narration", "")),
        )

        pdf.ln(3)

        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 8, "Dialogue", ln=True)

        pdf.set_font("Arial", "", 11)
        pdf.multi_cell(
            0,
            6,
            _clean_text(panel.get("dialogue", "")),
        )

    filename = "comiccraft_comic.pdf"
    output_path = EXPORTS_DIR / filename

    pdf.output(str(output_path))

    return f"/download/{filename}"