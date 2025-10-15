"""
@file report_pdf.py
@brief Unicode-compatible PDF report generator with Cyrillic support.
"""

from typing import List, Tuple, Optional
import os
from fpdf import FPDF

class PDFReport(FPDF):
    def __init__(self, title: str = "R&D Report"):
        super().__init__(orientation="P", unit="mm", format="A4")
        self.set_auto_page_break(auto=True, margin=12)

        fonts_dir = os.path.join(os.path.dirname(__file__), "fonts")
        reg = os.path.join(fonts_dir, "DejaVuSans.ttf")
        bold = os.path.join(fonts_dir, "DejaVuSans-Bold.ttf")

        self._use_dejavu = False

        try:
            if os.path.exists(reg) and os.path.exists(bold):
                self.add_font("DejaVu", "", reg, uni=True)
                self.add_font("DejaVu", "B", bold, uni=True)
                self._use_dejavu = True
                print(f"[PDFReport] DejaVu fonts loaded successfully from {fonts_dir}")
            else:
                print(f"[PDFReport] Warning: DejaVu fonts not found in {fonts_dir}")
                print(f"[PDFReport] Regular font: {os.path.exists(reg)}")
                print(f"[PDFReport] Bold font: {os.path.exists(bold)}")
        except Exception as e:
            print(f"[PDFReport] Error loading DejaVu fonts: {e}")
            self._use_dejavu = False

        base_font = "DejaVu" if self._use_dejavu else "Helvetica"
        self.set_font(base_font, size=12)

        self.title = title
        self.add_page()

        self.set_font(base_font, "B", 16)
        self.cell(0, 10, self._safe(self.title), ln=1, align="C")
        self.ln(2)

    def _safe(self, s: str) -> str:
        """
        @brief Make text safe for PDF output.
        @param s Input string
        @return str sanitized
        """
        if s is None:
            return ""
        
        s = (s
            .replace("\u2014", "-")   # em dash - hyphen
        )
        
        return s

    def footer(self):
        self.set_y(-15)
        self.set_font("DejaVu" if self._use_dejavu else "Helvetica", "", 9)
        self.set_text_color(120, 120, 120)
        self.cell(0, 10, self._safe(f"Page {self.page_no()}"), align="C")

    def add_section(self, heading: str, body: str):
        self.add_page()
        self.set_font("DejaVu" if self._use_dejavu else "Helvetica", "B", 13)
        self.multi_cell(0, 7, self._safe(heading))
        self.ln(2)
        self.set_font("DejaVu" if self._use_dejavu else "Helvetica", "", 11)
        for para in (body or "").split("\n\n"):
            self.multi_cell(0, 6, self._safe(para))
            self.ln(2)

    def add_image_page(self, title: str, img_path: str, width_mm: Optional[float] = 180.0):
        if not os.path.exists(img_path):
            return
        self.add_page()
        self.set_font("DejaVu" if self._use_dejavu else "Helvetica", "B", 12)
        self.multi_cell(0, 7, self._safe(title))
        self.ln(2)
        self.image(img_path, x=None, y=None, w=width_mm)

    def add_image_grid(self, title: str, images: List[Tuple[str, str]], cols: int = 2, cell_w: float = 90.0):
        if not images:
            return
        self.add_page()
        self.set_font("DejaVu" if self._use_dejavu else "Helvetica", "B", 12)
        self.multi_cell(0, 7, self._safe(title))
        self.ln(2)

        x0, y = self.get_x(), self.get_y()
        col = 0
        for subtitle, path in images:
            if not os.path.exists(path):
                continue
            x = 10 + col * (cell_w)
            self.set_xy(x, y)
            self.image(path, x=x, y=self.get_y(), w=cell_w - 10)
            self.ln(cell_w * 0.55)
            self.set_x(x)
            self.set_font("DejaVu" if self._use_dejavu else "Helvetica", "", 9)
            self.multi_cell(cell_w - 10, 5, self._safe(subtitle), align="C")
            col += 1
            if col >= cols:
                col = 0
                y = self.get_y() + 6
        self.set_y(self.get_y() + 4)
