import reflex as rx
import asyncio
import time
import logging
from app.services.email_service import EmailService


class ContactState(rx.State):
    name: str = ""
    email: str = ""
    message: str = ""
    website_url: str = ""
    form_loaded_at: float = 0.0
    loading: bool = False
    email_sent_modal_open: bool = False

    @rx.event
    def close_email_modal(self):
        self.email_sent_modal_open = False

    def _is_bot_detected(self) -> bool:
        if self.website_url:
            logging.warning(f"Bot detected: Honeypot filled with '{self.website_url}'")
            return True
        if self.form_loaded_at == 0:
            logging.warning(
                "Bot detected: No interaction recorded (form_loaded_at is 0)"
            )
            return True
        time_diff = time.time() - self.form_loaded_at
        if time_diff < 2.0:
            logging.warning(
                f"Bot detected: Submission too fast ({time_diff:.2f}s < 2.0s)"
            )
            return True
        return False

    @rx.event
    def set_name(self, value: str):
        self.name = value

    @rx.event
    def set_email(self, value: str):
        self.email = value

    @rx.event
    def set_message(self, value: str):
        self.message = value

    @rx.event
    def set_website_url(self, value: str):
        self.website_url = value

    @rx.event
    def ensure_form_loaded(self):
        if self.form_loaded_at == 0:
            self.form_loaded_at = time.time()
            logging.info(f"Form interaction started at {self.form_loaded_at}")

    @rx.event
    def mark_form_loaded(self, _val: str):
        """Helper to mark form as loaded on input change (accepts value argument)."""
        self.ensure_form_loaded()

    @rx.event
    async def send_message(self):
        if self._is_bot_detected():
            yield rx.toast.error(
                "Er is een fout opgetreden. Probeer het later opnieuw."
            )
            return
        self.loading = True
        yield
        subject = f"Contactformulier: Bericht van {self.name}"
        content = f'\n        <h2>Nieuw bericht via contactformulier</h2>\n        <p><strong>Naam:</strong> {self.name}</p>\n        <p><strong>E-mail:</strong> {self.email}</p>\n        <p><strong>Bericht:</strong></p>\n        <blockquote style="background: #f9f9f9; padding: 10px; border-left: 4px solid #10b981;">\n            {self.message}\n        </blockquote>\n        '
        success = EmailService.send_email(
            to_email="info@energie-insight.nl", subject=subject, content=content
        )
        self.loading = False
        if success:
            self.email_sent_modal_open = True
            self.name = ""
            self.email = ""
            self.message = ""
        else:
            yield rx.toast.error(
                "Kon bericht niet verzenden. Probeer het later opnieuw of mail ons direct."
            )