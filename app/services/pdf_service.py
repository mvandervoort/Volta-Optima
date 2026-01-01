import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import reflex as rx


class PDFService:
    @staticmethod
    def generate_report(data: dict, filename: str):
        upload_dir = rx.get_upload_dir()
        file_path = upload_dir / filename
        c = canvas.Canvas(file_path, pagesize=letter)
        c.drawString(
            100, 750, f"Energy Transition Report: {data.get('title', 'Unknown')}"
        )
        c.drawString(100, 730, "------------------------------------------------")
        y = 700
        for key, value in data.items():
            c.drawString(100, y, f"{key}: {value}")
            y -= 20
        c.save()
        return filename